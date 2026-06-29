import pandas as pd

from django.core.management.base import BaseCommand
from django.utils import timezone

from knowledge.models import (
    MetricDefinition,
    MetricSynonym,
    MetricReferenceRangeSet,
    MetricReferenceRangeRow,
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


class Command(BaseCommand):
    help = "Import baseline metric reference ranges from a known-good metrics CSV."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str)
        parser.add_argument(
            "--report-type",
            default="adult_microbiome",
            help="Report type slug. Default: adult_microbiome",
        )
        parser.add_argument(
            "--source",
            default="Baseline lab metrics CSV",
            help="Source label for this baseline import.",
        )

    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        report_type = options["report_type"]
        source = options["source"]

        df = pd.read_csv(csv_path)

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
                f"CSV missing required columns: {sorted(missing_columns)}"
            )

        metric_lookup = build_metric_lookup()

        imported_count = 0
        skipped_count = 0
        unresolved_metrics = []

        for raw_metric_name, metric_df in df.groupby("name", sort=False):
            lookup_key = normalize_metric_name(raw_metric_name)
            metric_definition = metric_lookup.get(lookup_key)

            if not metric_definition:
                unresolved_metrics.append(raw_metric_name)
                skipped_count += 1
                continue

            existing_active = MetricReferenceRangeSet.objects.filter(
                metric_definition=metric_definition,
                report_type=report_type,
                is_active=True,
            ).first()

            if existing_active:
                skipped_count += 1
                continue

            range_set = MetricReferenceRangeSet.objects.create(
                metric_definition=metric_definition,
                report_type=report_type,
                version=1,
                source=source,
                is_active=True,
                approved_at=timezone.now(),
            )

            for index, row in enumerate(metric_df.to_dict("records")):
                MetricReferenceRangeRow.objects.create(
                    range_set=range_set,
                    row_order=index,
                    category_title=str(row.get("category_title", "") or "").strip(),
                    range_lower=None if pd.isna(row.get("range_lower")) else float(row.get("range_lower")),
                    range_upper=None if pd.isna(row.get("range_upper")) else float(row.get("range_upper")),
                    evaluation=str(row.get("evaluation", "") or "").strip(),
                    range_color=str(row.get("range_color", "") or "").strip(),
                )

            imported_count += 1

        self.stdout.write(self.style.SUCCESS("Reference range baseline import complete."))
        self.stdout.write(f"Imported: {imported_count}")
        self.stdout.write(f"Skipped: {skipped_count}")

        if unresolved_metrics:
            self.stdout.write(self.style.WARNING("Unresolved metrics:"))
            for metric_name in unresolved_metrics:
                self.stdout.write(f"- {metric_name}")