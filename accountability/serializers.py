from django.db.models import Sum, ExpressionWrapper, F, IntegerField, Q, Value
from django.db.models.functions import Coalesce
from rest_framework import serializers

from accountability.models import (
    Report,
    Disbursement,
    Resolution,
    Receipt,
    ReceiptType,
    ReceiptItem,
    AccountObject,
)


class ResolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resolution
        fields = ("document_number", "document_year", "document")


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


class ReportSerializer(serializers.ModelSerializer):
    disbursement = DisbursementSerializer()

    class Meta:
        model = Report
        fields = ("id", "updated_at", "disbursement", "status", "delivered_via")


class ReceiptTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptType
        fields = ("name",)


class AccountObjectSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()

    class Meta:
        model = AccountObject
        fields = ("key", "value", "parent")

    def get_parent(self, obj):
        if obj.parent:
            return AccountObjectSerializer(instance=obj.parent).data


class ReceiptItemSerializer(serializers.ModelSerializer):
    object_of_expenditure = AccountObjectSerializer(read_only=True)

    class Meta:
        model = ReceiptItem
        fields = (
            "id",
            "quantity",
            "description",
            "unit_price",
            "object_of_expenditure",
        )


class ReceiptSerializer(serializers.ModelSerializer):
    receipt_type = ReceiptTypeSerializer(read_only=True)
    items = ReceiptItemSerializer(many=True, read_only=True)
    total = serializers.IntegerField(read_only=True)

    class Meta:
        model = Receipt
        fields = (
            "id",
            "report_id",
            "receipt_type",
            "receipt_date",
            "receipt_number",
            "total",
            "items",
        )


class AccountObjectChartSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    total_expenditure = serializers.SerializerMethodField()

    class Meta:
        model = AccountObject
        fields = ["key", "value", "children", "total_expenditure"]

    def get_children(self, obj):
        if obj.children.exists():
            qs = obj.children.filter(receipt_items__isnull=False).distinct()
            if qs.exists():
                return AccountObjectChartSerializer(instance=qs, many=True).data
        return None

    def get_total_expenditure(self, obj):
        if not obj.children.exists():
            agg_func = Coalesce(
                Sum(
                    ExpressionWrapper(
                        F("unit_price") * F("quantity"),
                        output_field=IntegerField(),
                    ),
                    distinct=True,
                ),
                Value(0, output_field=IntegerField()),
            )
            total_expenditure = ReceiptItem.objects.filter(
                object_of_expenditure=obj
            ).aggregate(total=agg_func)["total"]
            if total_expenditure:
                return total_expenditure
        return None
