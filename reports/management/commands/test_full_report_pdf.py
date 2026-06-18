from pathlib import Path

from django.core.management.base import BaseCommand

from reports.models import ReportType, Report
from reports.services.taxa_description_service import enrich_taxa_csv
from reports.services.pdf_report_service import generate_pdf_with_existing_builder


class Command(BaseCommand):
    help = "Test full report generation using metrics CSV, taxa CSV, and existing PDF builder"

    def add_arguments(self, parser):
        parser.add_argument("metrics_csv_path", type=str)
        parser.add_argument("taxa_csv_path", type=str)
        parser.add_argument("--patient", type=str, default="Test Patient")
        parser.add_argument("--kit", type=str, required=True)
        parser.add_argument("--audience", type=str, default="adult")

    def handle(self, *args, **options):
        metrics_csv_path = options["metrics_csv_path"]
        taxa_csv_path = options["taxa_csv_path"]
        patient_name = options["patient"]
        audience = options["audience"]

        report_type, _ = ReportType.objects.update_or_create(
            name="Adult Gut Microbiome",
            defaults={
                "slug": "adult-gut-microbiome",
                "is_active": True,
            },
        )

        kit_id = options["kit"]

        report = Report.objects.create(
            report_type=report_type,
            patient_name=patient_name,
            physician_name="NAME",
            kit_id=kit_id,
            enterotype="Lachnospiraceae",
        )

        enrichment_result = enrich_taxa_csv(
            taxa_csv_path=taxa_csv_path,
            report=report,
            report_audience=audience,
        )

        enriched_taxa_path = (
            Path(taxa_csv_path).parent
            / f"{Path(taxa_csv_path).stem}_enriched.csv"
        )

        enrichment_result["dataframe"].to_csv(
            enriched_taxa_path,
            index=False,
        )

        generated_report = generate_pdf_with_existing_builder(
            report=report,
            metrics_csv_path=metrics_csv_path,
            enriched_taxa_csv_path=enriched_taxa_path,
        )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Full PDF report test complete"))
        self.stdout.write(f"Report ID: {report.id}")
        self.stdout.write(f"Patient: {report.patient_name}")
        self.stdout.write(f"Matched taxa: {enrichment_result['matched_count']}")
        self.stdout.write(f"Missing descriptions overall: {enrichment_result['missing_count']}")
        self.stdout.write(f"Generated PDF: {generated_report.pdf_file.url}")