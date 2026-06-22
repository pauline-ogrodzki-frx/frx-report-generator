from pathlib import Path

import csv
import tempfile
import shutil
from io import TextIOWrapper

from knowledge.forms import TaxonDefinitionForm
from knowledge.models import TaxonDefinition

from django.db import models
from django.core.files import File
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Max
from django.urls import reverse
from django.http import HttpResponseRedirect, FileResponse, Http404


from .forms import ReportCreateForm, ReportReviewForm
from .models import Report, ReportType, UploadedCSV, MissingTaxonDefinition, GeneratedReport
from .services.taxa_description_service import enrich_taxa_csv
from .services.pdf_report_service import generate_pdf_with_existing_builder
from .services.metrics_processing_service import process_metrics_csv

@login_required
def platform_dashboard(request):
    total_reports = Report.objects.count()
    completed_reports = Report.objects.filter(
        status=Report.STATUS_COMPLETED,
    ).count()
    failed_reports = Report.objects.filter(
        status=Report.STATUS_FAILED,
    ).count()

    unresolved_taxa = MissingTaxonDefinition.objects.filter(
        resolved=False,
    ).count()

    recent_reports = (
        Report.objects
        .select_related("report_type")
        .order_by("-created_at")[:10]
    )

    return render(
        request,
        "reports/platform_dashboard.html",
        {
            "total_reports": total_reports,
            "completed_reports": completed_reports,
            "failed_reports": failed_reports,
            "unresolved_taxa": unresolved_taxa,
            "recent_reports": recent_reports,
        },
    )


@login_required
def create_report(request):
    if request.method == "POST":
        form = ReportCreateForm(request.POST, request.FILES)

        if form.is_valid():
            report_type, _ = ReportType.objects.update_or_create(
                name="Adult Gut Microbiome",
                defaults={
                    "slug": "adult-gut-microbiome",
                    "is_active": True,
                },
            )

            report = form.save(commit=False)
            report.sampling_date = form.cleaned_data["sampling_date"]
            report.report_type = report_type
            report.status = report.STATUS_PROCESSING
            report.generated_by = request.user
            report.save()

            uploaded_csv = UploadedCSV.objects.create(
                report=report,
                original_metrics_csv=request.FILES["metrics_csv"],
                original_taxa_csv=request.FILES["taxa_csv"],
            )

            try:
                original_metrics_csv_path = field_file_to_temp_path(
                    uploaded_csv.original_metrics_csv,
                    suffix=".csv",
                )

                processed_metrics_csv_path = process_metrics_csv(
                    metrics_csv_path=original_metrics_csv_path,
                    report=report,
                )

                taxa_csv_path = field_file_to_temp_path(
                    uploaded_csv.original_taxa_csv,
                    suffix=".csv",
                )

                enrichment_result = enrich_taxa_csv(
                    taxa_csv_path=taxa_csv_path,
                    report=report,
                    report_audience="adult",
                )

                safe_kit_id = report.kit_id.replace("/", "-").replace(" ", "_")

                enriched_taxa_path = (
                    Path(taxa_csv_path).parent
                    / f"{safe_kit_id}_processed_taxa_enriched.csv"
                )

                enrichment_result["dataframe"].to_csv(
                    enriched_taxa_path,
                    index=False,
                )

                with open(enriched_taxa_path, "rb") as enriched_file:
                    uploaded_csv.processed_taxa_csv.save(
                        enriched_taxa_path.name,
                        File(enriched_file),
                        save=True,
                    )

                generate_pdf_with_existing_builder(
                    report=report,
                    metrics_csv_path=processed_metrics_csv_path,
                    enriched_taxa_csv_path=enriched_taxa_path,
                )

                report.status = report.STATUS_COMPLETED
                report.completed_at = timezone.now()
                report.save()

                return redirect("report_success", report_id=report.id)

            except Exception as error:
                report.status = report.STATUS_FAILED
                report.error_message = str(error)
                report.save()

                return redirect("report_success", report_id=report.id)

    else:
        form = ReportCreateForm()

    return render(
        request,
        "reports/create_report.html",
        {
            "form": form,
        },
    )

