from knowledge.models import ReportMetricTemplate

for t in ReportMetricTemplate.objects.filter(
    report_type="adult_microbiome",
    is_active=True,
    include_in_pdf=True,
    metric_order__gte=15,
    metric_order__lte=35,
).select_related("metric_definition").order_by(
    "super_category_order",
    "category_order",
    "metric_order",
    "display_order",
    "id",
):
    print(
        "id=", t.id,
        "metric=", t.metric_definition.metric_name,
        "category_title=", repr(t.category_title),
        "category_override=", repr(t.category_title_override),
        "super=", t.super_category_order,
        "category=", t.category_order,
        "metric_order=", t.metric_order,
        "display_order=", t.display_order,
        "rows=", len(t.legacy_range_template or []),
    )
