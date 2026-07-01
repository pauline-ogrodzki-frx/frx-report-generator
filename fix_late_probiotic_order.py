from knowledge.models import ReportMetricTemplate

updates = [
    ("Streptococcus thermophilus", 88),
    ("Lactobacillaceae", 93),
]

for metric_name, metric_order in updates:
    updated = ReportMetricTemplate.objects.filter(
        report_type="adult_microbiome",
        metric_definition__metric_name=metric_name,
    ).update(
        super_category_order=28,
        category_order=28,
        metric_order=metric_order,
        display_order=metric_order,
        is_active=True,
        include_in_pdf=True,
    )

    print(f"Updated {metric_name}: {updated} template(s).")
