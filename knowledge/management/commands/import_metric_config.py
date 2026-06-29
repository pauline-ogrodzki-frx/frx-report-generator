import json
from pathlib import Path

from django.core.management.base import BaseCommand

from knowledge.models import MetricDefinition


def to_bool(value):
    return str(value).strip().upper() == "TRUE"


class Command(BaseCommand):
    help = "Import legacy config_fields.json into MetricDefinition."

    def add_arguments(self, parser):
        parser.add_argument(
            "json_path",
            type=str,
            help="Path to config_fields.json",
        )

    def handle(self, *args, **options):
        json_path = Path(options["json_path"])

        if not json_path.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {json_path}"))
            return

        data = json.loads(json_path.read_text())

        created = 0
        updated = 0
        skipped = 0

        for item in data:
            metric_name = (item.get("name") or "").strip()

            if not metric_name:
                skipped += 1
                continue

            obj, was_created = MetricDefinition.objects.update_or_create(
                metric_name=metric_name,
                defaults={
                    "display_name": metric_name,
                    "category": (item.get("category_title") or "").strip(),
                    "description": (item.get("Comments") or "").strip(),
                    "super_category": (item.get("Super category") or "").strip(),
                    "is_percentage": to_bool(item.get("Percentage")),
                    "use_italics": to_bool(item.get("Italics")),
                    "comments": (item.get("Comments") or "").strip(),
                    "source_system": "legacy_config_fields_json",
                    "is_active": True,
                },
            )

            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS("Metric config import complete."))
        self.stdout.write(f"Created: {created}")
        self.stdout.write(f"Updated: {updated}")
        self.stdout.write(f"Skipped: {skipped}")