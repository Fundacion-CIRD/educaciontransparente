from django.db.models import Sum, ExpressionWrapper, F, Value
from django.db.models.functions import Coalesce
from django.db.models import IntegerField

from rest_framework import viewsets
from rest_framework.response import Response

from accountability.filters import (
    DisbursementFilter,
    ReportFilter,
    ReceiptFilter,
    ReceiptItemFilter,
)
from accountability.models import (
    Report,
    Disbursement,
    Receipt,
    ReceiptItem,
    AccountObject,
    Resolution,
)
from accountability.serializers import (
    ReportSerializer,
    DisbursementSerializer,
    ReceiptSerializer,
    AccountObjectChartSerializer,
    ReceiptItemSerializer,
    ResolutionSerializer,
)
from core.models import Institution


class ResolutionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Resolution.objects.order_by("document_year", "document_number")
    serializer_class = ResolutionSerializer
    search_fields = ["full_document_number"]


class DisbursementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Disbursement.objects.all().order_by(
        "-resolution__document_year", "-disbursement_date"
    )
    serializer_class = DisbursementSerializer
    filterset_class = DisbursementFilter

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["disbursement"] = True
        return context

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        total_disbursed = qs.distinct().aggregate(total=Sum("amount_disbursed"))[
            "total"
        ]
        reports = Report.objects.filter(disbursement__in=qs).distinct()
        receipts = Receipt.objects.filter(report__in=reports).distinct()
        total_reported = receipts.aggregate(reported=Sum("receipt_total"))["reported"]
        response_data = super().list(request, *args, **kwargs).data
        response_data["summary"] = {
            "total_disbursed": total_disbursed,
            "total_reported": total_reported,
        }
        return Response(data=response_data)


class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Report.objects.all().order_by(
        "-disbursement__resolution__document_year", "-disbursement__disbursement_date"
    )
    serializer_class = ReportSerializer
    filterset_class = ReportFilter


class ReceiptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    filterset_class = ReceiptFilter


class ReceiptItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReceiptItem.objects.all()
    serializer_class = ReceiptItemSerializer
    filterset_class = ReceiptItemFilter


class AccountObjectChartViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AccountObject.objects.all()
    serializer_class = AccountObjectChartSerializer

    def _get_institution(self):
        institution_id = self.request.GET.get("institution")
        try:
            institution_id = int(institution_id)
        except (ValueError, TypeError):
            return None
        try:
            return Institution.objects.get(pk=institution_id)
        except Institution.DoesNotExist:
            return None

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["year"] = self._get_year()
        context["institution"] = self._get_institution()
        return context

    def _get_year(self):
        year = self.request.GET.get("year", None)
        try:
            return int(year)
        except (ValueError, TypeError):
            return None

    def get_queryset(self):
        institution = self._get_institution()
        year = self._get_year()
        if not institution or ("year" in self.request.GET.keys() and not year):
            return AccountObject.objects.none()
        leaf_qs = AccountObject.objects.filter(
            receipt_items__receipt__institution=institution
        )
        if year:
            leaf_qs = leaf_qs.filter(receipt_items__receipt__receipt_date__year=year)
        second_level_qs = AccountObject.objects.filter(
            children__in=leaf_qs.distinct()
        ).distinct()
        top_level_qs = AccountObject.objects.filter(
            children__in=second_level_qs
        ).distinct()
        return top_level_qs
