from django_filters import rest_framework as filters

from rest_framework import viewsets

from accountability.models import (
    Report,
    Disbursement,
    Receipt,
    ReceiptItem,
    AccountObject,
)
from accountability.serializers import (
    ReportSerializer,
    DisbursementSerializer,
    ReceiptSerializer,
    AccountObjectChartSerializer,
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


class AccountObjectChartViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AccountObject.objects.all()
    serializer_class = AccountObjectChartSerializer

    def get_queryset(self):
        institution_id = self.request.GET.get("institution")
        if not institution_id:
            return AccountObject.objects.none()
        leaf_qs = AccountObject.objects.filter(
            receipt_items__receipt__report__disbursement__institution_id=institution_id
        ).distinct()
        second_level_qs = AccountObject.objects.filter(children__in=leaf_qs).distinct()
        top_level_qs = AccountObject.objects.filter(
            children__in=second_level_qs
        ).distinct()
        return top_level_qs
