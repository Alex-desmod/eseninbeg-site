from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Count, F, Q

from apps.core.forms import ContactValidationMixin, HoneypotMixin
from apps.events.models import Distance
from .models import Registration


class RegistrationForm(ContactValidationMixin, HoneypotMixin, forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    consent = forms.BooleanField(
        label='Согласие на обработку персональных данных',
        required=True,
        error_messages={'required': 'Нужно согласие на обработку персональных данных'},
    )

    class Meta:
        model = Registration
        fields = ['distance', 'surname', 'name', 'patronymic', 'birth_date', 'gender', 'phone', 'email', 'city', 'club']
        widgets = {
            'surname': forms.TextInput(attrs={'autocomplete': 'family-name'}),
            'name': forms.TextInput(attrs={'autocomplete': 'given-name'}),
            'patronymic': forms.TextInput(attrs={'autocomplete': 'additional-name'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'phone': forms.TextInput(attrs={'autocomplete': 'tel', 'inputmode': 'tel'}),
        }

    def __init__(self, *args, event=None, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)
        if event is not None:
            self.fields['distance'].queryset = available_distances(event)
        self.fields['distance'].empty_label = 'Выберите дистанцию'

    def clean_distance(self):
        distance = self.cleaned_data['distance']
        if self.event and distance.event_id != self.event.pk:
            raise ValidationError('Дистанция не относится к выбранному событию')
        return distance

    def clean_surname(self):
        return self.validate_name(self.cleaned_data['surname'], 'Фамилия')

    def clean_name(self):
        return self.validate_name(self.cleaned_data['name'], 'Имя')

    def clean_patronymic(self):
        return self.validate_name(self.cleaned_data['patronymic'], 'Отчество')

    def clean(self):
        cleaned_data = super().clean()
        if self.event:
            self.instance.event = self.event
        surname = cleaned_data.get('surname') or ''
        name = cleaned_data.get('name') or ''
        patronymic = cleaned_data.get('patronymic') or ''
        birth_date = cleaned_data.get('birth_date')

        if self.event and surname and name and birth_date:
            duplicate = Registration.objects.filter(
                event=self.event,
                surname__iexact=surname,
                name__iexact=name,
                birth_date=birth_date,
            ).exclude(status='cancelled')
            # Compare patronymics, treating a missing value as the empty string
            if patronymic:
                duplicate = duplicate.filter(patronymic__iexact=patronymic)
            else:
                duplicate = duplicate.filter(Q(patronymic='') | Q(patronymic__isnull=True))
            if self.instance.pk:
                duplicate = duplicate.exclude(pk=self.instance.pk)
            if duplicate.exists():
                raise ValidationError(
                    'Спортсмен с такими ФИО и датой рождения уже зарегистрирован на это событие'
                )
        return cleaned_data


def available_distances(event):
    """Distances of the event that still have free slots (no limit or limit not reached)."""
    return Distance.objects.filter(event=event).annotate(
        active_registrations=Count(
            'registrations',
            filter=~Q(registrations__status='cancelled'),
        )
    ).filter(
        Q(max_registrations__isnull=True)
        | Q(active_registrations__lt=F('max_registrations'))
    )
