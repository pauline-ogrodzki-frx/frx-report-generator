from django.db import models
from django.conf import settings


class TaxonDefinition(models.Model):
    organism = models.CharField(max_length=1000, unique=True)

    phylum = models.CharField(
        max_length=1000,
        blank=True,
        null=True
    )

    associations = models.TextField(
        blank=True,
        null=True
    )

    frx_description = models.TextField(
        blank=True,
        null=True
    )

    th_description = models.TextField(
        blank=True,
        null=True
    )

    baby_description = models.TextField(
        blank=True,
        null=True
    )

    microba_description = models.TextField(
        blank=True,
        null=True
    )

    unseenbio_description = models.TextField(
        blank=True,
        null=True
    )

    daytwo_description = models.TextField(
        blank=True,
        null=True
    )

    industry_description = models.TextField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["organism"]

    def __str__(self):
        return self.organism


class MetricDefinition(models.Model):
    metric_name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=255, blank=True)
    super_category = models.CharField(max_length=255, blank=True)
    is_percentage = models.BooleanField(default=False)
    use_italics = models.BooleanField(default=False)
    comments = models.TextField(blank=True)
    description = models.TextField(blank=True)
    source_system = models.CharField(
        max_length=255,
        default="Adult Gut Microbiome",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["metric_name"]

    def __str__(self):
        return self.metric_name


class MetricSynonym(models.Model):
    metric_definition = models.ForeignKey(
        MetricDefinition,
        on_delete=models.CASCADE,
        related_name="synonyms",
    )
    synonym = models.CharField(max_length=255)
    source_system = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["synonym"]
        constraints = [
            models.UniqueConstraint(
                fields=["metric_definition", "synonym"],
                name="unique_metric_synonym",
            )
        ]

    def __str__(self):
        return f"{self.synonym} → {self.metric_definition.metric_name}"

class TaxonSynonym(models.Model):
    taxon_definition = models.ForeignKey(
        TaxonDefinition,
        on_delete=models.CASCADE,
        related_name="synonyms",
    )
    synonym = models.CharField(max_length=255)
    source_system = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["synonym"]
        constraints = [
            models.UniqueConstraint(
                fields=["taxon_definition", "synonym"],
                name="unique_taxon_synonym",
            )
        ]

    def __str__(self):
        return f"{self.synonym} → {self.taxon_definition.organism}"




class EnterotypeDefinition(models.Model):
    name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    report_type = models.CharField(
        max_length=100,
        default="adult_microbiome",
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.display_name or self.name

class ReportSection(models.Model):
    report_type = models.CharField(
        max_length=100,
        default="adult_microbiome",
    )
    section_name = models.CharField(max_length=255)
    super_category = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "section_name"]
        unique_together = ("report_type", "section_name")

    def __str__(self):
        return f"{self.report_type} - {self.section_name}"

class ReportMetricTemplate(models.Model):
    report_type = models.CharField(
        max_length=100,
        default="adult_microbiome",
    )

    metric_definition = models.ForeignKey(
        MetricDefinition,
        on_delete=models.CASCADE,
        related_name="report_templates",
    )

    section = models.ForeignKey(
        ReportSection,
        on_delete=models.CASCADE,
        related_name="metrics",
    )

    category_title = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    # Report Layout Engine v2 fields
    super_category_order = models.PositiveIntegerField(default=0)
    category_order = models.PositiveIntegerField(default=0)
    metric_order = models.PositiveIntegerField(default=0)

    display_name_override = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    category_title_override = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    super_category_override = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    decimal_places = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    include_in_pdf = models.BooleanField(default=True)
    preserve_repeated_rows = models.BooleanField(default=True)

    legacy_range_template = models.JSONField(
        blank=True,
        null=True,
    )

    legacy_notes = models.TextField(blank=True, default="")

    is_percentage = models.BooleanField(default=False)
    use_italics = models.BooleanField(default=False)
    comments = models.TextField(blank=True)

    is_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = [
            "super_category_order",
            "category_order",
            "metric_order",
            "display_order",
            "metric_definition__metric_name",
        ]

    def __str__(self):
        return f"{self.report_type} - {self.metric_definition.metric_name}"
        

class MetricReferenceRangeSet(models.Model):
    metric_definition = models.ForeignKey(
        MetricDefinition,
        on_delete=models.CASCADE,
        related_name="reference_range_sets",
    )

    report_type = models.CharField(max_length=100, default="adult_microbiome")

    version = models.PositiveIntegerField(default=1)
    source = models.CharField(max_length=255, blank=True, default="Lab CSV import")

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["metric_definition__metric_name", "-version"]
        unique_together = [
            "metric_definition",
            "report_type",
            "version",
        ]

    def __str__(self):
        return (
            f"{self.metric_definition.metric_name} "
            f"{self.report_type} v{self.version}"
        )


class MetricReferenceRangeRow(models.Model):
    range_set = models.ForeignKey(
        MetricReferenceRangeSet,
        on_delete=models.CASCADE,
        related_name="rows",
    )

    row_order = models.PositiveIntegerField(default=0)

    category_title = models.CharField(max_length=255, blank=True, default="")
    range_lower = models.FloatField(blank=True, null=True)
    range_upper = models.FloatField(blank=True, null=True)
    evaluation = models.CharField(max_length=255, blank=True, default="")
    range_color = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        ordering = ["range_set", "row_order"]

    def __str__(self):
        return (
            f"{self.range_set.metric_definition.metric_name}: "
            f"{self.range_lower} - {self.range_upper} "
            f"{self.evaluation} {self.range_color}"
        )

class MetricReferenceRangeChange(models.Model):
    STATUS_OPEN = "open"
    STATUS_APPROVED = "approved"
    STATUS_IGNORED = "ignored"

    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_IGNORED, "Ignored"),
    ]

    metric_definition = models.ForeignKey(
        MetricDefinition,
        on_delete=models.CASCADE,
        related_name="reference_range_changes",
    )

    report_type = models.CharField(max_length=100, default="adult_microbiome")

    report = models.ForeignKey(
        "reports.Report",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="reference_range_changes",
    )

    detected_signature = models.TextField()
    approved_signature = models.TextField(blank=True, default="")
    
    proposed_rows = models.JSONField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )

    detected_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="reviewed_reference_range_changes",
    )

    approved_range_set = models.ForeignKey(
        "knowledge.MetricReferenceRangeSet",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="approved_changes",
    )

    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-detected_at"]

    def __str__(self):
        return (
            f"{self.metric_definition.metric_name} "
            f"{self.report_type} reference range change"
        )