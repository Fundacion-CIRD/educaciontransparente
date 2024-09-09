import json

from django.db import migrations, transaction
from django.conf import settings


def import_account_objects(apps, schema_editor):
    AccountObject = apps.get_model("accountability", "AccountObject")

    @transaction.atomic
    def process_category(category_data, parent=None):
        category = AccountObject.objects.create(
            key=category_data["code"], value=category_data["name"], parent=parent
        )
        for subcategory in category_data.get("subcategories", []):
            subcategory_obj = process_category(subcategory, parent=category)
            for item in subcategory.get("items", []):
                AccountObject.objects.create(
                    key=item["code"], value=item["name"], parent=subcategory_obj
                )
        return category

    filename = (
        settings.BASE_DIR / "accountability" / "fixtures" / "account_objects.json"
    )
    with open(filename) as handle:
        data = json.load(handle)
        for element in data:
            process_category(element)


class Migration(migrations.Migration):
    dependencies = [
        ("accountability", "0007_accountobject_alter_reportstatus_options_and_more"),
    ]

    operations = [
        migrations.RunPython(import_account_objects, migrations.RunPython.noop),
    ]
