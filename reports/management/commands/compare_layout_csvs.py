from collections import Counter, defaultdict

import pandas as pd

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Compare expected and generated layout CSVs structurally."

    def add_arguments(self, parser):
        parser.add_argument("expected_csv", type=str)
        parser.add_argument("generated_csv", type=str)

    def handle(self, *args, **options):
        expected_csv = options["expected_csv"]
        generated_csv = options["generated_csv"]

        expected = pd.read_csv(expected_csv)
        generated = pd.read_csv(generated_csv)

        self.stdout.write("\n=== ROW COUNTS ===")
        self.stdout.write(f"Expected rows:  {len(expected)}")
        self.stdout.write(f"Generated rows: {len(generated)}")

        expected_pairs = list(
            zip(
                expected["name"].astype(str),
                expected["category_title"].astype(str),
            )
        )
        generated_pairs = list(
            zip(
                generated["name"].astype(str),
                generated["category_title"].astype(str),
            )
        )

        expected_counter = Counter(expected_pairs)
        generated_counter = Counter(generated_pairs)

        all_pairs = sorted(set(expected_counter) | set(generated_counter))

        self.stdout.write("\n=== ROW COUNT DIFFERENCES BY METRIC + CATEGORY ===")

        differences = []

        for pair in all_pairs:
            expected_count = expected_counter.get(pair, 0)
            generated_count = generated_counter.get(pair, 0)

            if expected_count != generated_count:
                differences.append(
                    {
                        "name": pair[0],
                        "category_title": pair[1],
                        "expected": expected_count,
                        "generated": generated_count,
                        "delta": generated_count - expected_count,
                    }
                )

        if not differences:
            self.stdout.write("No row-count differences by metric/category.")
        else:
            for item in differences:
                self.stdout.write(
                    f"{item['name']} | {item['category_title']} | "
                    f"expected={item['expected']} generated={item['generated']} "
                    f"delta={item['delta']}"
                )

        self.stdout.write("\n=== METRIC PRESENCE ===")

        expected_names = Counter(expected["name"].astype(str))
        generated_names = Counter(generated["name"].astype(str))

        expected_only = sorted(set(expected_names) - set(generated_names))
        generated_only = sorted(set(generated_names) - set(expected_names))

        self.stdout.write(f"Metrics only in expected: {len(expected_only)}")
        for name in expected_only:
            self.stdout.write(f" - {name}")

        self.stdout.write(f"Metrics only in generated: {len(generated_only)}")
        for name in generated_only:
            self.stdout.write(f" - {name}")

        self.stdout.write("\n=== ROW COUNT DIFFERENCES BY METRIC ===")

        metric_differences = []

        for name in sorted(set(expected_names) | set(generated_names)):
            expected_count = expected_names.get(name, 0)
            generated_count = generated_names.get(name, 0)

            if expected_count != generated_count:
                metric_differences.append(
                    (name, expected_count, generated_count, generated_count - expected_count)
                )

        if not metric_differences:
            self.stdout.write("No metric-level row-count differences.")
        else:
            for name, expected_count, generated_count, delta in metric_differences:
                self.stdout.write(
                    f"{name}: expected={expected_count} generated={generated_count} delta={delta}"
                )

        self.stdout.write("\n=== FIRST ORDER MISMATCHES ===")

        mismatch_count = 0

        for index, (expected_pair, generated_pair) in enumerate(
            zip(expected_pairs, generated_pairs)
        ):
            if expected_pair != generated_pair:
                self.stdout.write(
                    f"Row {index}: "
                    f"expected={expected_pair[0]} | {expected_pair[1]} ; "
                    f"generated={generated_pair[0]} | {generated_pair[1]}"
                )
                mismatch_count += 1

                if mismatch_count >= 25:
                    break

        if mismatch_count == 0 and len(expected) == len(generated):
            self.stdout.write("No order mismatches.")

        self.stdout.write("\n=== CATEGORY PLACEMENTS BY METRIC ===")

        expected_categories = defaultdict(set)
        generated_categories = defaultdict(set)

        for name, category in expected_pairs:
            expected_categories[name].add(category)

        for name, category in generated_pairs:
            generated_categories[name].add(category)

        placement_differences = []

        for name in sorted(set(expected_categories) | set(generated_categories)):
            expected_set = expected_categories.get(name, set())
            generated_set = generated_categories.get(name, set())

            if expected_set != generated_set:
                placement_differences.append((name, expected_set, generated_set))

        if not placement_differences:
            self.stdout.write("No category placement differences.")
        else:
            for name, expected_set, generated_set in placement_differences:
                self.stdout.write(
                    f"{name}: expected={sorted(expected_set)} generated={sorted(generated_set)}"
                )