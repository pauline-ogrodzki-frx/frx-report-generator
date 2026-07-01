from knowledge.models import ReportMetricTemplate

templates = (
    ReportMetricTemplate.objects
    .filter(
        report_type="adult_microbiome",
        metric_definition__metric_name="Bifidobacterium",
        super_category_order=7,
        category_order=7,
        metric_order=20,
    )
    .order_by("id")
)

keep = templates.first()

if keep:
    templates.exclude(id=keep.id).update(
        is_active=False,
        include_in_pdf=False,
    )
    print(f"Kept Bifidobacterium template id={keep.id}; deactivated duplicates.")
else:
    print("No matching duplicate Bifidobacterium templates found.")
