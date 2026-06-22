import pandas as pd
from django.core.files.base import ContentFile
from io import StringIO

from reports.services.metric_ordering import LEGACY_METRIC_ORDER


def normalize_metric_name(name):
    if pd.isna(name):
        return ""
    return str(name).strip()


def process_metrics_csv(report):
    """
    Takes the uploaded lab metrics CSV, reorders rows by metric name,
    preserves unknown/new metrics at the end, and saves a processed metrics CSV.
    """

    if not report.metrics_csv:
        raise ValueError("No metrics CSV uploaded for this report.")

    with report.metrics_csv.open("rb") as f:
        df = pd.read_csv(f)

    if df.empty:
        raise ValueError("Uploaded metrics CSV is empty.")

    # Try to detect metric-name column
    possible_metric_columns = [
        "Metric",
        "metric",
        "Metric Name",
        "metric_name",
        "name",
        "Name",
    ]

    metric_col = None
    for col in possible_metric_columns:
        if col in df.columns:
            metric_col = col
            break

    if metric_col is None:
        raise ValueError(
            f"Could not identify metric-name column. Found columns: {list(df.columns)}"
        )

    df["_normalized_metric_name"] = df[metric_col].apply(normalize_metric_name)

    order_map = {
        metric_name: index
        for index, metric_name in enumerate(LEGACY_METRIC_ORDER)
    }

    df["_sort_order"] = df["_normalized_metric_name"].map(order_map)

    known_df = df[df["_sort_order"].notna()].copy()
    unknown_df = df[df["_sort_order"].isna()].copy()

    known_df = known_df.sort_values("_sort_order")
    unknown_df = unknown_df.sort_values("_normalized_metric_name")

    processed_df = pd.concat([known_df, unknown_df], ignore_index=True)

    processed_df = processed_df.drop(
        columns=["_normalized_metric_name", "_sort_order"],
        errors="ignore"
    )

    csv_buffer = StringIO()
    processed_df.to_csv(csv_buffer, index=False)

    filename = f"{report.kit_id}_processed_metrics.csv"

    report.processed_metrics_csv.save(
        filename,
        ContentFile(csv_buffer.getvalue().encode("utf-8")),
        save=True
    )

    return report.processed_metrics_csv