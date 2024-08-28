import uuid

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.text import slugify


class Resolution(models.Model):
    document_number = models.PositiveSmallIntegerField(verbose_name="nro. resolución")
    document_year = models.PositiveSmallIntegerField(verbose_name="año de resolución")
    document = models.FileField(
        upload_to="resolutions",
        verbose_name="documento de resolución",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "resolución"
        verbose_name_plural = "resoluciones"

    def __str__(self):
        return f"{self.document_number}/{self.document_year}"


class Disbursement(models.Model):
    resolution = models.ForeignKey(
        Resolution,
        on_delete=models.CASCADE,
        related_name="disbursements",
        verbose_name="resolución",
    )
    institution = models.ForeignKey(
        "core.Institution",
        on_delete=models.CASCADE,
        related_name="disbursements",
        verbose_name="institución",
    )
    disbursement_date = models.DateField(verbose_name="fecha de desembolso")
    amount_disbursed = models.IntegerField(verbose_name="monto desembolsado", null=True)
    funds_origin = models.CharField(
        max_length=50, default="", blank=True, verbose_name="origen del ingreso"
    )
    origin_details = models.TextField(default="", blank=True, verbose_name="marco")
    due_date = models.DateField(verbose_name="fecha a rendir")
    principal_name = models.CharField(
        max_length=200,
        default="",
        blank=True,
        verbose_name="nombre del director",
    )
    principal_issued_id = models.CharField(
        max_length=20, default="", blank=True, verbose_name="C.I. del director"
    )
    payment_type = models.CharField(
        max_length=150, default="", blank=True, verbose_name="tipo de pago"
    )
    documents = GenericRelation(
        "core.Document", related_name="expense_report", verbose_name="documentos"
    )
    pictures = GenericRelation(
        "core.Picture", related_name="expense_report", verbose_name="imágenes"
    )
    comments = models.TextField(default="", blank=True, verbose_name="observaciones")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "desembolso"
        verbose_name_plural = "desembolsos"

    def __str__(self):
        year, month, day = str(self.disbursement_date).split("-")
        _date = f"{day}/{month}/{year}"
        return f"Des. resol. {self.resolution} ({_date}): {self.institution.name}"


class ReportStatus(models.Model):
    key = models.CharField(max_length=20, unique=True, verbose_name="código")
    value = models.CharField(max_length=200, verbose_name="nombre")

    class Meta:
        verbose_name = "Estado de rendición"
        verbose_name_plural = "Estados de rendición"

    def __str__(self):
        return self.value

    def clean(self):
        super().clean()
        if not self.key:
            self.key = slugify(self.value)
        original_key = self.key
        while ReportStatus.objects.filter(key=self.key).exists():
            random_suffix = uuid.uuid4().hex[:6]
            self.key = f"{original_key}-{random_suffix}"


class Report(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    disbursement = models.ForeignKey(
        Disbursement,
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name="desembolso",
    )
    status = models.ForeignKey(
        ReportStatus, on_delete=models.PROTECT, verbose_name="estado"
    )
    delivered_via = models.CharField(max_length=250, verbose_name="recepción")

    class Meta:
        verbose_name = "rendición"
        verbose_name_plural = "rendiciones"

    def __str__(self):
        return f"{self.disbursement}: {self.updated_at} ({self.status.value})"


class ReceiptType(models.Model):
    name = models.CharField("nombre", max_length=100, unique=True)

    class Meta:
        verbose_name = "tipo de comprobante"
        verbose_name_plural = "tipos de comprobante"

    def __str__(self):
        return self.name


class Receipt(models.Model):
    report = models.ForeignKey(
        Report, on_delete=models.CASCADE, related_name="receipts"
    )
    receipt_type = models.ForeignKey(
        ReceiptType,
        on_delete=models.CASCADE,
        related_name="receipts",
        verbose_name="tipo de comprobante",
    )
    receipt_date = models.DateField(verbose_name="fecha")
    receipt_number = models.CharField(
        verbose_name="número de comprobante", max_length=30
    )
    object_of_expenditure = models.CharField(
        max_length=10, default="", blank=True, verbose_name="Objeto de gasto"
    )
    description = models.CharField("concepto", default="", blank=True, max_length=2000)
    total = models.PositiveIntegerField(verbose_name="Total", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    documents = GenericRelation(
        "core.Document", related_name="receipts", verbose_name="documentos"
    )

    class Meta:
        verbose_name = "comprobante"
        verbose_name_plural = "comprobantes"

    def __str__(self):
        return f"{self.receipt_type} nro. {self.receipt_number}"
