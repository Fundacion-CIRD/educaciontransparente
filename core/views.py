from django.db.models import Count, Sum, ExpressionWrapper, F, IntegerField, Value
from django.db.models.functions import Coalesce
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
        qs = qs.annotate(
            total_reported=Coalesce(
                Sum(
                    ExpressionWrapper(
                        F("disbursements__reports__receipts__items__unit_price")
                        * F("disbursements__reports__receipts__items__quantity"),
                        output_field=IntegerField(),
                    )
                ),
                Value(0, output_field=IntegerField()),
            )
        )
        return qs.aggregate(
            disbursed=Sum("disbursements__amount_disbursed"),
            reported=Sum("total_reported"),
        )


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
