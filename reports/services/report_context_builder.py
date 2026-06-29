from reports.models import UploadedCSV

from knowledge.models import (
    EnterotypeDefinition,
    ReportMetricTemplate,
    ReportSection,
)
from reports.services.metrics.template_ordered_processor import (
    build_ordered_metric_context,
)


def build_report_context(report):
    """
    Build a structured report context for one Report instance.

    This does not replace the legacy PDF engine yet.
    It creates the foundation for Report Engine v2.
    """

    report_type_key = "adult_microbiome"

    metric_context = None

    uploaded_csv = UploadedCSV.objects.filter(report=report).first()

    if uploaded_csv and uploaded_csv.original_metrics_csv:
        metric_context = build_ordered_metric_context(
            input_csv_path=uploaded_csv.original_metrics_csv.path,
            report=report,
            report_type=report_type_key,
            record_missing=False,
        )

    sections = (
        ReportSection.objects
        .filter(report_type=report_type_key, is_active=True)
        .prefetch_related("metrics__metric_definition")
        .order_by("display_order", "section_name")
    )

    metric_templates = (
        ReportMetricTemplate.objects
        .filter(report_type=report_type_key, is_active=True)
        .select_related("metric_definition", "section")
        .order_by("display_order")
    )

    enterotype_definition = None

    if report.enterotype:
        enterotype_definition = (
            EnterotypeDefinition.objects
            .filter(
                report_type=report_type_key,
                name=report.enterotype,
                is_active=True,
            )
            .first()
        )

    context = {
        "report": {
            "id": report.id,
            "kit_id": report.kit_id,
            "patient_name": report.patient_name,
            "physician_name": report.physician_name,
            "sampling_date": report.sampling_date,
            "enterotype": report.enterotype,
            "status": report.status,
        },
        "metrics": metric_context,
        "enterotype": {
            "name": (
                enterotype_definition.name
                if enterotype_definition
                else report.enterotype
            ),
            "display_name": (
                enterotype_definition.display_name
                if enterotype_definition
                else report.enterotype
            ),
            "description": (
                enterotype_definition.description
                if enterotype_definition
                else ""
            ),
        } if report.enterotype else None,
        "sections": [],
    }

    templates_by_section = {}

    for template in metric_templates:
        templates_by_section.setdefault(template.section_id, []).append(template)

    for section in sections:
        context["sections"].append({
            "id": section.id,
            "name": section.section_name,
            "super_category": section.super_category,
            "display_order": section.display_order,
            "metrics": [
                {
                    "metric_name": template.metric_definition.metric_name,
                    "display_name": template.metric_definition.display_name,
                    "category": template.metric_definition.category,
                    "category_title": template.category_title,
                    "display_order": template.display_order,
                    "is_percentage": template.is_percentage,
                    "use_italics": template.use_italics,
                    "comments": template.comments,
                    "is_required": template.is_required,
                }
                for template in templates_by_section.get(section.id, [])
            ],
        })

    return context