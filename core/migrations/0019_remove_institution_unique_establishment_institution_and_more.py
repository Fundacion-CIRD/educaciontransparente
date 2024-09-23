# Generated by Django 4.2.16 on 2024-09-18 02:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0018_alter_institution_code"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="institution",
            name="unique_establishment_institution",
        ),
        migrations.AddConstraint(
            model_name="institution",
            constraint=models.UniqueConstraint(
                fields=("code", "establishment", "name"),
                name="unique_establishment_institution",
            ),
        ),
    ]