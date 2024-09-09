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
)


def add_account_object_permissions(user):
    content_type = ContentType.objects.get_for_model(AccountObject)
    permissions = Permission.objects.filter(
        codename__startswith="view",
        content_type=content_type,
    )
    user.user_permissions.add(*permissions)


def add_default_permissions(user):
    add_account_object_permissions(user)
    content_types = ContentType.objects.get_for_models(
        Resolution,
        DisbursementOrigin,
        OriginDetail,
        Disbursement,
        Report,
        ReceiptType,
        Receipt,
        ReceiptItem,
    )
    permissions = Permission.objects.filter(
        content_type__in=content_types.values(),
    )
    user.user_permissions.add(*permissions)
