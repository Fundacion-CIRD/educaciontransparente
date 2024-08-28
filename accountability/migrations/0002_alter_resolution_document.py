# Generated by Django 4.2.15 on 2024-08-22 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accountability", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resolution",
            name="document",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="resolutions",
                verbose_name="documento de resolución",
            ),
        ),
    ]
