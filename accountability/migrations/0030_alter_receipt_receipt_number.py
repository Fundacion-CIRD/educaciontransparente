# Generated by Django 4.2.16 on 2024-10-10 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accountability", "0029_alter_receipt_receipt_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="receipt",
            name="receipt_number",
            field=models.CharField(
                blank=True,
                default="",
                max_length=30,
                verbose_name="número de comprobante",
            ),
        ),
    ]
