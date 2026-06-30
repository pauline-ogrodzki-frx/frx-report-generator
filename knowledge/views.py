from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import TaxonDefinition, MetricReferenceRangeChange
from .services.reference_range_approval_service import (
    approve_reference_range_change,
    ignore_reference_range_change,
)


@login_required
def knowledge_dashboard(request):
    total_taxa = TaxonDefinition.objects.count()

    taxa_with_frx_description = (
        TaxonDefinition.objects
        .exclude(frx_description__isnull=True)
        .exclude(frx_description="")
        .count()
    )

    taxa_missing_frx_description = (
        TaxonDefinition.objects
        .filter(frx_description__isnull=True)
        .count()
    ) + (
        TaxonDefinition.objects
        .filter(frx_description="")
        .count()
    )

    recently_updated = (
        TaxonDefinition.objects
        .order_by("-updated_at")[:25]
    )

    return render(
        request,
        "knowledge/dashboard.html",
        {
            "total_taxa": total_taxa,
            "taxa_with_frx_description": taxa_with_frx_description,
            "taxa_missing_frx_description": taxa_missing_frx_description,
            "recently_updated": recently_updated,
        },
    )


@staff_member_required
@require_POST
def approve_reference_range_change_view(request, change_id):
    change = get_object_or_404(
        MetricReferenceRangeChange,
        id=change_id,
    )

    try:
        approve_reference_range_change(
            change=change,
            user=request.user,
            note=request.POST.get("notes", ""),
        )
        messages.success(
            request,
            "Reference range change approved. A new active reference range version was created.",
        )
    except Exception as exc:
        messages.error(
            request,
            f"Could not approve reference range change: {exc}",
        )

    return redirect("/reports/reference-range-changes/")


@staff_member_required
@require_POST
def ignore_reference_range_change_view(request, change_id):
    change = get_object_or_404(
        MetricReferenceRangeChange,
        id=change_id,
    )

    ignore_reference_range_change(
        change=change,
        user=request.user,
        note=request.POST.get("notes", ""),
    )

    messages.success(
        request,
        "Reference range change ignored.",
    )

    return redirect("/reports/reference-range-changes/")