from django.db.models import (
    Sum,
    ExpressionWrapper,
    F,
    IntegerField,
)
from rest_framework import serializers

from accountability.models import (
    DisbursementOrigin,
    Report,
    Disbursement,
    Resolution,
    Receipt,
    ReceiptType,
    ReceiptItem,
    AccountObject,
    Provider,
    OriginDetail,
    PaymentType,
)
from core.serializers import InstitutionSerializer


class ResolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resolution
        fields = (
            "id",
            "document_number",
            "document_year",
            "document",
            "full_document_number",
        )


class DisbursementOriginSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisbursementOrigin
        fields = ("code",)


class OriginDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginDetail
        fields = ("name",)


class PaymentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentType
        fields = ("name",)


class DisbursementSerializer(serializers.ModelSerializer):
    resolution = ResolutionSerializer()
    funds_origin = DisbursementOriginSerializer(read_only=True)
    origin_details = OriginDetailSerializer(read_only=True)
    payment_type = PaymentTypeSerializer(read_only=True)
    institution_id = serializers.PrimaryKeyRelatedField(read_only=True)
    institution_name = serializers.CharField(source="institution.name", read_only=True)

    class Meta:
        model = Disbursement
        fields = (
            "id",
            "resolution",
            "resolution_amount",
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
            "comments",
        )


class ReportSerializer(serializers.ModelSerializer):
    reported_amount = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    disbursement = DisbursementSerializer(read_only=True)

    class Meta:
        model = Report
        fields = (
            "id",
            "updated_at",
            "institution_id",
            "disbursement",
            "status",
            "report_date",
            "reported_amount",
            "balance",
            "delivered_via",
            "comments",
            "institution_id",
        )

    @staticmethod
    def get_reported_amount(obj):
        return obj.receipts.aggregate(
            total=Sum("receipt_total", output_field=IntegerField())
        )["total"]

    def get_balance(self, obj):
        reported = self.get_reported_amount(obj)
        disbursed = obj.disbursement.amount_disbursed
        if not disbursed or not reported:
            return None
        return disbursed - reported


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
            "receipt_id",
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
    provider = ProviderSerializer(read_only=True)
    receipt_total = serializers.SerializerMethodField()
    institution = InstitutionSerializer(read_only=True)

    class Meta:
        model = Receipt
        fields = (
            "id",
            "report_id",
            "receipt_type",
            "receipt_date",
            "receipt_number",
            "provider",
            "institution",
            "disbursement_id",
            "receipt_total",
            "items",
        )

    def get_receipt_total(self, obj):
        return obj.receipt_total


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
                qs = qs.filter(
                    children__receipt_items__receipt__receipt_date__year=year
                )
        else:
            qs = obj.children.filter(
                receipt_items__receipt__institution=self.context["institution"]
            )
            if year:
                qs = qs.filter(receipt_items__receipt__receipt_date__year=year)
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
                qs = qs.filter(receipt__receipt_date__year=self.context.get("year"))
            qs = qs.annotate(
                subtotal=ExpressionWrapper(
                    F("unit_price") * F("quantity"),
                    output_field=IntegerField(),
                )
            )
            total = qs.aggregate(total=Sum("subtotal"))["total"]
            return total
        return None
