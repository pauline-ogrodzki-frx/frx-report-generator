from pathlib import Path

from reports.services.metrics.template_ordered_processor import (
    process_metrics_with_template,
)


def process_metrics_csv(metrics_csv_path, report):
    """
    Creates a processed metrics CSV before PDF generation.

    The processed file is now generated through the database-driven
    ReportMetricTemplate / MetricDefinition / MetricSynonym engine.
    """

    metrics_csv_path = Path(metrics_csv_path)

    safe_kit_id = str(report.kit_id or report.id).replace("/", "-").replace(" ", "_")

    processed_metrics_path = (
        metrics_csv_path.parent / f"{safe_kit_id}_processed_metrics.csv"
    )

    process_metrics_with_template(
        input_csv_path=metrics_csv_path,
        output_csv_path=processed_metrics_path,
        report=report,
        report_type=report.report_type.slug,
    )

    return str(processed_metrics_path)