from django.db import models


class TaxonDefinition(models.Model):
    organism = models.CharField(max_length=255, unique=True)

    phylum = models.CharField(
        max_length=255,
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
    category = models.CharField(max_length=255)

    metric = models.CharField(
        max_length=255,
        unique=True
    )

    general_description = models.TextField(
        blank=True,
        null=True
    )

    adult_description = models.TextField(
        blank=True,
        null=True
    )

    baby_description = models.TextField(
        blank=True,
        null=True
    )

    diet_lifestyle = models.TextField(
        blank=True,
        null=True
    )

    microba_description = models.TextField(
        blank=True,
        null=True
    )

    frx_description = models.TextField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "metric"]

    def __str__(self):
        return self.metric

