from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import UniqueConstraint


class ImportantDatesModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Department(ImportantDatesModel):
    code = models.CharField(max_length=12, verbose_name="código")
    name = models.CharField(max_length=256, verbose_name="nombre")

    class Meta:
        verbose_name = "departamento"
        verbose_name_plural = "departamentos"
        constraints = [UniqueConstraint(fields=("code",), name="unique_department")]

    def __str__(self):
        return self.name


class District(ImportantDatesModel):
    code = models.CharField(max_length=12, verbose_name="código")
    name = models.CharField(max_length=500, verbose_name="nombre")
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name="departamento",
        related_name="districts",
    )

    class Meta:
        verbose_name = "distrito"
        verbose_name_plural = "distritos"
        constraints = [
            UniqueConstraint(
                fields=("code", "department"), name="unique_district_in_department"
            )
        ]
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return f"{self.name} - {self.department}"


class Locality(ImportantDatesModel):
    code = models.CharField(max_length=12, verbose_name="código")
    name = models.CharField(max_length=500, verbose_name="nombre")
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        verbose_name="distrito",
        related_name="localities",
    )

    class Meta:
        verbose_name = "localidad"
        verbose_name_plural = "localidades"
        constraints = [
            UniqueConstraint(
                fields=("code", "district"), name="unique_locality_in_district"
            )
        ]
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return self.name


class Establishment(ImportantDatesModel):
    code = models.CharField(max_length=12, verbose_name="código")
    last_data_capture = models.PositiveBigIntegerField(null=True, blank=True)
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        verbose_name="distrito",
        related_name="establishments",
    )
    locality = models.ForeignKey(
        Locality,
        on_delete=models.CASCADE,
        verbose_name="localidad",
        related_name="establishments",
        null=True,
        blank=True,
    )
    zone_code = models.CharField(
        max_length=4, default="", blank=True, verbose_name="código zona"
    )
    zone_name = models.CharField(
        max_length=128, default="", blank=True, verbose_name="nombre zona"
    )
    address = models.TextField(default="", blank=True, verbose_name="dirección")
    latitude = models.DecimalField(
        max_digits=12, decimal_places=8, null=True, blank=True, verbose_name="latitud"
    )
    longitude = models.DecimalField(
        max_digits=12, decimal_places=8, null=True, blank=True, verbose_name="longitud"
    )

    class Meta:
        verbose_name = "establecimiento"
        verbose_name_plural = "establecimientos"
        constraints = [UniqueConstraint(fields=("code",), name="unique_establishment")]

    def __str__(self):
        return f"{self.code} - {self.district}"


class Institution(ImportantDatesModel):
    establishment = models.ForeignKey(
        Establishment,
        on_delete=models.CASCADE,
        related_name="institutions",
        verbose_name="establecimiento",
    )
    code = models.CharField(verbose_name="código", max_length=12)
    name = models.CharField(max_length=500, verbose_name="nombre")
    institution_type = models.CharField(max_length=50, verbose_name="tipo")
    phone_number = models.CharField(
        max_length=50, default="", blank=True, verbose_name="teléfono"
    )
    website = models.URLField(blank=True, default="", verbose_name="sitio web")
    email = models.EmailField(blank=True, default="", verbose_name="email")
    users = models.ManyToManyField(
        "users.User",
        through="InstitutionUser",
        verbose_name="usuarios",
        related_name="institutions",
    )

    class Meta:
        verbose_name = "institución"
        verbose_name_plural = "instituciones"
        constraints = [
            UniqueConstraint(
                fields=("code", "establishment", "name"),
                name="unique_establishment_institution",
            )
        ]
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return f"{self.name} ({self.establishment.district.name})"


class InstitutionUser(ImportantDatesModel):
    institution = models.ForeignKey(
        to=Institution,
        on_delete=models.CASCADE,
        related_name="institution_users",
        verbose_name="institución",
    )
    user = models.ForeignKey(
        to="users.User",
        on_delete=models.CASCADE,
        related_name="institution_users",
        verbose_name="usuario",
    )
    is_manager = models.BooleanField(default=False, verbose_name="es administrador")

    class Meta:
        verbose_name = "usuario de institución"
        verbose_name_plural = "usuarios de institución"


class Picture(ImportantDatesModel):
    file = models.ImageField(upload_to="pictures", verbose_name="imagen")
    description = models.CharField(max_length=500, default="", blank=True)
    object_id = models.PositiveBigIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        verbose_name = "imagen"
        verbose_name_plural = "imágenes"
        indexes = [models.Index(fields=["content_type", "object_id"])]

    def __str__(self):
        return self.description


class Document(ImportantDatesModel):
    name = models.CharField("nombre", max_length=100)
    file = models.FileField(upload_to="documents", verbose_name="documento")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "documento"
        verbose_name_plural = "documentos"
        indexes = [models.Index(fields=["content_type", "object_id"])]


class Resource(models.Model):
    name = models.CharField(verbose_name="nombre", max_length=150)
    description = models.TextField(verbose_name="descripción", default="", blank=True)
    url = models.URLField(verbose_name="URL", default="", blank=True)
    document = models.FileField(
        upload_to="resources", verbose_name="documento", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="creado_el")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="actualizado_el")

    class Meta:
        verbose_name = "recurso"
        verbose_name_plural = "recursos"
        ordering = ("updated_at", "name")

    def __str__(self):
        return self.name

    def clean(self):
        if not self.url and not self.document:
            raise ValidationError("Debe agregar una URL o un documento.")
