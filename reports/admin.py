from django.contrib import admin

from .models import (
    ReportType,
    ReportTemplate,
    Report,
    UploadedCSV,
    GeneratedReport,
    MissingTaxonDefinition,
)


@admin.register(ReportType)
class ReportTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "created_at",
    )

    search_fields = (
        "name",
    )


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "report_type",
        "version",
        "is_active",
    )

    list_filter = (
        "report_type",
        "is_active",
    )

    search_fields = (
        "name",
    )


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "kit_id",
        "patient_name",
        "physician_name",
        "report_type",
        "status",
        "created_at",
        "completed_at",
    )

    search_fields = (
        "kit_id",
        "patient_name",
        "physician_name",
    )

    list_filter = (
        "report_type",
        "status",
        "created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "completed_at",
        "error_message",
    )


@admin.register(UploadedCSV)
class UploadedCSVAdmin(admin.ModelAdmin):
    list_display = (
        "report",
        "original_metrics_csv",
        "original_taxa_csv",
        "processed_metrics_csv",
        "processed_taxa_csv",
    )


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = (
        "report",
        "generated_at",
    )


@admin.register(MissingTaxonDefinition)
class MissingTaxonDefinitionAdmin(admin.ModelAdmin):
    list_display = (
        "taxonomy_name",
        "report",
        "detected_abundance",
        "resolved",
        "reviewed_by",
        "reviewed_at",
        "created_at",
    )

    search_fields = (
        "taxonomy_name",
    )

    list_filter = (
        "resolved",
        "reviewed_at",
    )

    readonly_fields = (
        "created_at",
    )

