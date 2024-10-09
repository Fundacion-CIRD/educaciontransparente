import csv
import json

from django.db.models import Sum, Q, ExpressionWrapper, F, IntegerField, Value
from django.db.models.functions import Coalesce, ExtractYear
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import DetailView, TemplateView

from accountability.filters import (
    DisbursementFilter,
    ReportFilter,
    ReceiptFilter,
    ReceiptItemFilter,
)
from accountability.models import (
    Report,
    Disbursement,
    Receipt,
    ReceiptItem,
    DisbursementOrigin,
    ReceiptType,
    AccountObject,
)
from core.filters import InstitutionFilter
from core.models import Department, Institution, Resource, District
from core.serializers import InstitutionSerializer


# Create your views here.


def index(request):
    departments = (
        Department.objects.filter(
            districts__establishments__institutions__disbursements__isnull=False
        )
        .distinct()
        .order_by("name")
    )
    return render(
        request,
        context={"departments": departments},
        template_name="website/index.html",
    )


def quienes_somos(request):
    return render(request, "website/quienes_somos.html")


def open_data(request):
    return render(request, "website/open-data.html")


def institutions_open_data(request):
    institution_types = (
        Institution.objects.values_list("institution_type", flat=True)
        .distinct()
        .order_by("institution_type")
    )
    context = {
        "departments": Department.objects.order_by("name"),
        "institution_types": institution_types,
    }
    return render(request, "website/open-data/institutions.html", context)


def disbursements_open_data(request):
    context = {
        "disbursement_origins": DisbursementOrigin.objects.order_by("code"),
    }
    return render(request, "website/open-data/disbursements.html", context)


def reports_open_data(request):
    return render(request, "website/open-data/reports.html")


def receipts_open_data(request):
    return render(
        request,
        "website/open-data/receipts.html",
        {"receipt_types": ReceiptType.objects.all()},
    )


def receipt_items_open_data(request):
    return render(
        request,
        "website/open-data/receipt-items.html",
        {
            "account_objects": AccountObject.objects.filter(receipt_items__isnull=False)
            .order_by("key")
            .distinct()
        },
    )


def resources(request):
    context = {"resources": Resource.objects.all()}
    return render(request, "website/resources.html", context)


def get_totals(disbursed_qs, reported_qs):
    qs = reported_qs.annotate(
        total_reported=Coalesce(
            Sum(
                ExpressionWrapper(
                    F("receipts__items__unit_price") * F("receipts__items__quantity"),
                    output_field=IntegerField(),
                )
            ),
            Value(0, output_field=IntegerField()),
        )
    )
    return {
        "disbursed": disbursed_qs.aggregate(
            disbursed=Sum("amount_disbursed", distinct=True)
        )["disbursed"],
        "reported": qs.aggregate(reported=Sum("total_reported", distinct=True))[
            "reported"
        ],
    }


def get_yearly_report(disbursed_qs, reported_qs):
    current_year = timezone.now().year
    yearly_report = {}
    for i in range(5):
        year = current_year - i
        total_disbursed_sum = Sum(
            "amount_disbursed",
            filter=Q(disbursement_date__year=year),
            distinct=True,
        )
        total_reported_sum = Coalesce(
            Sum(
                ExpressionWrapper(
                    F("receipts__items__unit_price") * F("receipts__items__quantity"),
                    output_field=IntegerField(),
                ),
                filter=Q(receipts__report__disbursement__disbursement_date__year=year),
                distinct=True,
            ),
            Value(0, output_field=IntegerField()),
        )
        yearly_report[year] = {
            "total_disbursed": disbursed_qs.aggregate(sum=total_disbursed_sum)["sum"],
            "total_reported": reported_qs.aggregate(sum=total_reported_sum)["sum"],
        }
    return yearly_report


class InstitutionDetailsView(DetailView):
    queryset = Institution.objects.all()
    template_name = "website/institution-details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        disbursed_qs = Disbursement.objects.filter(institution=context["object"])
        reported_qs = Report.objects.filter(disbursement__institution=context["object"])
        years = (
            disbursed_qs.filter(disbursement_date__isnull=False)
            .annotate(year=ExtractYear("disbursement_date"))
            .values_list("year", flat=True)
            .distinct()
            .order_by("-year")
        )
        context["totals"] = get_totals(disbursed_qs, reported_qs)
        yearly_report = get_yearly_report(disbursed_qs, reported_qs)
        context["yearly_report"] = json.dumps(yearly_report, default=str)
        context["years"] = years
        return context


class ReportDetailView(TemplateView):
    template_name = "website/report-details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = get_object_or_404(Institution, pk=kwargs["institution_id"])
        context["report"] = get_object_or_404(Report, pk=kwargs.get("report_id"))
        context["receipts"] = context["report"].receipts.order_by("-receipt_date")
        reported_qs = Report.objects.filter(id=context["report"].id)
        disbursement_qs = Disbursement.objects.filter(reports__in=reported_qs)
        context["totals"] = get_totals(disbursement_qs, reported_qs)
        return context


def get_report_total(report):
    return report.receipts.aggregate(
        total=Sum("receipt_total", output_field=IntegerField())
    )["total"]


