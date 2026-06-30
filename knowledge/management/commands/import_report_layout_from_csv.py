import csv
from collections import OrderedDict
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand

from knowledge.models import (
    MetricDefinition,
    MetricSynonym,
    ReportMetricTemplate,
)


def normalize_metric_name(value):
    return (
        (value or "")
        .strip()
        .lower()
        .replace("–", "-")
        .replace("—", "-")
    )


def decimal_places_from_value(value):
    if value in (None, ""):
        return None

    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None

    exponent = decimal_value.as_tuple().exponent

    if exponent >= 0:
        return 0

    return abs(exponent)


class Command(BaseCommand):
    help = "Import report layout ordering and legacy range templates from a known-good reordered metrics CSV."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str)
        parser.add_argument(
            "--report-type",
            type=str,
            default="adult-gut-microbiome",
        )

    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        report_type = options["report_type"]

        metric_lookup = {}

        for metric in MetricDefinition.objects.all():
            metric_lookup[normalize_metric_name(metric.metric_name)] = metric

        for synonym in MetricSynonym.objects.select_related("metric_definition"):
            metric_lookup[normalize_metric_name(synonym.synonym)] = synonym.metric_definition

        grouped_rows = OrderedDict()
        unresolved_metrics = []

        with open(csv_path, newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)

            for row_index, row in enumerate(reader):
                raw_name = row.get("name", "")
                lookup_key = normalize_metric_name(raw_name)
                metric_definition = metric_lookup.get(lookup_key)

                if not metric_definition:
                    unresolved_metrics.append(raw_name)
                    continue

                metric_id = metric_definition.id

                if metric_id not in grouped_rows:
                    grouped_rows[metric_id] = {
                        "metric_definition": metric_definition,
                        "first_row_index": row_index,
                        "rows": [],
                    }

                grouped_rows[metric_id]["rows"].append(
                    {
                        "row_order": len(grouped_rows[metric_id]["rows"]),
                        "name": row.get("name", ""),
                        "category_title": row.get("category_title", ""),
                        "user_value": row.get("user_value", ""),
                        "range_lower": row.get("range_lower", ""),
                        "range_upper": row.get("range_upper", ""),
                        "evaluation": row.get("evaluation", ""),
                        "range_color": row.get("range_color", ""),
                    }
                )

        updated_count = 0
        missing_template_count = 0

        category_order_lookup = OrderedDict()

        for group_index, group in enumerate(grouped_rows.values(), start=1):
            metric_definition = group["metric_definition"]
            rows = group["rows"]

            first_row = rows[0]
            category_title = first_row.get("category_title", "")

            if category_title not in category_order_lookup:
                category_order_lookup[category_title] = len(category_order_lookup) + 1

            template = (
                ReportMetricTemplate.objects
                .filter(
                    metric_definition=metric_definition,
                    report_type=report_type,
                )
                .first()
            )

            if not template:
                missing_template_count += 1
                continue

            decimal_candidates = [
                decimal_places_from_value(row.get("user_value"))
                for row in rows
            ]
            decimal_candidates = [
                value for value in decimal_candidates
                if value is not None
            ]

            inferred_decimal_places = (
                max(decimal_candidates)
                if decimal_candidates
                else None
            )

            template.super_category_order = category_order_lookup[category_title]
            template.category_order = category_order_lookup[category_title]
            template.metric_order = group_index
            template.display_order = group_index

            if category_title and category_title != template.category_title:
                template.category_title_override = category_title

            template.legacy_range_template = rows

            if inferred_decimal_places is not None:
                template.decimal_places = inferred_decimal_places

            template.include_in_pdf = True
            template.preserve_repeated_rows = True

            template.save()

            updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported layout for {updated_count} metrics."
            )
        )

        self.stdout.write(
            f"Missing templates: {missing_template_count}"
        )

        if unresolved_metrics:
            unique_unresolved = sorted(set(unresolved_metrics))
            self.stdout.write(
                self.style.WARNING(
                    f"Unresolved metrics: {len(unique_unresolved)}"
                )
            )

            for metric_name in unique_unresolved[:50]:
                self.stdout.write(f" - {metric_name}")
                