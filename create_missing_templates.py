from knowledge.models import MetricDefinition, ReportMetricTemplate, ReportSection

report_type = "adult_microbiome"

section, _ = ReportSection.objects.get_or_create(
    report_type=report_type,
    section_name="Adult Gut Microbiome",
    defaults={
        "display_order": 0,
        "super_category": "Adult Gut Microbiome",
        "is_active": True,
    },
)

missing_metrics = [
    ("Proteobacteria / Actinobacteriota ratio", "Gut Ratio"),
    ("Methane production capacity", "Methane Production"),
    ("Indole-3-propionic acid", "Protein Breakdown Capacity"),
    ("Trimethylamine", "Protein Breakdown Capacity"),
    ("Ammonia", "Protein Breakdown Capacity"),
    ("Branched Chain Amino Acids", "Protein Breakdown Capacity"),
    ("Oxalate degradation", "Oxalate Degradation Capacity"),
]

created = 0

for metric_name, category_title in missing_metrics:
    metric = MetricDefinition.objects.get(metric_name=metric_name)

    _, was_created = ReportMetricTemplate.objects.get_or_create(
        report_type=report_type,
        metric_definition=metric,
        defaults={
            "section": section,
            "category_title": category_title,
            "display_order": 9999,
            "is_active": True,
            "include_in_pdf": True,
            "preserve_repeated_rows": True,
        },
    )

    if was_created:
        created += 1

print(f"Created {created} ReportMetricTemplate records.")
