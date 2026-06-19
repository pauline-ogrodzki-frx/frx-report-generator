import json
import os
import shutil
from pathlib import Path

from django.conf import settings
from django.core.files import File

from reports.models import GeneratedReport


def generate_pdf_with_existing_builder(
    report,
    metrics_csv_path,
    enriched_taxa_csv_path,
):
    """
    Uses the existing report_builder.py pipeline by creating a temporary config.json.
    """

    legacy_dir = Path(settings.BASE_DIR)

    output_folder = legacy_dir / "generated_reports"
    output_folder.mkdir(exist_ok=True)

    config = {
        "output_folder": str(output_folder),
        "Physician Name": report.physician_name or "",
        "Patient Name": report.patient_name or "",
        "Kit ID": report.kit_id or str(report.id),
        "Sampling Date": report.sampling_date.strftime("%Y-%m-%d") if report.sampling_date else "",
        "metrics_file": str(metrics_csv_path),
        "taxa_file": str(enriched_taxa_csv_path),
        "enterotype": report.enterotype or "LACHNOSPIRACEAE",
    }

    config_path = legacy_dir / "config.json"

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

        print("PDF CONFIG USED:")
        print(config)

    import report_builder

    report_builder.build_pdf_report(config)

    expected_pdf_path = output_folder / f"report_TEST{report.kit_id}.pdf"

    if not expected_pdf_path.exists():
        available_files = [file.name for file in output_folder.glob("*")]
        raise FileNotFoundError(
            f"Expected PDF was not created: {expected_pdf_path}. "
            f"Files currently in output folder: {available_files}"
        )

    generated_report = GeneratedReport.objects.create(
        report=report,
    )

    with open(expected_pdf_path, "rb") as pdf_file:
        generated_report.pdf_file.save(
            expected_pdf_path.name,
            File(pdf_file),
            save=True,
        )

    return generated_report
