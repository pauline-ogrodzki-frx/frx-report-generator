import pandas as pd

from django.core.management.base import BaseCommand
from knowledge.models import TaxonDefinition


class Command(BaseCommand):
    help = "Import FRX microorganism definitions from Excel workbook"

    def add_arguments(self, parser):
        parser.add_argument("excel_path", type=str)

    def clean_value(self, value):
        if pd.isna(value):
            return ""
        return str(value).strip()

    def handle(self, *args, **options):
        excel_path = options["excel_path"]

        self.stdout.write(self.style.WARNING("Loading Excel workbook..."))

        df = pd.read_excel(
            excel_path,
            sheet_name="Microorganisms"
        )

        required_columns = [
            "organism",
            "phylum",
            "associations",
            "adult description",
            "infant/child description",
        ]

        missing_columns = [
            column for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:
            self.stdout.write(
                self.style.ERROR(
                    f"Missing required columns: {missing_columns}"
                )
            )
            return

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for _, row in df.iterrows():
            organism = self.clean_value(row["organism"])

            if not organism:
                skipped_count += 1
                continue

            obj, created = TaxonDefinition.objects.update_or_create(
                organism=organism,
                defaults={
                    "phylum": self.clean_value(row["phylum"]),
                    "associations": self.clean_value(row["associations"]),
                    "frx_description": self.clean_value(row["adult description"]),
                    "baby_description": self.clean_value(row["infant/child description"]),
                    "is_active": True,
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Import complete."))
        self.stdout.write(f"Created: {created_count}")
        self.stdout.write(f"Updated: {updated_count}")
        self.stdout.write(f"Skipped rows without organism: {skipped_count}")

