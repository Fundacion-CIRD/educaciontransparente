from argparse import FileType

from django.core.management import BaseCommand

from core.processors import DataImporter


class Command(BaseCommand):
    help = "Imports a CSV file containing establishments or institutions"

    def add_arguments(self, parser):
        parser.add_argument(
            "import_type",
            type=str,
            choices=["establishments", "institutions"],
        )
        parser.add_argument("import_file", nargs="?", type=FileType("r"))

    def handle(self, *args, **options):
        importer = DataImporter(options["import_file"], options["import_type"])
        skipped_lines = importer.process()
        if not skipped_lines:
            self.stdout.write(self.style.SUCCESS("No skipped lines"))
        for line in skipped_lines:
            self.stdout.write(
                self.style.SUCCESS(f"Skipped line {line[0]}. Reason: {line[1]}")
            )