CSV_SETTINGS = {
    "institutions": {
        "queryset": Institution.objects.filter(disbursements__isnull=False).distinct(),
        "filterset": InstitutionFilter,
        "filename": "instituciones.csv",
        "headers": [
            "id",
            "codigo_mec_establecimiento",
            "codigo_mec",
            "nombre",
            "tipo",
            "direccion",
            "telefono",
            "sitio_web",
            "email",
            "latitud",
            "longitud",
            "localidad",
            "distrito",
            "departamento",
        ],
        "extractor": lambda institution: [
            institution.id,
            institution.establishment.code,
            institution.code,
            institution.name,
            institution.institution_type,
            institution.establishment.address,
            institution.phone_number,
            institution.website,
            institution.email,
            institution.establishment.latitude,
            institution.establishment.longitude,
            institution.establishment.locality.name,
            institution.establishment.district.name,
            institution.establishment.district.department.name,
        ],
    },
    "disbursements": {
        "queryset": Disbursement.objects.all(),
        "filterset": DisbursementFilter,
        "filename": "desembolsos.csv",
        "headers": [
            "id",
            "resolucion",
            "id_institucion",
            "nombre_institucion",
            "fecha_desembolso",
            "monto_resolucion",
            "monto_desembolsado",
            "origen_fondo",
            "marco",
            "fecha_a_rendir",
            "nombre_director",
            "ci_director",
            "tipo_pago",
            "observaciones",
        ],
        "extractor": lambda disbursement: [
            disbursement.id,
            str(disbursement.resolution),
            disbursement.institution_id,
            disbursement.institution.name,
            disbursement.disbursement_date,
            disbursement.resolution_amount,
            disbursement.amount_disbursed,
            disbursement.funds_origin.code,
            disbursement.origin_details.name,
            disbursement.due_date,
            disbursement.principal_name,
            disbursement.principal_issued_id,
            disbursement.payment_type.name if disbursement.payment_type else "",
            disbursement.comments,
        ],
    },
    "reports": {
        "queryset": Report.objects.all(),
        "filterset": ReportFilter,
        "filename": "rendiciones.csv",
        "headers": [
            "id",
            "id_desembolso",
            "id_institucion",
            "nombre_institucion",
            "fecha_rendicion",
            "monto_rendido",
            "recepcion",
            "observaciones",
        ],
        "extractor": lambda report: [
            report.id,
            report.disbursement.id,
            report.disbursement.institution.id,
            report.disbursement.institution.name,
            report.report_date,
            get_report_total(report),
            report.delivered_via,
        ],
    },
    "receipts": {
        "queryset": Receipt.objects.all(),
        "filterset": ReceiptFilter,
        "filename": "comprobantes.csv",
        "headers": [
            "id",
            "id_institucion",
            "id_desembolso",
            "id_rendicion",
            "tipo_comprobante",
            "nro_comprobante",
            "fecha_comprobante",
            "ruc_proveedor",
            "nombre_proveedor",
            "total",
        ],
        "extractor": lambda receipt: [
            receipt.id,
            receipt.institution_id,
            receipt.disbursement.id,
            receipt.report_id,
            receipt.receipt_type.name,
            receipt.receipt_number,
            receipt.receipt_date,
            receipt.provider.ruc if receipt.provider else "Sin datos",
            receipt.provider.name if receipt.provider else "Sin datos",
            receipt.receipt_total,
        ],
    },
    "receipt-items": {
        "queryset": ReceiptItem.objects.all(),
        "filterset": ReceiptItemFilter,
        "filename": "detalles_de_comprobante.csv",
        "headers": [
            "id",
            "id_comprobante",
            "objeto_gasto",
            "cantidad",
            "concepto",
            "precio_unitario",
        ],
        "extractor": lambda receipt_item: [
            receipt_item.id,
            receipt_item.receipt_id,
            f"{receipt_item.object_of_expenditure.key}: {receipt_item.object_of_expenditure.value}",
            receipt_item.quantity,
            receipt_item.description,
            receipt_item.unit_price,
        ],
    },
}


def add_csv_data(csv_writer, collection, request):
    collection_settings = CSV_SETTINGS[collection]
    filterset = collection_settings["filterset"](
        request.GET, queryset=collection_settings["queryset"]
    )
    columns = collection_settings["headers"]
    csv_writer.writerow(columns)
    for item in filterset.qs.all():
        csv_writer.writerow(collection_settings["extractor"](item))


def add_json_data(collection, request):
    settings = CSV_SETTINGS[collection]
    filterset = settings["filterset"](request.GET, queryset=settings["queryset"])
    data = []
    for item in filterset.qs.all():
        data.append(dict(zip(settings["headers"], settings["extractor"](item))))
    return data


def export_to_csv(request):
    collection = request.GET.get("collection")
    _format = request.GET.get("format")
    if not collection:
        return HttpResponse("No collection selected")
    if _format == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="{CSV_SETTINGS[collection]["filename"]}"'
        )
        writer = csv.writer(response)
        add_csv_data(writer, collection, request)
    else:
        response = JsonResponse(add_json_data(collection, request), safe=False)
    return response
