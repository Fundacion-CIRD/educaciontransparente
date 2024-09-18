import csv
import json

from django.db.models import Sum, Q, ExpressionWrapper, F, IntegerField, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import DetailView, TemplateView

from accountability.models import Report, Disbursement, Receipt
from core.models import Department, Institution, Resource
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
        context["totals"] = get_totals(disbursed_qs, reported_qs)
        yearly_report = get_yearly_report(disbursed_qs, reported_qs)
        context["yearly_report"] = json.dumps(yearly_report, default=str)
        context["years"] = yearly_report.keys()
        print(context["years"])
        return context


class ReportDetailView(TemplateView):
    template_name = "website/report-details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = get_object_or_404(Institution, pk=kwargs["institution_id"])
        context["report"] = get_object_or_404(Report, pk=kwargs.get("report_id"))
        reported_qs = Report.objects.filter(id=context["report"].id)
        disbursement_qs = Disbursement.objects.filter(reports__in=reported_qs)
        context["totals"] = get_totals(disbursement_qs, reported_qs)
        return context


CSV_SETTINGS = {
    "institutions": {
        "queryset": Institution.objects.filter(disbursements__isnull=False).distinct(),
        "filename": "instituciones.csv",
        "headers": [
            "id",
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
        "filename": "desembolsos.csv",
        "headers": [
            "id",
            "resolucion",
            "id_institucion",
            "nombre_institucion",
            "fecha_desembolso",
            "monto_desembolso",
            "origen_fondo",
            "marco",
            "fecha_a_rendir",
            "nombre_director",
            "ci_director",
            "tipo_pago",
        ],
        "extractor": lambda disbursement: [
            disbursement.id,
            str(disbursement.resolution),
            disbursement.institution_id,
            disbursement.institution.name,
            disbursement.disbursement_date,
            disbursement.amount_disbursed,
            disbursement.funds_origin,
            disbursement.origin_details,
            disbursement.due_date,
            disbursement.principal_name,
            disbursement.principal_issued_id,
            disbursement.payment_type,
        ],
    },
    "reports": {
        "queryset": Report.objects.all(),
        "filename": "rendiciones.csv",
        "headers": [
            "id",
            "id_desembolso",
            "id_institucion",
            "nombre_institucion",
            "estado",
            "recepcion",
        ],
        "extractor": lambda report: [
            report.id,
            report.disbursement.id,
            report.disbursement.institution.id,
            report.disbursement.institution.name,
            report.status.value,
            report.delivered_via,
        ],
    },
    "receipts": {
        "queryset": Receipt.objects.all(),
        "filename": "comprobantes.csv",
        "headers": [
            "id",
            "id_rendicion",
            "tipo_comprobante",
            "nro_comprobante",
            "fecha_comprobante",
            "objeto_gasto",
            "conceptos",
            "total",
        ],
        "extractor": lambda receipt: [
            receipt.id,
            receipt.report_id,
            receipt.receipt_type.name,
            receipt.receipt_number,
            receipt.receipt_date,
            receipt.object_of_expenditure,
            receipt.description,
            receipt.total,
        ],
    },
}


def add_csv_data(csv_writer, collection):
    collection_settings = CSV_SETTINGS[collection]
    columns = collection_settings["headers"]
    csv_writer.writerow(columns)
    for item in collection_settings["queryset"]:
        csv_writer.writerow(collection_settings["extractor"](item))


def add_json_data(collection):
    settings = CSV_SETTINGS[collection]
    data = []
    for item in settings["queryset"]:
        data.append(dict(zip(settings["headers"], settings["extractor"](item))))
    return data


def export_to_csv(request):
    collection = request.GET.get("collection")
    format = request.GET.get("format")
    if not collection:
        return HttpResponse("No collection selected")
    if format == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="{CSV_SETTINGS[collection]["filename"]}"'
        )
        writer = csv.writer(response)
        add_csv_data(writer, collection)
    else:
        response = JsonResponse(add_json_data(collection), safe=False)
    return response
