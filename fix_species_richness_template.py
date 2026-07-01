from knowledge.models import ReportMetricTemplate

updated = (
    ReportMetricTemplate.objects
    .filter(
        report_type="adult_microbiome",
        metric_definition__metric_name="Species richness",
        category_title_override="Microbiome Diversity",
    )
    .update(
        is_active=False,
        include_in_pdf=False,
    )
)

print(f"Deactivated {updated} old Species richness template(s).")