def get_common_probiotic_species_rows(report):
    uploaded_csv = (
        UploadedCSV.objects
        .filter(report=report)
        .order_by("-id")
        .first()
    )

    if not uploaded_csv:
        return []

    metrics_file = uploaded_csv.original_metrics_csv

    if not metrics_file:
        return []

    rows = []

    with metrics_file.open("rb") as file:
        text_file = TextIOWrapper(file, encoding="utf-8")
        reader = csv.DictReader(text_file)

        for row in reader:
            category_title = row.get("category_title", "").strip()

            if category_title == "Common Probiotic Species":
                rows.append(row)

    return rows

@login_required
def review_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    probiotic_species_rows = get_common_probiotic_species_rows(report)

    if request.method == "POST":
        form = ReportReviewForm(request.POST, instance=report)

        if form.is_valid():
            reviewed_report = form.save(commit=False)
            reviewed_report.review_status = "approved"
            reviewed_report.reviewed_by = request.user
            reviewed_report.reviewed_at = timezone.now()
            reviewed_report.save()

            uploaded_csv = (
                UploadedCSV.objects
                .filter(report=report)
                .order_by("-id")
                .first()
            )

            if uploaded_csv and uploaded_csv.processed_taxa_csv:
                original_metrics_csv_path = field_file_to_temp_path(
                    uploaded_csv.original_metrics_csv,
                    suffix=".csv",
                )

                processed_metrics_csv_path = process_metrics_csv(
                    metrics_csv_path=original_metrics_csv_path,
                    report=reviewed_report,
                )

                processed_taxa_csv_path = field_file_to_temp_path(
                    uploaded_csv.processed_taxa_csv,
                    suffix=".csv",
                )

                generate_pdf_with_existing_builder(
                    report=reviewed_report,
                    metrics_csv_path=processed_metrics_csv_path,
                    enriched_taxa_csv_path=processed_taxa_csv_path,
                )

            messages.success(
                request,
                "Report reviewed, approved, and final PDF regenerated."
            )

            return redirect("report_detail", report_id=report.id)

    else:
        form = ReportReviewForm(instance=report)

    return render(
        request,
        "reports/review_report.html",
        {
            "report": report,
            "form": form,
            "probiotic_species_rows": probiotic_species_rows,
        },
    )

