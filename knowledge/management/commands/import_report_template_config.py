import json
from pathlib import Path

from django.core.management.base import BaseCommand

from knowledge.models import (
    EnterotypeDefinition,
    MetricDefinition,
    ReportMetricTemplate,
    ReportSection,
)


def to_bool(value):
    return str(value).strip().upper() == "TRUE"


class Command(BaseCommand):
    help = "Import legacy config_fields.json into report template models."

    def add_arguments(self, parser):
        parser.add_argument("json_path", type=str)
        parser.add_argument(
            "--report-type",
            type=str,
            default="adult_microbiome",
        )

    def handle(self, *args, **options):
        json_path = Path(options["json_path"])
        report_type = options["report_type"]

        data = json.loads(json_path.read_text())

        sections = {}
        enterotypes_created = 0
        enterotypes_updated = 0
        metrics_created = 0
        metrics_updated = 0
        templates_created = 0
        templates_updated = 0

        for index, item in enumerate(data, start=1):
            name = (item.get("name") or "").strip()
            category_title = (item.get("category_title") or "").strip()
            super_category = (item.get("Super category") or "").strip()
            comments = (item.get("Comments") or "").strip()

            if not name:
                continue

            section_key = super_category or "Uncategorised"

            section, _ = ReportSection.objects.get_or_create(
                report_type=report_type,
                section_name=section_key,
                defaults={
                    "super_category": super_category,
                    "display_order": len(sections) + 1,
                    "is_active": True,
                },
            )
            sections[section_key] = section

            if category_title == "Enterotype":
                obj, created = EnterotypeDefinition.objects.update_or_create(
                    name=name,
                    report_type=report_type,
                    defaults={
                        "display_name": name,
                        "description": comments,
                        "is_active": True,
                    },
                )

                if created:
                    enterotypes_created += 1
                else:
                    enterotypes_updated += 1

                continue

            metric, created = MetricDefinition.objects.update_or_create(
                metric_name=name,
                defaults={
                    "display_name": name,
                    "category": category_title,
                    "description": comments,
                    "source_system": "legacy_config_fields_json",
                    "is_active": True,
                },
            )

            if created:
                metrics_created += 1
            else:
                metrics_updated += 1

            template, created = ReportMetricTemplate.objects.update_or_create(
                report_type=report_type,
                metric_definition=metric,
                section=section,
                category_title=category_title,
                defaults={
                    "display_order": index,
                    "is_percentage": to_bool(item.get("Percentage")),
                    "use_italics": to_bool(item.get("Italics")),
                    "comments": comments,
                    "is_required": False,
                    "is_active": True,
                },
            )

            if created:
                templates_created += 1
            else:
                templates_updated += 1

        self.stdout.write(self.style.SUCCESS("Report template import complete."))
        self.stdout.write(f"Enterotypes created: {enterotypes_created}")
        self.stdout.write(f"Enterotypes updated: {enterotypes_updated}")
        self.stdout.write(f"Metrics created: {metrics_created}")
        self.stdout.write(f"Metrics updated: {metrics_updated}")
        self.stdout.write(f"Templates created: {templates_created}")
        self.stdout.write(f"Templates updated: {templates_updated}")