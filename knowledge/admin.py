from django.contrib import admin

from .models import TaxonDefinition, MetricDefinition


@admin.register(TaxonDefinition)
class TaxonDefinitionAdmin(admin.ModelAdmin):
    list_display = (
        "organism",
        "phylum",
        "is_active",
        "updated_at",
    )

    fields = (
        "organism",
        "phylum",
        "associations",
        "frx_description",
        "baby_description",
        "is_active",
    )

    search_fields = (
        "organism",
        "phylum",
        "associations",
        "frx_description",
        "baby_description",
    )

    list_filter = (
        "phylum",
        "is_active",
    )


@admin.register(MetricDefinition)
class MetricDefinitionAdmin(admin.ModelAdmin):
    list_display = (
        "metric_name",
        "display_name",
        "category",
        "source_system",
        "is_active",
        "created_at",
    )

    search_fields = (
        "metric_name",
        "display_name",
        "category",
    )

    list_filter = (
        "source_system",
        "category",
        "is_active",
    )