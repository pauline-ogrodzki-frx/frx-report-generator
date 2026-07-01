import pandas as pd

from knowledge.models import (
    MetricDefinition,
    MetricSynonym,
    ReportMetricTemplate,
)


def normalize(value):
    return (
        str(value or "")
        .strip()
        .lower()
        .replace("–", "-")
        .replace("—", "-")
    )


metric_lookup = {}

for metric in MetricDefinition.objects.all():
    metric_lookup[normalize(metric.metric_name)] = metric

for synonym in MetricSynonym.objects.select_related("metric_definition"):
    metric_lookup[normalize(synonym.synonym)] = synonym.metric_definition


df = pd.read_csv("data/FRXEGR568_metrics_reordered.csv")

placements = []
seen = set()

for _, row in df.iterrows():
    metric_name = str(row.get("name", "")).strip()
    category_title = str(row.get("category_title", "")).strip()

    placement_key = (metric_name, category_title)

    if placement_key in seen:
        continue

    seen.add(placement_key)
    placements.append(placement_key)


updated = 0
missing_metric_definitions = []
missing_template_placements = []

for placement_order, (metric_name, category_title) in enumerate(placements, start=1):
    metric = metric_lookup.get(normalize(metric_name))

    if not metric:
        missing_metric_definitions.append((metric_name, category_title))
        continue

    templates = (
        ReportMetricTemplate.objects
        .filter(
            report_type="adult_microbiome",
            metric_definition=metric,
            is_active=True,
            include_in_pdf=True,
        )
        .order_by("id")
    )

    selected_template = None

    for template in templates:
        effective_category = (
            template.category_title_override
            or template.category_title
            or ""
        ).strip()

        if effective_category == category_title:
            selected_template = template
            break

    if selected_template is None:
        missing_template_placements.append((metric_name, category_title))
        continue

    selected_template.super_category_order = placement_order
    selected_template.category_order = placement_order
    selected_template.metric_order = placement_order
    selected_template.display_order = placement_order

    if selected_template.category_title != category_title:
        selected_template.category_title_override = category_title

    selected_template.save()
    updated += 1


print(f"Unique placements found: {len(placements)}")
print(f"Updated template placements: {updated}")
print(f"Missing metric definitions: {len(missing_metric_definitions)}")
print(f"Missing template placements: {len(missing_template_placements)}")

if missing_metric_definitions:
    print("\nMISSING METRIC DEFINITIONS")
    for item in missing_metric_definitions:
        print(item)

if missing_template_placements:
    print("\nMISSING TEMPLATE PLACEMENTS")
    for item in missing_template_placements:
        print(item)
