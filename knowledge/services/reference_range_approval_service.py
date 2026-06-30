from django.db import transaction
from django.utils import timezone

from knowledge.models import (
    MetricReferenceRangeSet,
    MetricReferenceRangeRow,
    MetricReferenceRangeChange,
)


@transaction.atomic
def ignore_reference_range_change(change, user=None, note=""):
    change.status = MetricReferenceRangeChange.STATUS_IGNORED
    change.reviewed_by = user
    change.reviewed_at = timezone.now()
    change.notes = note or ""
    change.save(update_fields=["status", "reviewed_by", "reviewed_at", "notes"])
    return change


@transaction.atomic
def approve_reference_range_change(change, user=None, note=""):
    if change.status != MetricReferenceRangeChange.STATUS_OPEN:
        return change

    active_set = (
        MetricReferenceRangeSet.objects
        .filter(
            metric_definition=change.metric_definition,
            report_type=change.report_type,
            is_active=True,
        )
        .order_by("-version")
        .first()
    )

    if not active_set:
        raise ValueError("No active reference range set found for this metric.")

    new_set = MetricReferenceRangeSet.objects.create(
        metric_definition=active_set.metric_definition,
        report_type=active_set.report_type,
        version=active_set.version + 1,
        source=f"Approved detected change ID {change.id}",
        is_active=True,
        approved_at=timezone.now(),
    )

    proposed_rows = change.proposed_rows or []

    if not proposed_rows:
        raise ValueError("No proposed reference range rows found for this change.")

    for row in proposed_rows:
        MetricReferenceRangeRow.objects.create(
            range_set=new_set,
            row_order=row.get("row_order", 0),
            category_title=row.get("category_title", ""),
            range_lower=row.get("range_lower"),
            range_upper=row.get("range_upper"),
            evaluation=row.get("evaluation", ""),
            range_color=row.get("range_color", ""),
        )

    active_set.is_active = False
    active_set.save(update_fields=["is_active"])

    change.status = MetricReferenceRangeChange.STATUS_APPROVED
    change.reviewed_by = user
    change.reviewed_at = timezone.now()
    change.notes = note or ""
    change.approved_signature = change.detected_signature
    change.approved_range_set = new_set
    change.save(
        update_fields=[
            "status",
            "reviewed_by",
            "reviewed_at",
            "notes",
            "approved_signature",
            "approved_range_set",
        ]
    )

    return change