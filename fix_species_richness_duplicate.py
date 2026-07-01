from knowledge.models import ReportMetricTemplate

updated = ReportMetricTemplate.objects.filter(
    id=5,
    report_type="adult_microbiome",
    metric_definition__metric_name__iexact="Species richness",
).update(
    is_active=False,
    include_in_pdf=False,
)

print(f"Deactivated {updated} duplicate Species richness template.")
