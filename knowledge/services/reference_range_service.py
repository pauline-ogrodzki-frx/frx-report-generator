import json

import pandas as pd

from knowledge.models import (
    MetricDefinition,
    MetricSynonym,
    MetricReferenceRangeSet,
    MetricReferenceRangeChange,
)


def normalize_metric_name(value):
    return (
        (value or "")
        .strip()
        .lower()
        .replace("–", "-")
        .replace("—", "-")
    )


def build_metric_lookup():
    lookup = {}

    for metric in MetricDefinition.objects.all():
        lookup[normalize_metric_name(metric.metric_name)] = metric

    for synonym in MetricSynonym.objects.select_related("metric_definition"):
        lookup[normalize_metric_name(synonym.synonym)] = synonym.metric_definition

    return lookup


def build_reference_range_signature(rows):
    """
    Build a stable JSON signature for reference-range rows.

    Excludes kit_id and user_value because those are sample-specific.
    """

    signature_rows = []

    for index, row in enumerate(rows):
        signature_rows.append({
            "row_order": index,
            "category_title": str(row.get("category_title", "") or "").strip(),
            "range_lower": None if pd.isna(row.get("range_lower")) else float(row.get("range_lower")),
            "range_upper": None if pd.isna(row.get("range_upper")) else float(row.get("range_upper")),
            "evaluation": str(row.get("evaluation", "") or "").strip(),
            "range_color": str(row.get("range_color", "") or "").strip(),
        })

    return json.dumps(signature_rows, sort_keys=True)


def get_active_reference_signature(metric_definition, report_type):
    active_set = (
        MetricReferenceRangeSet.objects
        .filter(
            metric_definition=metric_definition,
            report_type=report_type,
            is_active=True,
        )
        .prefetch_related("rows")
        .order_by("-version")
        .first()
    )

    if not active_set:
        return ""

    rows = []

    for row in active_set.rows.all().order_by("row_order"):
        rows.append({
            "row_order": row.row_order,
            "category_title": row.category_title,
            "range_lower": row.range_lower,
            "range_upper": row.range_upper,
            "evaluation": row.evaluation,
            "range_color": row.range_color,
        })

    return json.dumps(rows, sort_keys=True)


def detect_reference_range_changes(metrics_csv_path, report=None, report_type="adult_microbiome"):
    """
    Compare lab CSV reference-range rows against approved database ranges.

    Creates open MetricReferenceRangeChange records when an existing metric has
    no approved range yet or when the approved range differs from the CSV.
    """

    df = pd.read_csv(metrics_csv_path)

    required_columns = {
        "name",
        "category_title",
        "range_lower",
        "range_upper",
        "evaluation",
        "range_color",
    }

    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Metrics CSV missing required reference-range columns: {sorted(missing_columns)}"
        )

    metric_lookup = build_metric_lookup()

    created_changes = []
    unresolved_metrics = []

    for raw_metric_name, metric_df in df.groupby("name", sort=False):
        lookup_key = normalize_metric_name(raw_metric_name)
        metric_definition = metric_lookup.get(lookup_key)

        if not metric_definition:
            unresolved_metrics.append(raw_metric_name)
            continue

        proposed_rows = json.loads(
            build_reference_range_signature(
                metric_df.to_dict("records")
            )
        )

        detected_signature = json.dumps(proposed_rows, sort_keys=True)

        approved_signature = get_active_reference_signature(
            metric_definition=metric_definition,
            report_type=report_type,
        )

        if detected_signature != approved_signature:
            change, created = MetricReferenceRangeChange.objects.get_or_create(
                metric_definition=metric_definition,
                report_type=report_type,
                report=report,
                detected_signature=detected_signature,
                defaults={
                    "approved_signature": approved_signature,
                    "proposed_rows": proposed_rows,
                    "status": MetricReferenceRangeChange.STATUS_OPEN,
                },
            )

            if created:
                created_changes.append(change)

    return {
        "created_changes": created_changes,
        "created_change_count": len(created_changes),
        "unresolved_metrics": unresolved_metrics,
        "unresolved_metric_count": len(unresolved_metrics),
    }