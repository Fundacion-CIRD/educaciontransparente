from rest_framework import serializers

from accountability.models import (
    Report,
    Disbursement,
    Resolution,
    Receipt,
    ReceiptType,
    ReportStatus,
)


class ResolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resolution
        fields = ("document_number", "document_year")


class DisbursementSerializer(serializers.ModelSerializer):
    resolution = ResolutionSerializer()
    institution_id = serializers.PrimaryKeyRelatedField(read_only=True)
    institution_name = serializers.CharField(source="institution.name", read_only=True)

    class Meta:
        model = Disbursement
        fields = (
            "id",
            "resolution",
            "disbursement_date",
            "amount_disbursed",
            "funds_origin",
            "origin_details",
            "due_date",
            "principal_name",
            "principal_issued_id",
            "payment_type",
            "institution_id",
            "institution_name",
        )


class ReportStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportStatus
        fields = ("value",)


class ReportSerializer(serializers.ModelSerializer):
    disbursement = DisbursementSerializer()
    status = ReportStatusSerializer()

    class Meta:
        model = Report
        fields = ("id", "updated_at", "disbursement", "status", "delivered_via")


class ReceiptTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptType
        fields = ("name",)


class ReceiptSerializer(serializers.ModelSerializer):
    receipt_type = ReceiptTypeSerializer(read_only=True)

    class Meta:
        model = Receipt
        fields = (
            "id",
            "report_id",
            "receipt_type",
            "receipt_date",
            "receipt_number",
            "object_of_expenditure",
            "description",
            "total",
        )
