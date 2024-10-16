from django.db import models
from django.contrib.admin import register, display
from django.contrib.contenttypes.admin import GenericTabularInline
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.forms.widgets import WysiwygWidget

from core.models import (
    Department,
    District,
    Institution,
    Locality,
    Establishment,
    Document,
    Resource,
)


@register(Department)
class DepartmentAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@register(District)
class DistrictAdmin(ModelAdmin):
    list_display = ("name", "department")
    search_fields = ("name", "department__name")
    list_filter = ("department",)
    ordering = ("department", "name")


@register(Locality)
class LocalityAdmin(ModelAdmin):
    list_display = ("name", "district")
    search_fields = ("name", "district__name")
    list_filter = ("district__department",)
    ordering = (
        "district__name",
        "name",
    )


@register(Establishment)
class EstablishmentAdmin(ModelAdmin):
    list_display = ("code", "locality", "district", "zone_name")
    list_filter = ("zone_name", "district__department")
    ordering = ("district", "code")
    search_fields = ("code",)


@register(Institution)
class InstitutionAdmin(ModelAdmin):
    list_display = (
        "name",
        "get_district",
        "get_department",
    )
    list_filter = (
        "institution_type",
        "establishment__district__department",
    )
    search_fields = (
        "name",
        "code",
        "establishment__code",
        "establishment__district__name",
    )
    ordering = ("name",)
    autocomplete_fields = ("establishment",)
    fieldsets = [
        (None, {"fields": ["name", ("code", "institution_type"), "establishment"]}),
        (
            "Contacto",
            {"fields": ["email", "phone_number", "website"]},
        ),
    ]

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        return ["establishment", "code", "institution_type", "name"]

    @display(description="Distrito", ordering="establishment__district__name")
    def get_district(self, obj):
        return obj.establishment.district.name

    @display(
        description="Departamento", ordering="establishment__district__department__name"
    )
    def get_department(self, obj):
        return obj.establishment.district.department.name

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Institution.objects.all()
        return Institution.objects.filter(users=request.user)

    def get_model_perms(self, request):
        return {
            "add": request.user.is_superuser,
            "change": request.user.is_superuser,
            "delete": request.user.is_superuser,
            "view": self.has_view_permission(request),
        }


class DocumentInline(GenericTabularInline, TabularInline):
    model = Document
    fields = ("name", "file")
    extra = 0

    @staticmethod
    def get_form_queryset(obj):
        return Document.objects.filter(object_id=obj.id)

    @staticmethod
    def save_new_instance(parent, instance):
        instance.content_object = parent
        instance.object_id = parent.id
        instance.save()


@register(Resource)
class ResourceAdmin(ModelAdmin):
    list_display = ("name", "updated_at")
    search_fields = ("name", "description")

    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }
