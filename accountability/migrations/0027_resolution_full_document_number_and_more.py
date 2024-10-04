# Generated by Django 4.2.16 on 2024-10-04 00:01

from django.db import migrations, models
import django.db.models.deletion
from django.db.models import F, Value
from django.db.models.functions import Concat


def add_full_document_number(apps, schema_editor):
    Resolution = apps.get_model("accountability", "Resolution")
    Resolution.objects.update(
        full_document_number=Concat(
            F("document_number"), Value("/"), F("document_year")
        )
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0019_remove_institution_unique_establishment_institution_and_more"),
        ("accountability", "0026_alter_receiptitem_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="resolution",
            name="full_document_number",
            field=models.CharField(default="", editable=False, max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="receipt",
            name="institution",
            field=models.ForeignKey(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="receipts",
                to="core.institution",
                verbose_name="institución",
            ),
        ),
        migrations.AlterField(
            model_name="receipt",
            name="provider",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="accountability.provider",
                verbose_name="proveedor",
            ),
        ),
        migrations.RunPython(add_full_document_number, migrations.RunPython.noop),
    ]
