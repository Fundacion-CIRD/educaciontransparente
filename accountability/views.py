from django_filters import rest_framework as filters

from rest_framework import viewsets

from accountability.models import Report, Disbursement, Receipt
from accountability.serializers import (
    ReportSerializer,
    DisbursementSerializer,
    ReceiptSerializer,
)
from core.models import Institution


class ReportFilter(filters.FilterSet):
    institution = filters.ModelChoiceFilter(
        field_name="disbursement__institution_id", queryset=Institution.objects.all()
    )
    year = filters.NumberFilter(
        field_name="disbursement__disbursement_date__year",
    )

    class Meta:
        model = Report
        fields = ["institution"]


class DisbursementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Disbursement.objects.all()
    serializer_class = DisbursementSerializer


class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    filterset_class = ReportFilter


class ReceiptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
