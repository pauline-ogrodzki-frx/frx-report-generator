from django.db import models


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

    is_percentage = models.BooleanField(default=False)
    use_italics = models.BooleanField(default=False)
    comments = models.TextField(blank=True)

    is_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "metric_definition__metric_name"]

    def __str__(self):
        return f"{self.report_type} - {self.metric_definition.metric_name}"


