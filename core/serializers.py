from rest_framework import serializers

from core.models import Department, District, Locality, Establishment, Institution


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ("id", "code", "name")


class DistrictSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = District
        fields = ("id", "department", "code", "name")


class LocalitySerializer(serializers.ModelSerializer):
    district = DistrictSerializer(read_only=True)

    class Meta:
        model = Locality
        fields = ("id", "district", "code", "name")


class EstablishmentSerializer(serializers.ModelSerializer):
    locality = LocalitySerializer(read_only=True)

    class Meta:
        model = Establishment
        fields = (
            "id",
            "code",
            "locality",
            "zone_code",
            "zone_name",
            "address",
            "latitude",
            "longitude",
        )


class InstitutionSerializer(serializers.ModelSerializer):
    establishment = EstablishmentSerializer(read_only=True)

    class Meta:
        model = Institution
        fields = (
            "id",
            "code",
            "name",
            "institution_type",
            "phone_number",
            "website",
            "email",
            "establishment",
        )
