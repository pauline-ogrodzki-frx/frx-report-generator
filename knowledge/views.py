from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import TaxonDefinition


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