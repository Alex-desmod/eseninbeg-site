from django import forms
from import_export.forms import ConfirmImportForm, ImportForm

from apps.events.models import Distance
from .models import ResultEntry


class ResultImportForm(ImportForm):
    """Import form: the admin picks the distance and the year of the protocol."""

    distance = forms.ModelChoiceField(
        queryset=Distance.objects.select_related('event').order_by('event__title', 'name'),
        label='Дистанция',
        help_text='Протокол будет импортирован для выбранной дистанции',
    )
    year = forms.IntegerField(
        label='Год',
        min_value=1900,
        max_value=2100,
        help_text='Год проведения забега',
    )

    def clean(self):
        cleaned_data = super().clean()
        distance = cleaned_data.get('distance')
        year = cleaned_data.get('year')
        if distance and year and ResultEntry.objects.filter(distance=distance, year=year).exists():
            raise forms.ValidationError(
                f'Результаты для дистанции «{distance}» за {year} год уже импортированы. '
                'Удалите их перед повторным импортом.'
            )
        return cleaned_data


class ResultConfirmImportForm(ConfirmImportForm):
    """Second (confirm) step: keeps the distance and year chosen on the first step."""

    distance = forms.ModelChoiceField(queryset=Distance.objects.all(), widget=forms.HiddenInput)
    year = forms.IntegerField(widget=forms.HiddenInput)
