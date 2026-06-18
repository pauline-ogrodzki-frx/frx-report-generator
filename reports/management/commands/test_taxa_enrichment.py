from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand

from reports.services.taxa_description_service import (
    enrich_taxa_csv,
)


class Command(BaseCommand):
    help = "Test taxa enrichment using FRX knowledge base"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path",
            type=str,
        )

    def handle(self, *args, **options):
        csv_path = options["csv_path"]

        result = enrich_taxa_csv(
            taxa_csv_path=csv_path,
            report=None,
            report_audience="adult",
        )

        df = result["dataframe"]

        output_path = (
            Path(csv_path).parent
            / f"{Path(csv_path).stem}_enriched.csv"
        )

        df.to_csv(
            output_path,
            index=False,
        )

        top20_df = df.copy()

        top20_df["classified_relative_abundance"] = pd.to_numeric(
            top20_df["classified_relative_abundance"],
            errors="coerce",
        )

        top20_df = top20_df.sort_values(
            by="classified_relative_abundance",
            ascending=False,
        ).head(20)

        missing_top20_df = top20_df[
            top20_df["about_gut"].fillna("").astype(str).str.strip() == ""
        ]

        missing_output_path = (
            Path(csv_path).parent
            / f"{Path(csv_path).stem}_top20_missing_definitions.csv"
        )

        missing_top20_df[
            [
                "taxonomy_name",
                "classified_relative_abundance",
                "taxonomy_category",
                "category_gut",
            ]
        ].to_csv(
            missing_output_path,
            index=False,
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS("Enrichment complete")
        )

        self.stdout.write(
            f"Matched: {result['matched_count']}"
        )

        self.stdout.write(
            f"Missing overall: {result['missing_count']}"
        )

        self.stdout.write(
            f"Missing in top 20: {len(missing_top20_df)}"
        )

        self.stdout.write(
            f"Output: {output_path}"
        )

        self.stdout.write(
            f"Top 20 missing definitions file: {missing_output_path}"
        )