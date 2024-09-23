import io
import logging
import re
from datetime import datetime
from typing import IO

from dateutil.relativedelta import relativedelta
from openpyxl import load_workbook

from accountability.models import (
    Resolution,
    Disbursement,
    Report,
    DisbursementOrigin,
    OriginDetail,
    PaymentType,
    ReceiptType,
    AccountObject,
    Receipt,
    ReceiptItem,
)
from core.models import Institution

logger = logging.getLogger(__name__)


class ExcelProcessor:
    class ProcessingError(Exception):
        def __init__(self, message):
            self.message = f"Error processing file: {message}"

    def __init__(self, file: IO, sheet_name="General"):
        _file = io.BytesIO(file.read())
        self.workbook = load_workbook(filename=_file, data_only=True)
        self.sheet = self.workbook[sheet_name]
        dimensions = self.sheet.dimensions
        _, last_cell = dimensions.split(":")
        self.last_row = int(re.search(r"\d+", last_cell).group())
        self.institution = None
        self.resolution = None
        self.disbursement = None
        self.report = None
        self.receipt = None
        self.funds_origin = None
        self.origin_details = None
        self.report_status = None
        self.disbursement_date = None
        self.payment_type = None

    def process(self):
        empty_row_count = 0
        all_rows = [row for row in self.sheet.rows]
        for idx, row in enumerate(all_rows[3:485]):
            logger.info(f"Processing row {idx + 1}")
            if all(cell is None for cell in row):
                empty_row_count += 1
                if empty_row_count >= 2:
                    break
            empty_row_count = 0
            try:
                self.get_or_create_report(row)
            except Exception as e:
                logger.info(f"Error in line {idx + 1}: {e}", exc_info=True)

    def get_institution(self, row):
        code = row[1].value
        establishment_code = row[0].value
        name = row[3].value.strip()
        if not code or not establishment_code:
            return self.institution
        if self.institution and (
            self.institution.code == code
            and self.institution.establishment.code == establishment_code
        ):
            return self.institution
        try:
            self.institution = Institution.objects.get(
                code=code, establishment__code=establishment_code, name=name
            )
            return self.institution
        except Institution.DoesNotExist:
            logger.info(
                f"Institution with code {row[1].value}, establishment code {row[0].value} does not exist."
            )
            return None
        except Institution.MultipleObjectsReturned:
            try:
                self.institution = Institution.objects.get(
                    code=code, establishment__code=establishment_code, name=row[3].value
                )
            except Institution.DoesNotExist:
                pass
            logger.info(
                f"Institution with name={name}, code {row[1].value}, establishment code {row[0].value} does not exist"
            )
            return None

    def _determine_payment_type(self, payment_type_str: str):
        if not payment_type_str:
            return self.payment_type
        normalized = (payment_type_str or "").lower()
        if "ch" in normalized:
            return PaymentType.objects.get_or_create(name="Cheque")[0]
        if any(keyword in normalized for keyword in ["transf", "cta", "cuenta", "red"]):
            return PaymentType.objects.get_or_create(name="Transferencia bancaria")[0]
        self.payment_type, _ = PaymentType.objects.get_or_create(name="Otro")
        return self.payment_type

    def _get_disbursement_date(self, row):
        value = row[14].value
        if not isinstance(value, datetime):
            return None
        disbursement_date = value.date() if row[14].value else None
        # return previous value when no date is found
        if not disbursement_date:
            return self.disbursement_date
        self.disbursement_date = disbursement_date
        return disbursement_date

    def _get_disbursement_data(self, row) -> dict | None:
        funds_origin = row[11].value
        origin_details = row[12].value
        if funds_origin:
            self.funds_origin, _ = DisbursementOrigin.objects.get_or_create(
                code=funds_origin,
            )
        if origin_details:
            self.origin_details, _ = OriginDetail.objects.get_or_create(
                name=origin_details.strip()
            )
        data = {
            "resolution_amount": row[9].value,
            "amount_disbursed": row[15].value,
            "principal_name": row[6].value or "",
            "principal_issued_id": row[7].value or "",
            "funds_origin": self.funds_origin,
            "origin_details": self.origin_details,
            "payment_type": self._determine_payment_type(row[13].value),
        }
        return data

    def get_or_create_disbursement(self, row) -> Disbursement | None:
        institution = self.get_institution(row)
        if not institution:
            return None
        resolution_no = row[8].value
        resolution_year = row[10].value
        if (
            self.resolution
            and self.resolution.document_number == resolution_no
            and self.resolution.document_year == resolution_year
        ):
            resolution = self.resolution
        else:
            self.resolution, _ = Resolution.objects.get_or_create(
                document_year=resolution_year,
                document_number=resolution_no,
            )
            resolution = self.resolution
        data = self._get_disbursement_data(row)
        if not data:
            return self.disbursement
        disbursement_date = self._get_disbursement_date(row)
        data["due_date"] = (
            disbursement_date + relativedelta(months=6, days=15)
            if disbursement_date
            else None
        )
        self.disbursement, _ = Disbursement.objects.get_or_create(
            institution=institution,
            resolution=resolution,
            disbursement_date=disbursement_date,
            defaults=data,
        )
        return self.disbursement

    @staticmethod
    def _get_balance_and_status(row) -> tuple[int, str]:
        disbursed_amount = row[15].value
        reported_amount = row[17].value
        if disbursed_amount and reported_amount:
            balance = disbursed_amount - reported_amount
        else:
            balance = row[18].value
        return balance, (
            Report.ReportStatus.finished.value
            if balance <= 0
            else Report.ReportStatus.pending.value
        )

    def get_or_create_report(self, row) -> Report | None:
        disbursement = self.get_or_create_disbursement(row)
        if not disbursement:
            return self.report
        report_date = (
            row[16].value.date() if isinstance(row[16].value, datetime) else None
        )
        if not report_date:
            return self.report
        delivered_via = (row[20].value or "").strip()
        comments = (row[21].value or "").strip()
        # reported_amount = row[17].value
        _, status = self._get_balance_and_status(row)
        self.report, _ = Report.objects.get_or_create(
            disbursement=disbursement,
            defaults={
                "status": status,
                "delivered_via": delivered_via,
                "comments": comments,
                "report_date": report_date,
            },
        )
        return self.report

    @staticmethod
    def _get_receipt_type(row) -> ReceiptType | None:
        receipt_type_str = row[22].value.strip().title() if row[22].value else None
        if not receipt_type_str:
            return None
        receipt_type, _ = ReceiptType.objects.get_or_create(
            name=receipt_type_str,
        )
        return receipt_type

    @staticmethod
    def _get_object_of_expenditure(row) -> AccountObject | None:
        obj_no = row[24].value
        try:
            obj_no = int(obj_no)
        except ValueError:
            return None
        try:
            return AccountObject.objects.get(key=obj_no)
        except AccountObject.DoesNotExist:
            return None

    @staticmethod
    def _parse_unit_price(unit_price_str):
        digits = "".join(num for num in re.findall(r"\d+", unit_price_str))
        return int(digits) if digits else 0

    def process_receipt(self, row):
        report = self.get_or_create_report(row)
        receipt_number = (str(row[23].value) or "").strip()
        if receipt_number.lower() == "rendido sin movimiento":
            return
        receipt_type = self._get_receipt_type(row)
        if not receipt_type:
            return
        receipt_number = (str(row[23].value) or "").strip()
        object_of_expenditure = self._get_object_of_expenditure(row)
        description = (row[25].value or "").strip()
        receipt_date = (
            row[26].value.date() if isinstance(row[26].value, datetime) else None
        )
        unit_price = row[27].value
        if not unit_price:
            return
        if isinstance(unit_price, str):
            unit_price = self._parse_unit_price(unit_price)
        receipt, _ = Receipt.objects.get_or_create(
            report=report,
            receipt_number=receipt_number,
            receipt_date=receipt_date,
            receipt_type=receipt_type,
        )
        ReceiptItem.objects.create(
            receipt=receipt,
            object_of_expenditure=object_of_expenditure,
            description=description or "No disponible",
            unit_price=unit_price,
            quantity=1,
        )
