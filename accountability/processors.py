import io
import logging
import re
from typing import IO

from django.template.defaultfilters import slugify
from openpyxl import load_workbook

from accountability.models import Resolution, Disbursement, Report, ReportStatus
from core.models import Institution

logger = logging.getLogger(__name__)


class AccountabilityProcessor:
    class ProcessingError(Exception):
        def __init__(self, message):
            self.message = f"Error processing file: {message}"

    def __init__(self, file: IO):
        _file = io.BytesIO(file.read())
        self.workbook = load_workbook(filename=_file, data_only=True)
        self.sheet = self.workbook["General"]
        dimensions = self.sheet.dimensions
        _, last_cell = dimensions.split(":")
        self.last_row = int(re.search(r"\d+", last_cell).group())
        self.last_institution = None
        self.last_resolution = None
        self.last_disbursement = None
        self.report = None
        self.last_voucher = None
        self.current_row = None

    def process(self):
        rows = self.sheet[4 : self.last_row]
        for row in rows:
            self.current_row = tuple(row)
            institution = self.get_institution()

    def get_institution(self):
        institution_id = self.current_row[1]
        if self.last_institution and self.last_institution.code == institution_id:
            return self.last_institution
        elif not institution_id:
            return self.last_institution
        try:
            self.last_institution = Institution.objects.get(code=institution_id)
            return self.last_institution
        except Institution.DoesNotExist as exc:
            logger.info(f"Institution with code {institution_id} does not exist.")
            raise AccountabilityProcessor.ProcessingError(exc)
        except Institution.MultipleObjectsReturned as exc:
            logger.info(f"Institution with code {institution_id} has multiple entries.")
            raise AccountabilityProcessor.ProcessingError(exc)

    def get_resolution(self):
        year, number = self.current_row[10], self.current_row[8]
        try:
            self.last_resolution, _ = Resolution.objects.get_or_create(
                document_year=year, document_no=number
            )
        except Resolution.MultipleObjectsReturned as exc:
            logger.info(f"Resolution {number}/{year} has multiple entries.")
            raise AccountabilityProcessor.ProcessingError(exc)

    def get_disbursement(self):
        institution = self.get_institution()
        resolution = self.get_resolution()
        funds_origin = self.current_row[11]
        origin_details = self.current_row[12]
        payment_type = self.current_row[13]
        payment_date = self.current_row[14]
        amount_disbursed = self.current_row[15]
        principal_name = self.current_row[6]
        principal_issued_id = self.current_row[7]
        self.last_disbursement, _ = Disbursement.objects.get_or_create(
            resolution=resolution,
            institution=institution,
            funds_origin=funds_origin,
            origin_details=origin_details,
            payment_type=payment_type,
            payment_date=payment_date,
            amount_disbursed=amount_disbursed,
            principal_name=principal_name,
            principal_issued_id=principal_issued_id,
        )
        return self.last_disbursement

    def get_report(self):
        updated_at = self.current_row[16]
        status = self.current_row[19]
        status_code = slugify(status)
        status, _ = ReportStatus.objects.get_or_create
        delivered_via = self.current_row[20]
        comments = self.current_row[21]

        disbursement = self.get_disbursement()
        self.report, _ = Report.objects.get_or_create(
            disbursement=disbursement,
            updated_at=updated_at,
            status=status,
            delivered_via=delivered_via,
        )
        return self.report
