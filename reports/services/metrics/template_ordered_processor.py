import csv
from pathlib import Path

from knowledge.models import (
    MetricDefinition,
    MetricSynonym,
    ReportMetricTemplate,
)
from reports.models import MissingMetricDefinition


def normalize_metric_name(value):
    return (
        (value or "")
        .strip()
        .lower()
        .replace("–", "-")
        .replace("—", "-")
    )

def build_metric_lookup():
    """
    Build a lookup dictionary that maps both canonical metric names
    and known synonyms to the canonical MetricDefinition.
    """

    lookup = {}

    for metric in MetricDefinition.objects.all():
        lookup[normalize_metric_name(metric.metric_name)] = metric

    for synonym in MetricSynonym.objects.select_related("metric_definition"):
        lookup[normalize_metric_name(synonym.synonym)] = synonym.metric_definition

    return lookup


def read_metric_rows(input_csv_path):
    input_csv_path = Path(input_csv_path)

    with input_csv_path.open("r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        rows = list(reader)

    if not fieldnames:
        raise ValueError("Metrics CSV has no headers.")

    if "name" in fieldnames:
        metric_name_column = "name"
    else:
        metric_name_column = fieldnames[0]

    rows_by_metric_name = {
        normalize_metric_name(row.get(metric_name_column)): row
        for row in rows
        if normalize_metric_name(row.get(metric_name_column))
    }

    return fieldnames, metric_name_column, rows, rows_by_metric_name


def build_ordered_metric_context(
    input_csv_path,
    report=None,
    report_type="adult_microbiome",
    record_missing=False,
):
    fieldnames, metric_name_column, rows, rows_by_metric_name = read_metric_rows(
        input_csv_path
    )
    
    metric_lookup = build_metric_lookup()

    templates = (
        ReportMetricTemplate.objects
        .filter(report_type=report_type, is_active=True)
        .select_related("metric_definition", "section")
        .order_by("display_order")
    )

    ordered_metrics = []
    matched_metric_keys = set()
    recorded_missing_metric_names = set()

    for template in templates:
        template_metric_name = template.metric_definition.metric_name
        metric_lookup_key = normalize_metric_name(template_metric_name)
        source_row = rows_by_metric_name.get(metric_lookup_key)

        metric_context = {
            "metric_name": template_metric_name,
            "display_name": template.metric_definition.display_name,
            "category": template.metric_definition.category,
            "category_title": template.category_title,
            "section": template.section.section_name,
            "super_category": template.section.super_category,
            "display_order": template.display_order,
            "is_percentage": template.is_percentage,
            "use_italics": template.use_italics,
            "comments": template.comments,
            "is_required": template.is_required,
            "source_row": source_row,
            "is_present": source_row is not None,
        }

        ordered_metrics.append(metric_context)

        if source_row:
            matched_metric_keys.add(metric_lookup_key)
        elif (
            record_missing
            and report is not None
            and template_metric_name not in recorded_missing_metric_names
        ):
            MissingMetricDefinition.objects.get_or_create(
                report=report,
                metric_name=template_metric_name,
                defaults={
                    "category_title": template.category_title,
                    "resolved": False,
                },
            )
            recorded_missing_metric_names.add(template_metric_name)

    extra_metrics = []

    for metric_lookup_key, row in rows_by_metric_name.items():
        if metric_lookup_key not in matched_metric_keys:
            original_metric_name = row.get(metric_name_column, metric_lookup_key)

            extra_metrics.append({
                "metric_name": original_metric_name,
                "display_name": original_metric_name,
                "category": "Unmapped lab metric",
                "category_title": "Unmapped lab metric",
                "section": "Unmapped",
                "super_category": "Unmapped",
                "display_order": None,
                "is_percentage": False,
                "use_italics": False,
                "comments": "",
                "is_required": False,
                "source_row": row,
                "is_present": True,
            })

            if (
                record_missing
                and report is not None
                and original_metric_name not in recorded_missing_metric_names
            ):
                MissingMetricDefinition.objects.get_or_create(
                    report=report,
                    metric_name=original_metric_name,
                    defaults={
                        "category_title": "Unmapped lab metric",
                        "resolved": False,
                    },
                )
                recorded_missing_metric_names.add(original_metric_name)

    return {
        "fieldnames": fieldnames,
        "metric_name_column": metric_name_column,
        "input_rows": len(rows),
        "template_rows": templates.count(),
        "matched_rows": len(matched_metric_keys),
        "ordered_metrics": ordered_metrics,
        "extra_metrics": extra_metrics,
    }


def export_metric_context_to_legacy_csv(metric_context, output_csv_path):
    output_csv_path = Path(output_csv_path)
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = metric_context["fieldnames"]

    export_rows = []

    for metric in metric_context["ordered_metrics"]:
        if metric["source_row"]:
            export_rows.append(metric["source_row"])

    for metric in metric_context["extra_metrics"]:
        if metric["source_row"]:
            export_rows.append(metric["source_row"])

    with output_csv_path.open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(export_rows)

    return {
        "output_csv_path": str(output_csv_path),
        "output_rows": len(export_rows),
    }


def process_metrics_with_template(
    input_csv_path,
    output_csv_path,
    report=None,
    report_type="adult_microbiome",
):
    metric_context = build_ordered_metric_context(
        input_csv_path=input_csv_path,
        report=report,
        report_type=report_type,
        record_missing=True,
    )

    export_result = export_metric_context_to_legacy_csv(
        metric_context=metric_context,
        output_csv_path=output_csv_path,
    )

    return {
        **metric_context,
        **export_result,
    }