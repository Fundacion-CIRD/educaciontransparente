# Generated by Django 4.2.15 on 2024-08-22 00:02

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0007_alter_institution_code"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="institutionuser",
            options={
                "verbose_name": "usuario de institución",
                "verbose_name_plural": "usuarios de institución",
            },
        ),
        migrations.AddField(
            model_name="institution",
            name="users",
            field=models.ManyToManyField(
                through="core.InstitutionUser",
                to=settings.AUTH_USER_MODEL,
                verbose_name="usuarios",
            ),
        ),
    ]
