from django.db.models import Sum
from rest_framework import viewsets

from accountability.models import Receipt, Disbursement
from core.filters import InstitutionFilter
from core.models import Institution, Department, District
from core.serializers import (
    InstitutionSerializer,
    DepartmentSerializer,
    DistrictSerializer,
)


class InstitutionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Institution.objects.filter(disbursements__isnull=False).distinct()
    serializer_class = InstitutionSerializer
    filterset_class = InstitutionFilter
    search_fields = ("name",)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {**response.data, "summary": self.get_totals()}
        return response

    def get_totals(self):
        qs = self.filter_queryset(self.get_queryset())
        receipts = Receipt.objects.filter(institution__in=qs).distinct()
        disbursements = Disbursement.objects.filter(institution__in=qs).distinct()
        total_reported = receipts.aggregate(total_reported=Sum("receipt_total"))[
            "total_reported"
        ]
        total_disbursed = disbursements.aggregate(
            total_disbursed=Sum("amount_disbursed")
        )["total_disbursed"]
        return {
            "disbursed": total_disbursed,
            "reported": total_reported,
        }


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = District.objects.filter(
        establishments__institutions__disbursements__isnull=False
    ).distinct()
    serializer_class = DistrictSerializer
    filterset_fields = ("department",)
    search_fields = ("name",)
