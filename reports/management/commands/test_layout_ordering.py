import tempfile
from pathlib import Path

import pandas as pd

from django.core.management.base import BaseCommand

from reports.services.layout_engine.ordering import apply_template_order


class Command(BaseCommand):
    help = "Test template-driven metrics CSV ordering against a known-good reordered CSV."

    def add_arguments(self, parser):
        parser.add_argument("original_csv", type=str)
        parser.add_argument("expected_csv", type=str)
        parser.add_argument(
            "--report-type",
            type=str,
            default="adult_microbiome",
        )

    def handle(self, *args, **options):
        original_csv = options["original_csv"]
        expected_csv = options["expected_csv"]
        report_type = options["report_type"]

        output_path = Path(tempfile.gettempdir()) / "layout_engine_ordered_metrics.csv"

        result = apply_template_order(
            metrics_csv_path=original_csv,
            output_csv_path=output_path,
            report_type=report_type,
        )

        generated = pd.read_csv(output_path)
        expected = pd.read_csv(expected_csv)

        generated_names = generated["name"].tolist()
        expected_names = expected["name"].tolist()

        exact_order_match = generated_names == expected_names

        self.stdout.write(f"Generated file: {output_path}")
        self.stdout.write(f"Generated rows: {len(generated)}")
        self.stdout.write(f"Expected rows: {len(expected)}")
        self.stdout.write(f"Ordered metrics: {result['ordered_metric_count']}")
        self.stdout.write(f"Unmatched groups: {result['unmatched_group_count']}")
        self.stdout.write(f"Exact metric order match: {exact_order_match}")

        if not exact_order_match:
            self.stdout.write(self.style.WARNING("First mismatches:"))

            for index, (generated_name, expected_name) in enumerate(
                zip(generated_names, expected_names)
            ):
                if generated_name != expected_name:
                    self.stdout.write(
                        f"Row {index}: generated={generated_name} expected={expected_name}"
                    )

                    if index > 25:
                        break