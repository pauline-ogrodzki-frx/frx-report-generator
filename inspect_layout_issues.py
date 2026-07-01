import pandas as pd

from knowledge.models import ReportMetricTemplate

expected = pd.read_csv("data/FRXEGR568_metrics_reordered.csv")
generated = pd.read_csv("/var/folders/l0/qqhy0ccd03s6yqfjtc3dtzs00000gn/T/layout_engine_ordered_metrics.csv")

metrics = [
    "Streptococcus thermophilus",
    "Lactobacillaceae",
    "Species richness",
]

for metric in metrics:
    print(f"\nEXPECTED: {metric}")
    print(expected[expected["name"] == metric][["name", "category_title"]].to_string())

    print(f"\nGENERATED: {metric}")
    print(generated[generated["name"] == metric][["name", "category_title"]].to_string())


print("\nSPECIES RICHNESS TEMPLATES")
for t in ReportMetricTemplate.objects.filter(
    report_type="adult_microbiome",
    metric_definition__metric_name__iexact="Species richness",
).select_related("metric_definition").order_by("id"):
    print(
        "id=", t.id,
        "metric=", t.metric_definition.metric_name,
        "category_title=", repr(t.category_title),
        "category_override=", repr(t.category_title_override),
        "super=", t.super_category_order,
        "category=", t.category_order,
        "metric_order=", t.metric_order,
        "active=", t.is_active,
        "include=", t.include_in_pdf,
        "rows=", len(t.legacy_range_template or []),
    )
