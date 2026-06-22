from django.conf import settings
from django.db import models


class ReportType(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)

    description = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ReportTemplate(models.Model):
    report_type = models.ForeignKey(
        ReportType,
        on_delete=models.CASCADE,
        related_name="templates"
    )

    name = models.CharField(max_length=150)
    version = models.CharField(max_length=50, default="v1")

    template_pdf = models.FileField(
        upload_to="report_templates/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["report_type", "name", "version"]
        unique_together = ["report_type", "name", "version"]

    def __str__(self):
        return f"{self.report_type.name} - {self.name} ({self.version})"


class Report(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]

    PROBIOTIC_COLOR_CHOICES = [
        ("green", "Green"),
        ("yellow", "Yellow"),
        ("red", "Red"),
    ]

    REVIEW_STATUS_CHOICES = [
        ("draft", "Draft"),
        ("pending_review", "Pending Review"),
        ("approved", "Approved"),
    ]

    report_type = models.ForeignKey(
        ReportType,
        on_delete=models.PROTECT,
        related_name="reports"
    )

    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.PROTECT,
        related_name="reports",
        blank=True,
        null=True
    )

    processed_metrics_csv = models.FileField(
        upload_to="uploads/processed_metrics/",
        blank=True,
        null=True
    )

    kit_id = models.CharField(max_length=100, db_index=True)
    patient_name = models.CharField(max_length=255)
    physician_name = models.CharField(max_length=255)
    sampling_date = models.DateField(blank=True, null=True)

    ENTEROTYPE_CHOICES = [
        ("Bacteroides", "Bacteroides"),
        ("Prevotella", "Prevotella"),
        ("Ruminococcaceae", "Ruminococcaceae"),
        ("Lachnospiraceae", "Lachnospiraceae"),
        ("Bifidobacterium", "Bifidobacterium"),
        ("Other", "Other"),
        ("Enterobacteriaceae", "Enterobacteriaceae"),
    ]
    enterotype = models.CharField(
        max_length=120,
        choices=ENTEROTYPE_CHOICES,
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT
    )

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="generated_reports"
    )

    review_status = models.CharField(
        max_length=30,
        choices=REVIEW_STATUS_CHOICES,
        default="pending_review",
    )

    probiotic_species_color = models.CharField(
        max_length=10,
        choices=PROBIOTIC_COLOR_CHOICES,
        blank=True,
        null=True,
        help_text="Manual FRX reviewer colour for Common Probiotic Species.",
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_reports",
    )

    reviewed_at = models.DateTimeField(null=True, blank=True)

    error_message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.kit_id} - {self.patient_name}"


class UploadedCSV(models.Model):
    report = models.OneToOneField(
        Report,
        on_delete=models.CASCADE,
        related_name="uploaded_csvs"
    )

    original_metrics_csv = models.FileField(
        upload_to="uploads/original_metrics/"
    )

    original_taxa_csv = models.FileField(
        upload_to="uploads/original_taxa/"
    )

    processed_metrics_csv = models.FileField(
        upload_to="uploads/processed_metrics/",
        blank=True,
        null=True
    )

    processed_taxa_csv = models.FileField(
        upload_to="uploads/processed_taxa/",
        blank=True,
        null=True
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CSV files for {self.report.kit_id}"


class GeneratedReport(models.Model):
    report = models.OneToOneField(
        Report,
        on_delete=models.CASCADE,
        related_name="generated_pdf"
    )

    pdf_file = models.FileField(upload_to="generated_reports/")

    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Generated PDF for {self.report.kit_id}"


class MissingTaxonDefinition(models.Model):
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name="missing_taxa"
    )

    taxonomy_name = models.CharField(max_length=255)
    detected_abundance = models.FloatField(blank=True, null=True)

    resolved = models.BooleanField(default=False)

    notes = models.TextField(
        blank=True,
        null=True,
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    reviewed_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["taxonomy_name"]
        unique_together = ["report", "taxonomy_name"]

    def __str__(self):
        return f"{self.taxonomy_name} missing for {self.report.kit_id}"



