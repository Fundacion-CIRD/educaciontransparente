from django_filters import rest_framework as filters

from accountability.models import (
    Resolution,
    DisbursementOrigin,
    Disbursement,
    Report,
    ReceiptType,
    Receipt,
    ReceiptItem,
)
from core.models import Institution

INSTITUTION = "Institución"


class DisbursementFilter(filters.FilterSet):
    institution = filters.ModelChoiceFilter(
        queryset=Institution.objects.filter(reports__isnull=False).distinct(),
        label=INSTITUTION,
    )
    resolution = filters.ModelChoiceFilter(
        queryset=Resolution.objects.all(), label="Resolución"
    )
    funds_origin = filters.ModelChoiceFilter(
        queryset=DisbursementOrigin.objects.all(), label="Origen del fondo"
    )
    disbursement_date = filters.DateFromToRangeFilter(field_name="disbursement_date")


class ReportFilter(filters.FilterSet):
    institution = filters.ModelChoiceFilter(
        queryset=Institution.objects.filter(reports__isnull=False).distinct(),
        label=INSTITUTION,
    )

    year = filters.NumberFilter(
        field_name="disbursement__resolution__document_year", label="Año"
    )
    disbursement = filters.ModelChoiceFilter(
        queryset=Disbursement.objects.all(),
    )
    report_date = filters.DateFromToRangeFilter(field_name="report_date")

    class Meta:
        model = Report
        fields = ["institution"]


class ReceiptFilter(filters.FilterSet):
    institution = filters.ModelChoiceFilter(
        queryset=Institution.objects.filter(reports__isnull=False).distinct(),
        label=INSTITUTION,
    )
    disbursement = filters.ModelChoiceFilter(
        queryset=Disbursement.objects.all(),
    )
    report = filters.ModelChoiceFilter(
        queryset=Report.objects.all(),
    )
    receipt_type = filters.ModelChoiceFilter(
        queryset=ReceiptType.objects.all(),
    )
    receipt_date = filters.DateFromToRangeFilter(field_name="receipt_date")

    class Meta:
        model = Receipt
        fields = ["institution", "disbursement", "report", "receipt_date"]


class ReceiptItemFilter(filters.FilterSet):
    class Meta:
        model = ReceiptItem
        fields = ["object_of_expenditure", "receipt"]
