from django.db.models import (
    Sum,
    ExpressionWrapper,
    F,
    IntegerField,
    Q,
    Value,
    Expression,
)
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
    Provider,
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


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ("ruc", "name")


class ReceiptSerializer(serializers.ModelSerializer):
    receipt_type = ReceiptTypeSerializer(read_only=True)
    items = ReceiptItemSerializer(many=True, read_only=True)
    total = serializers.IntegerField(read_only=True)
    provider = ProviderSerializer(read_only=True)

    class Meta:
        model = Receipt
        fields = (
            "id",
            "report_id",
            "receipt_type",
            "receipt_date",
            "receipt_number",
            "provider",
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
        year = self.context.get("year")
        if not obj.children.exists():
            return None
        if not obj.parent:
            qs = obj.children.filter(
                children__receipt_items__receipt__institution=self.context[
                    "institution"
                ]
            )
            if year:
                qs = qs.filter(children__receipt_items__receipt__date__year=year)
        else:
            qs = obj.children.filter(
                receipt_items__receipt__institution=self.context["institution"]
            )
            if year:
                qs = qs.filter(receipt_items__receipt__date__year=year)
        return AccountObjectChartSerializer(
            instance=qs.distinct(), many=True, context=self.context
        ).data

    def get_total_expenditure(self, obj):
        if not obj.children.exists():
            qs = ReceiptItem.objects.filter(
                object_of_expenditure=obj,
                receipt__institution=self.context["institution"],
            ).distinct()
            if self.context.get("year"):
                qs = qs.filter(receipt__receipt__date__year=self.context.get("year"))
            qs = qs.annotate(
                subtotal=ExpressionWrapper(
                    F("unit_price") * F("quantity"),
                    output_field=IntegerField(),
                )
            )
            total = qs.aggregate(total=Sum("subtotal"))["total"]
            return total
        return None
