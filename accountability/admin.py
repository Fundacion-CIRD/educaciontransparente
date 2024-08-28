from django.contrib.admin import register, display
from django.utils.numberformat import format as format_number
from unfold.admin import ModelAdmin, StackedInline

from accountability.models import (
    Disbursement,
    Report,
    ReceiptType,
    Receipt,
    ReportStatus,
    Resolution,
)
from core.admin import DocumentInline


@register(Resolution)
class ResolutionAdmin(ModelAdmin):
    list_display = ("document_number", "document_year")
    list_filter = ("document_year",)
    search_fields = ("document_number",)
    fieldsets = [
        (None, {"fields": ["document_number", "document_year", "document"]}),
    ]


@register(Disbursement)
class DisbursementAdmin(ModelAdmin):
    list_display = (
        "institution",
        "resolution",
        "get_amount_disbursed",
        "disbursement_date",
        "due_date",
    )
    list_filter = ("disbursement_date",)
    search_fields = ("institution__name",)
    autocomplete_fields = ("institution", "resolution")
    inlines = [DocumentInline]
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
                    "disbursement_date",
                    "amount_disbursed",
                    "funds_origin",
                    "origin_details",
                    "payment_type",
                ]
            },
        ),
    ]

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Disbursement.objects.all()
        return Disbursement.objects.filter(institution__users=request.user).distinct()

    @display(description="Monto desembolsado", ordering="amount_disbursed")
    def get_amount_disbursed(self, obj):
        return obj.amount_disbursed
        return format_number(obj.amount_disbursed, ",", thousand_sep=".")


@register(ReportStatus)
class ReportStatusAdmin(ModelAdmin):
    list_display = ("value",)
    fields = ("value",)


class ReceiptInline(StackedInline):
    model = Receipt
    extra = 0
    min_num = 1
    fieldsets = [
        (
            "",
            {
                "fields": [
                    "receipt_type",
                    ("receipt_number", "receipt_date"),
                    ("object_of_expenditure", "description", "total"),
                ]
            },
        ),
        # ("Documentos", {"fields": ["documents"]}),
    ]


@register(Report)
class ReportAdmin(ModelAdmin):
    list_display = ("disbursement", "status", "delivered_via", "updated_at")
    list_filter = ("status", "updated_at")
    inlines = [ReceiptInline]
    autocomplete_fields = ("disbursement",)


@register(ReceiptType)
class ReceiptTypeAdmin(ModelAdmin):
    list_display = ("name",)


@register(Receipt)
class ReceiptAdmin(ModelAdmin):
    list_display = ("receipt_type", "receipt_date", "receipt_number")
    inlines = [DocumentInline]

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial["report"] = Report.objects.last()
        return initial
