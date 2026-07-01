import pandas as pd

from knowledge.models import MetricDefinition, MetricSynonym, ReportMetricTemplate


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


def build_template_list(report_type):
    return (
        ReportMetricTemplate.objects
        .filter(
            report_type=report_type,
            is_active=True,
            include_in_pdf=True,
            metric_order__gt=0,
            super_category_order__gt=0,
            category_order__gt=0,
        )
        .select_related("metric_definition")
        .order_by(
            "super_category_order",
            "category_order",
            "metric_order",
            "display_order",
            "id",
        )
    )


def apply_legacy_range_template(metric_df, template):
    """
    Rebuild metric rows only when the legacy template adds PDF-only rows.

    For now, only expand when the legacy template has more rows than the
    original lab CSV for that metric.
    """

    if not template.legacy_range_template:
        return metric_df

    if len(template.legacy_range_template) <= len(metric_df):
        return metric_df

    source_row = metric_df.iloc[0].to_dict()
    output_rows = []

    for template_row in template.legacy_range_template:
        new_row = source_row.copy()

        for key, value in template_row.items():
            if key in new_row and key not in ["user_value", "name"]:
                new_row[key] = value

        new_row["user_value"] = source_row.get("user_value", "")

        output_rows.append(new_row)

    return pd.DataFrame(output_rows)


def apply_template_order(metrics_csv_path, output_csv_path, report_type="adult_microbiome"):
    """
    Reorder the original lab metrics CSV according to ReportMetricTemplate order.

    This is Report Layout Engine v1.

    It preserves repeated rows for each metric because repeated rows are still
    required by the legacy PDF colour/range logic.
    """

    df = pd.read_csv(metrics_csv_path)

    if "name" not in df.columns:
        raise ValueError("Metrics CSV must contain a 'name' column.")

    metric_lookup = build_metric_lookup()
    template_list = build_template_list(report_type)
    template_metric_ids = {template.metric_definition_id for template in template_list}

    ordered_frames = []
    unmatched_frames = []

    grouped = df.groupby("name", sort=False)

    source_groups = {}

    for raw_metric_name, metric_df in grouped:
        metric_definition = metric_lookup.get(
            normalize_metric_name(raw_metric_name)
        )

        if not metric_definition:
            unmatched_frames.append(metric_df)
            continue

        if metric_definition.id not in template_metric_ids:
            unmatched_frames.append(metric_df)
            continue

        if metric_definition.id not in source_groups:
            source_groups[metric_definition.id] = metric_df.copy()

    for template in sorted(
        template_list,
        key=lambda template: (
            template.super_category_order,
            template.category_order,
            template.metric_order,
            template.display_order,
            template.id,
        ),
    ):
        metric_id = template.metric_definition_id

        metric_df = source_groups.get(metric_id)

        if metric_df is None:
            continue

        metric_df = metric_df.copy()

        metric_df = apply_legacy_range_template(
            metric_df=metric_df,
            template=template,
        )

        if template.category_title_override:
            metric_df["category_title"] = template.category_title_override

        if template.display_name_override:
            metric_df["name"] = template.display_name_override

        ordered_frames.append(metric_df)

    if unmatched_frames:
        ordered_frames.extend(unmatched_frames)

    if not ordered_frames:
        raise ValueError("No metric rows could be ordered for PDF output.")

    output_df = pd.concat(ordered_frames, ignore_index=True)
    output_df.to_csv(output_csv_path, index=False)

    return {
        "output_csv_path": output_csv_path,
        "ordered_metric_count": len(source_groups),
        "unmatched_group_count": len(unmatched_frames),
        "row_count": len(output_df),
    }