from django_filters import rest_framework as filters


class InstitutionFilter(filters.FilterSet):
    district = filters.NumberFilter(field_name="establishment__locality__district_id")
    department = filters.NumberFilter(
        field_name="establishment__locality__district__department_id"
    )
    id = filters.NumberFilter(field_name="id")
    institution_type = filters.CharFilter()
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
