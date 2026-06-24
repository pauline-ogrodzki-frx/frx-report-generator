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

