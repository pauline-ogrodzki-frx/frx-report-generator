from django import forms

from .models import Report


class ReportCreateForm(forms.ModelForm):
    metrics_csv = forms.FileField()
    taxa_csv = forms.FileField()

    sampling_date = forms.DateField(
        required=True,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            attrs={"type": "date"},
            format="%Y-%m-%d",
        ),
    )

    class Meta:
        model = Report
        fields = [
            "kit_id",
            "patient_name",
            "physician_name",
            "sampling_date",
            "enterotype",
        ]

class ReportReviewForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["probiotic_species_color"]
        labels = {
            "probiotic_species_color": "Common Probiotic Species colour",
        }
        help_texts = {
            "probiotic_species_color": "Select the FRX-reviewed colour for this report before final approval.",
        }

