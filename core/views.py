from django.db.models import Count, Sum
from rest_framework import viewsets
from django_filters import rest_framework as filters

from core.models import Institution, Department, District
from core.serializers import (
    InstitutionSerializer,
    DepartmentSerializer,
    DistrictSerializer,
)


class InstitutionFilter(filters.FilterSet):
    district = filters.NumberFilter(field_name="establishment__locality__district_id")
    department = filters.NumberFilter(
        field_name="establishment__locality__district__department_id"
    )
    id = filters.NumberFilter(field_name="id")


class InstitutionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    filterset_class = InstitutionFilter
    search_fields = ("name",)

    def get_queryset(self):
        return Institution.objects.annotate(
            disbursement_qty=Count("disbursements")
        ).filter(disbursement_qty__gt=0)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {**response.data, "summary": self.get_totals()}
        return response

    def get_totals(self):
        qs = self.filter_queryset(self.get_queryset())
        return qs.aggregate(
            total_disbursed=Sum("disbursements__amount_disbursed"),
            total_reported=Sum("disbursements__reports__receipts__total"),
        )


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    filterset_fields = ("department",)
    search_fields = ("name",)
