# Generated by Django 4.2.16 on 2024-09-18 02:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0018_alter_institution_code"),
        ("accountability", "0024_alter_report_balance_alter_report_delivered_via"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="report",
            name="balance",
        ),
        migrations.RemoveField(
            model_name="report",
            name="reported_amount",
        ),
        migrations.AlterField(
            model_name="report",
            name="institution",
            field=models.ForeignKey(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reports",
                to="core.institution",
            ),
        ),
    ]