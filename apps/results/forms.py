from django import forms
from import_export.forms import ConfirmImportForm, ImportForm

from apps.events.models import Distance
from .models import ResultEntry


class ResultImportForm(ImportForm):
    """Import form: the admin picks the distance and the date of the protocol."""

    distance = forms.ModelChoiceField(
        queryset=Distance.objects.select_related('event').order_by('event__title', 'name'),
        label='Дистанция',
        help_text='Протокол будет импортирован для выбранной дистанции',
    )
    date = forms.DateField(
        label='Дата события',
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        help_text='Дата проведения забега',
    )

    def clean(self):
        cleaned_data = super().clean()
        distance = cleaned_data.get('distance')
        date = cleaned_data.get('date')
        if distance and date and ResultEntry.objects.filter(distance=distance, date=date).exists():
            raise forms.ValidationError(
                f'Результаты для дистанции «{distance}» за {date:%d.%m.%Y} уже импортированы. '
                'Удалите их перед повторным импортом.'
            )
        return cleaned_data


class ResultConfirmImportForm(ConfirmImportForm):
    """Second (confirm) step: keeps the distance and date chosen on the first step."""

    distance = forms.ModelChoiceField(queryset=Distance.objects.all(), widget=forms.HiddenInput)
    date = forms.DateField(widget=forms.HiddenInput, input_formats=['%Y-%m-%d'])
