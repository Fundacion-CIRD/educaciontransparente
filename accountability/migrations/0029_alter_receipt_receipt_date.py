# Generated by Django 4.2.16 on 2024-10-10 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accountability", "0028_alter_receipt_provider_alter_report_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="receipt",
            name="receipt_date",
            field=models.DateField(null=True, verbose_name="fecha de comprobante"),
        ),
    ]
