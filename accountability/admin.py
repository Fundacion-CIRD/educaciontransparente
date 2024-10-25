from django.contrib.admin import (
    register,
    display,
    RelatedFieldListFilter,
)
from django.core.exceptions import ValidationError
from django.core.validators import EMPTY_VALUES
from django.db.models import Sum, ExpressionWrapper, F, IntegerField, QuerySet
from django.http import HttpRequest
from django.utils.numberformat import format as format_number
from unfold import admin
from unfold.admin import ModelAdmin, StackedInline
from unfold.contrib.filters.admin import RangeDateFilter as BaseRangeDateFilter
from unfold.typing import FieldsetsType

from accountability.models import (
    Disbursement,
    Report,
    ReceiptType,
    Receipt,
    Resolution,
    AccountObject,
    ReceiptItem,
    OriginDetail,
    PaymentType,
    Provider,
    DisbursementOrigin,
)
from core.admin import DocumentInline


class RangeDateFilter(BaseRangeDateFilter):
    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        filters = {}
        value_from = self.used_parameters.get(self.field_path + "_from", None)
        if value_from not in EMPTY_VALUES:
            d, m, y = value_from.split("/")
            filters.update({self.parameter_name + "__gte": f"{y}-{m}-{d}"})
        value_to = self.used_parameters.get(self.field_path + "_to", None)
        if value_to not in EMPTY_VALUES:
            d, m, y = value_to.split("/")
            filters.update({self.parameter_name + "__lte": f"{y}-{m}-{d}"})
        try:
            return queryset.filter(**filters)
        except (ValueError, ValidationError):
            return None


@register(Resolution)
class ResolutionAdmin(ModelAdmin):
    list_display = ("document_number", "document_year")
    list_filter = ("document_year",)
    search_fields = ("document_number",)
    fieldsets = [
        (None, {"fields": ["document_number", "document_year", "document"]}),
    ]
    compressed_fields = True


@register(Disbursement)
class DisbursementAdmin(ModelAdmin):
    list_display = (
        "institution",
        "resolution",
        "get_amount_disbursed",
        "disbursement_date",
        "due_date",
    )
    list_filter = (
        ("disbursement_date", RangeDateFilter),
        ("due_date", RangeDateFilter),
    )
    list_filter_submit = True
    search_fields = (
        "institution__name",
        "resolution__full_document_number",
        "resolution_amount",
        "amount_disbursed",
    )
    autocomplete_fields = ("institution", "resolution", "origin_details")
    inlines = [DocumentInline]
    readonly_fields = ("due_date",)

    def get_fieldsets(self, request: HttpRequest, obj=None) -> FieldsetsType:
        fieldsets = [
            (
                "Institución",
                {"fields": ["institution", ("principal_name", "principal_issued_id")]},
            ),
            (
                "Desembolso",
                {
                    "fields": [
                        "resolution",
                        "resolution_amount",
                        ("disbursement_date", "due_date"),
                        "amount_disbursed",
                        "funds_origin",
                        "origin_details",
                        "payment_type",
                    ]
                },
            ),
        ]
        if request.user.is_superuser:
            fieldsets[1][1]["fields"] += [
                "is_historical",
            ]
        return fieldsets

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Disbursement.objects.all()
        return Disbursement.objects.filter(institution__users=request.user).distinct()

    @display(description="Monto desembolsado", ordering="amount_disbursed")
    def get_amount_disbursed(self, obj):
        try:
            return format_number(obj.amount_disbursed, ",", thousand_sep=".")
        except:
            return obj.amount_disbursed


@register(Report)
class ReportAdmin(ModelAdmin):
    list_display = (
        "disbursement",
        "status",
        "delivered_via",
        "report_date",
        "updated_at",
    )
    list_filter = (
        "status",
        ("report_date", RangeDateFilter),
        ("disbursement__disbursement_date", RangeDateFilter),
        ("updated_at", RangeDateFilter),
    )
    list_filter_submit = True
    autocomplete_fields = ("disbursement",)
    inlines = [DocumentInline]
    search_fields = (
        "disbursement__institution__name",
        "disbursement__resolution__full_document_number",
    )
    readonly_fields = ("status", "get_report_total")

    @admin.display(description="Total reportado")
    def get_report_total(self, obj):
        return obj.reported_total


@register(ReceiptType)
class ReceiptTypeAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class ReceiptItemInline(StackedInline):
    model = ReceiptItem
    fields = (
        "object_of_expenditure",
        (
            "quantity",
            "description",
            "unit_price",
        ),
    )
    autocomplete_fields = ("object_of_expenditure",)
    min_num = 1
    extra = 0


@register(Provider)
class ProviderAdmin(ModelAdmin):
    list_display = ("name", "ruc")
    search_fields = ("name", "ruc")


@register(Receipt)
class ReceiptAdmin(ModelAdmin):
    ordering = ("-receipt_date",)
    list_display = (
        "receipt_type",
        "receipt_date",
        "receipt_number",
        "get_total",
        "report",
    )
    inlines = [ReceiptItemInline]
    search_fields = (
        "report__disbursement__institution__name",
        "receipt_number",
        "receipt_total",
    )
    list_filter = [("receipt_date", RangeDateFilter)]
    list_filter_submit = True
    autocomplete_fields = ("receipt_type", "report", "provider")
    compressed_fields = True
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "report",
                    "receipt_type",
                    ("receipt_number", "receipt_date"),
                    "provider",
                    "document",
                ]
            },
        )
    ]

    @display(description="Total")
    def get_total(self, obj):
        return obj.items.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("quantity") * F("unit_price"), output_field=IntegerField()
                )
            )
        )["total"]

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial["report"] = Report.objects.last()
        return initial


class ParentFilter(RelatedFieldListFilter):
    def field_choices(self, field, request, model_admin):
        queryset = AccountObject.objects.filter(parent__isnull=True)
        return [(obj.pk, str(obj)) for obj in queryset]


@register(AccountObject)
class AccountObjectAdmin(ModelAdmin):
    list_display = ("key", "value", "parent")
    list_filter = (("parent", ParentFilter),)
    search_fields = (
        "key",
        "value",
    )
    ordering = ("key",)


@register(OriginDetail)
class OriginDetailAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@register(PaymentType)
class PaymentTypeAdmin(ModelAdmin):
    list_display = ("name",)
    ordering = ("name",)


@register(DisbursementOrigin)
class DisbursementOriginAdmin(ModelAdmin):
    list_display = ("code",)
    search_fields = ("code",)
