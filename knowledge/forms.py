from django import forms

from .models import TaxonDefinition, MetricDefinition


class TaxonDefinitionForm(forms.ModelForm):
    class Meta:
        model = TaxonDefinition

        fields = [
            "organism",
            "phylum",
            "associations",
            "frx_description",
            "th_description",
            "baby_description",
            "is_active",
        ]

        widgets = {
            "organism": forms.TextInput(attrs={"style": "width: 100%;"}),
            "phylum": forms.TextInput(attrs={"style": "width: 100%;"}),
            "associations": forms.Textarea(attrs={"rows": 4, "style": "width: 100%;"}),
            "frx_description": forms.Textarea(attrs={"rows": 8, "style": "width: 100%;"}),
            "th_description": forms.Textarea(attrs={"rows": 5, "style": "width: 100%;"}),
            "baby_description": forms.Textarea(attrs={"rows": 5, "style": "width: 100%;"}),
        }

class MetricDefinitionForm(forms.ModelForm):
    class Meta:
        model = MetricDefinition
        fields = (
            "metric_name",
            "display_name",
            "category",
            "description",
            "source_system",
            "is_active",
        )