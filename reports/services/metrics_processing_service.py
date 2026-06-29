import pandas as pd


METRIC_NAME_MAP = {
    "shannon diversity index": "Shannon diversity",
    "shannon diversity": "Shannon diversity",
    "host dna": "Host DNA",
    "firmicutes": "Firmicutes",
    "bacteroidota": "Bacteroidota",
    "prevotella": "Prevotella",
    "bacteroides": "Bacteroides",
    "phocaeicola dorei": "Phocaeicola dorei",
    "common probiotic species": "Common Probiotic Species",
}


def normalize_metric_name(value):
    if pd.isna(value):
        return value

    raw_value = str(value).strip()
    lookup_key = raw_value.lower()

    return METRIC_NAME_MAP.get(lookup_key, raw_value)


def process_metrics_csv(metrics_csv_path, report):
    """
    Creates a processed metrics CSV before PDF generation.

    This preserves the lab CSV structure expected by the legacy PDF builder,
    while normalizing only known legacy-required metric names.
    """

    df = pd.read_csv(metrics_csv_path)

    if "name" not in df.columns:
        raise ValueError(
            "Metrics CSV must contain a 'name' column. "
            f"Detected columns: {list(df.columns)}"
        )

    df["name"] = df["name"].apply(normalize_metric_name)

    safe_kit_id = str(report.kit_id or report.id).replace("/", "-").replace(" ", "_")

    processed_metrics_path = (
        pd.io.common.os.path.dirname(metrics_csv_path)
        + f"/{safe_kit_id}_processed_metrics.csv"
    )

    df.to_csv(processed_metrics_path, index=False)

    return processed_metrics_path