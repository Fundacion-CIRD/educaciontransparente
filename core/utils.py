from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from core.models import Institution, InstitutionUser, Picture, Document


def add_institution_permissions(user):
    content_type = ContentType.objects.get_for_model(Institution)
    permissions = Permission.objects.filter(
        codename__startswith="view",
        content_type=content_type,
    )
    user.user_permissions.add(*permissions)


def add_default_permissions(user):
    add_institution_permissions(user)
    content_types = ContentType.objects.get_for_models(
        InstitutionUser,
        Picture,
        Document,
    )
    permissions = Permission.objects.filter(
        content_type__in=content_types.values(),
    )
    user.user_permissions.add(*permissions)
