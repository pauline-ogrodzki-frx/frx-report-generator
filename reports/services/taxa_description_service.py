import pandas as pd

from knowledge.models import TaxonDefinition
from reports.models import MissingTaxonDefinition

missing_taxa = []

def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def enrich_taxa_csv(taxa_csv_path, report, report_audience="adult"):
    df = pd.read_csv(taxa_csv_path)

    taxon_column = "taxonomy_name"
    description_column = "about_gut"

    if taxon_column not in df.columns:
        raise ValueError(
            f"Missing required column: {taxon_column}. Available columns: {list(df.columns)}"
        )

    if description_column not in df.columns:
        df[description_column] = ""

    matched_count = 0
    missing_count = 0

    for index, row in df.iterrows():
        organism_name = clean_text(row[taxon_column])

        if not organism_name:
            continue

        definition = TaxonDefinition.objects.filter(
            organism__iexact=organism_name,
            is_active=True,
        ).first()

        if definition:
            if report_audience == "infant":
                description = clean_text(definition.baby_description)
            else:
                description = clean_text(definition.frx_description)

            if description:
                df.at[index, description_column] = description
                matched_count += 1
            else:
                df.at[index, description_column] = ""
                missing_count += 1
                missing_taxa.append(organism_name)

                if report:
                    MissingTaxonDefinition.objects.get_or_create(
                        report=report,
                        taxonomy_name=organism_name,
                        defaults={
                            "detected_abundance": row.get("classified_relative_abundance") or None,
                            "resolved": False,
                        },
                    )

        else:
            df.at[index, description_column] = ""
            missing_count += 1
            missing_taxa.append(organism_name)

            if report:
                MissingTaxonDefinition.objects.get_or_create(
                    report=report,
                    taxonomy_name=organism_name,
                    defaults={
                        "detected_abundance": row.get("classified_relative_abundance") or None,
                        "resolved": False,
                    },
                )

    return {
        "dataframe": df,
        "matched_count": matched_count,
        "missing_count": missing_count,
        "missing_taxa": missing_taxa,
    }