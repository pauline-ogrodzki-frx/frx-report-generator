from django.contrib import admin

from .models import TaxonDefinition, MetricDefinition, EnterotypeDefinition, ReportSection, ReportMetricTemplate


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

@admin.register(EnterotypeDefinition)
class EnterotypeDefinitionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "display_name",
        "report_type",
        "is_active",
        "created_at",
    )
    list_filter = ("report_type", "is_active")
    search_fields = ("name", "display_name", "description")


@admin.register(ReportSection)
class ReportSectionAdmin(admin.ModelAdmin):
    list_display = (
        "section_name",
        "super_category",
        "report_type",
        "display_order",
        "is_active",
    )
    list_filter = ("report_type", "is_active")
    search_fields = ("section_name", "super_category")
    ordering = ("report_type", "display_order")


@admin.register(ReportMetricTemplate)
class ReportMetricTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "metric_definition",
        "category_title",
        "section",
        "report_type",
        "display_order",
        "is_percentage",
        "use_italics",
        "is_required",
        "is_active",
    )
    list_filter = (
        "report_type",
        "section",
        "is_percentage",
        "use_italics",
        "is_required",
        "is_active",
    )
    search_fields = (
        "metric_definition__metric_name",
        "metric_definition__display_name",
        "category_title",
        "comments",
    )
    autocomplete_fields = ("metric_definition", "section")
    ordering = ("report_type", "display_order")