@login_required
def report_success(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    return render(
        request,
        "reports/report_success.html",
        {
            "report": report,
        },
    )


@login_required
def report_history(request):
    reports = (
        Report.objects
        .select_related("report_type", "generated_by")
        .prefetch_related("missing_taxa")
        .order_by("-created_at")
    )

    search_query = request.GET.get("q", "")
    status_filter = request.GET.get("status", "")

    if search_query:
        reports = reports.filter(
            models.Q(patient_name__icontains=search_query)
            | models.Q(kit_id__icontains=search_query)
            | models.Q(physician_name__icontains=search_query)
        )

    if status_filter:
        reports = reports.filter(status=status_filter)

    total_reports = reports.count()

    completed_reports = reports.filter(
        status=Report.STATUS_COMPLETED,
    ).count()

    failed_reports = reports.filter(
        status=Report.STATUS_FAILED,
    ).count()

    processing_reports = reports.filter(
        status=Report.STATUS_PROCESSING,
    ).count()

    draft_reports = reports.filter(
        status=Report.STATUS_DRAFT,
    ).count()

    return render(
        request,
        "reports/report_history.html",
        {
            "reports": reports,
            "total_reports": total_reports,
            "completed_reports": completed_reports,
            "failed_reports": failed_reports,
            "processing_reports": processing_reports,
            "draft_reports": draft_reports,
            "search_query": search_query,
            "status_filter": status_filter,
        },
    )


@login_required
def report_detail(request, report_id):
    report = get_object_or_404(
        Report.objects.select_related(
            "report_type",
            "generated_by",
        ),
        id=report_id,
    )

    return render(
        request,
        "reports/report_detail.html",
        {
            "report": report,
        },
    )


@login_required
def missing_taxa_dashboard(request):
    missing_taxa_summary = (
        MissingTaxonDefinition.objects
        .values("taxonomy_name")
        .annotate(
            report_count=Count("report", distinct=True),
            highest_abundance=Max("detected_abundance"),
            total_records=Count("id"),
            unresolved_count=Count(
                "id",
                filter=models.Q(resolved=False),
            ),
        )
        .order_by("-unresolved_count", "-report_count", "taxonomy_name")
    )

    return render(
        request,
        "reports/missing_taxa_dashboard.html",
        {
            "missing_taxa_summary": missing_taxa_summary,
        },
    )

@login_required
def missing_taxon_detail(request, taxonomy_name):
    missing_taxa = (
        MissingTaxonDefinition.objects
        .filter(taxonomy_name=taxonomy_name)
        .select_related("report", "report__report_type")
        .order_by("-detected_abundance")
    )

    return render(
        request,
        "reports/missing_taxon_detail.html",
        {
            "taxonomy_name": taxonomy_name,
            "missing_taxa": missing_taxa,
        },
    )


@login_required
def mark_missing_taxon_resolved(request, taxonomy_name):
    MissingTaxonDefinition.objects.filter(
        taxonomy_name=taxonomy_name,
    ).update(
        resolved=True,
        reviewed_by=request.user,
        reviewed_at=timezone.now(),
    )

    messages.success(
        request,
        f"{taxonomy_name} marked as resolved.",
    )

    return HttpResponseRedirect(
        reverse("missing_taxon_detail", args=[taxonomy_name])
    )

@login_required
def create_taxon_definition_from_missing(request, taxonomy_name):
    existing_definition = TaxonDefinition.objects.filter(
        organism=taxonomy_name,
    ).first()

    if request.method == "POST":
        form = TaxonDefinitionForm(
            request.POST,
            instance=existing_definition,
        )

        if form.is_valid():
            taxon_definition = form.save()

            MissingTaxonDefinition.objects.filter(
                taxonomy_name=taxon_definition.organism,
            ).update(
                resolved=True,
                reviewed_by=request.user,
                reviewed_at=timezone.now(),
            )

            messages.success(
                request,
                f"Taxon definition created for {taxon_definition.organism}.",
            )

            return redirect(
                "missing_taxon_detail",
                taxonomy_name=taxon_definition.organism,
            )

    else:
        if existing_definition:
            form = TaxonDefinitionForm(instance=existing_definition)
        else:
            form = TaxonDefinitionForm(
                initial={
                    "organism": taxonomy_name,
                    "is_active": True,
                }
            )

    return render(
        request,
        "reports/create_taxon_definition_from_missing.html",
        {
            "form": form,
            "taxonomy_name": taxonomy_name,
            "existing_definition": existing_definition,
        },
    )

@login_required
def download_generated_pdf(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    generated_report = (
        GeneratedReport.objects
        .filter(report=report)
        .order_by("-id")
        .first()
    )

    if not generated_report:
        raise Http404("Generated PDF not found.")

    return serve_field_file(
        generated_report.pdf_file,
        f"{report.kit_id}_FRX_Report.pdf",
    )


@login_required
def download_processed_taxa_csv(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    uploaded_csv = (
        UploadedCSV.objects
        .filter(report=report)
        .order_by("-id")
        .first()
    )

    if not uploaded_csv or not uploaded_csv.processed_taxa_csv:
        raise Http404("Processed taxa CSV not found.")

    return FileResponse(
        uploaded_csv.processed_taxa_csv.open("rb"),
        as_attachment=True,
        filename=f"{report.kit_id}_processed_taxa.csv",
    )

def serve_field_file(field_file, download_name):
    if not field_file:
        raise Http404("File not found.")

    if not default_storage.exists(field_file.name):
        raise Http404("File is missing from storage. It may have been removed during redeploy.")

    return FileResponse(
        default_storage.open(field_file.name, "rb"),
        as_attachment=True,
        filename=download_name,
    )

def field_file_to_temp_path(field_file, suffix=".csv"):
    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    )

    with field_file.open("rb") as source_file:
        shutil.copyfileobj(source_file, temp_file)

    temp_file.close()

    return temp_file.name

@login_required
def download_original_metrics_csv(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    uploaded_csv = UploadedCSV.objects.filter(report=report).order_by("-id").first()

    if not uploaded_csv:
        raise Http404("Uploaded CSV not found.")

    return serve_field_file(
        uploaded_csv.original_metrics_csv,
        f"{report.kit_id}_original_metrics.csv",
    )


@login_required
def download_original_taxa_csv(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    uploaded_csv = UploadedCSV.objects.filter(report=report).order_by("-id").first()

    if not uploaded_csv:
        raise Http404("Uploaded CSV not found.")

    return serve_field_file(
        uploaded_csv.original_taxa_csv,
        f"{report.kit_id}_original_taxa.csv",
    )