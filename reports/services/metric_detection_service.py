import pandas as pd

from knowledge.models import MetricDefinition
from reports.models import MissingMetricDefinition


def detect_missing_metrics(metrics_csv_path, report):
    df = pd.read_csv(metrics_csv_path)

    if "name" not in df.columns:
        raise ValueError(
            "Metrics CSV must contain a 'name' column to detect missing metrics."
        )

    metric_names = (
        df["name"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )

    known_metric_names = set(
        MetricDefinition.objects.filter(
            is_active=True,
        ).values_list(
            "metric_name",
            flat=True,
        )
    )

    missing_metrics = []

    for metric_name in metric_names:
        if metric_name not in known_metric_names:
            row = df[df["name"].astype(str).str.strip() == metric_name].iloc[0]
            category_title = str(row.get("category_title", "")).strip()

            missing_metric, created = MissingMetricDefinition.objects.get_or_create(
                report=report,
                metric_name=metric_name,
                defaults={
                    "category_title": category_title,
                    "resolved": False,
                },
            )

            if created:
                missing_metrics.append(missing_metric)

    return missing_metrics

    