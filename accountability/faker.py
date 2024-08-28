import json

from accountability.models import (
    Report,
    Disbursement,
    Resolution,
    Receipt,
    ReceiptType,
    ReportStatus,
)
from core.models import Institution
from django.conf import settings


def split_into_chunks(lst, chunk_size=10):
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def fake_data():
    base_dir = settings.BASE_DIR
    with open(base_dir / "accountability/MOCK_DATA.json") as handle:
        data = json.load(handle)
        resolution = Resolution.objects.first()
        institutions = Institution.objects.filter(
            establishment__latitude__isnull=False,
            establishment__longitude__isnull=False,
        ).order_by("?")[:50]
        Disbursement.objects.all().delete()
        chunks = split_into_chunks(data)
        for institution in institutions:
            for chunk in chunks:
                for item in chunk:
                    disbursement = Disbursement.objects.create(
                        **item.get("disbursement"),
                        resolution=resolution,
                        institution=institution,
                        due_date="2024-08-26",
                    )
                    status, _ = ReportStatus.objects.get_or_create(
                        key="finished", value="Finalizado"
                    )
                    report = Report.objects.create(
                        disbursement=disbursement,
                        status=status,
                        delivered_via="Mesa de entrada",
                    )
                    receipt_type, _ = ReceiptType.objects.get_or_create(
                        name="Factura legal"
                    )
                    for receipt in item.get("receipts"):
                        Receipt.objects.create(
                            **receipt,
                            receipt_type=receipt_type,
                            report=report,
                            object_of_expenditure="345",
                        )
