from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand

from reports.models import ReportType, Report, UploadedCSV
from reports.services.taxa_description_service import enrich_taxa_csv


class Command(BaseCommand):
    help = "Test report processing using reordered metrics and taxa CSVs"

    def add_arguments(self, parser):
        parser.add_argument("metrics_csv_path", type=str)
        parser.add_argument("taxa_csv_path", type=str)
        parser.add_argument("--patient", type=str, default="Test Patient")
        parser.add_argument("--audience", type=str, default="adult")

    def handle(self, *args, **options):
        metrics_csv_path = options["metrics_csv_path"]
        taxa_csv_path = options["taxa_csv_path"]
        patient_name = options["patient"]
        audience = options["audience"]

        report_type, _ = ReportType.objects.get_or_create(
            name="Adult Gut Microbiome"
        )

        report = Report.objects.create(
            patient_name=patient_name,
            report_type=report_type,
        )

        uploaded_csv = UploadedCSV.objects.create(
            report=report,
        )

        with open(metrics_csv_path, "rb") as metrics_file:
            uploaded_csv.original_metrics_csv.save(
                Path(metrics_csv_path).name,
                File(metrics_file),
                save=False,
            )

        with open(taxa_csv_path, "rb") as taxa_file:
            uploaded_csv.original_taxa_csv.save(
                Path(taxa_csv_path).name,
                File(taxa_file),
                save=False,
            )

        result = enrich_taxa_csv(
            taxa_csv_path=taxa_csv_path,
            report=report,
            report_audience=audience,
        )

        enriched_taxa_path = (
            Path(taxa_csv_path).parent
            / f"{Path(taxa_csv_path).stem}_enriched.csv"
        )

        result["dataframe"].to_csv(
            enriched_taxa_path,
            index=False,
        )

        with open(enriched_taxa_path, "rb") as enriched_file:
            uploaded_csv.processed_taxa_csv.save(
                enriched_taxa_path.name,
                File(enriched_file),
                save=False,
            )

        uploaded_csv.save()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Report processing test complete"))
        self.stdout.write(f"Report ID: {report.id}")
        self.stdout.write(f"Patient: {report.patient_name}")
        self.stdout.write(f"Matched taxa: {result['matched_count']}")
        self.stdout.write(f"Missing descriptions overall: {result['missing_count']}")
        self.stdout.write(f"Enriched taxa CSV: {enriched_taxa_path}")