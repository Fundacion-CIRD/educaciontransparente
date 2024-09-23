from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from accountability.models import (
    Resolution,
    Disbursement,
    Report,
    ReceiptType,
    AccountObject,
    Receipt,
    ReceiptItem,
    DisbursementOrigin,
    OriginDetail,
    PaymentType,
    Provider,
)


def add_view_permissions(user, *models):
    content_types = ContentType.objects.get_for_models(*models).values()
    permissions = Permission.objects.filter(
        codename__startswith="view",
        content_type__in=content_types,
    )
    user.user_permissions.add(*permissions)


def add_default_permissions(user):
    add_view_permissions(user, AccountObject, DisbursementOrigin)
    content_types = ContentType.objects.get_for_models(
        Resolution,
        OriginDetail,
        PaymentType,
        Disbursement,
        Report,
        ReceiptType,
        Receipt,
        ReceiptItem,
        Provider,
    )
    permissions = Permission.objects.filter(
        content_type__in=content_types.values(),
    )
    user.user_permissions.add(*permissions)
