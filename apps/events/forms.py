import re

from django import forms
from django.core.exceptions import ValidationError

from .models import WaitlistEntry

FULL_NAME_RE = re.compile(r"^[А-ЯЁа-яёA-Za-z\-\s']+$")


class WaitlistForm(forms.ModelForm):
    # Honeypot: невидимое обычным пользователям поле.
    # Простые боты заполняют все поля формы подряд — если это поле не пустое, считаем заявку спамом.
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    consent = forms.BooleanField(
        label='Согласие на обработку персональных данных',
        required=True,
        error_messages={'required': 'Нужно согласие на обработку персональных данных'},
    )

    class Meta:
        model = WaitlistEntry
        fields = ['full_name', 'phone', 'email']
        widgets = {
            'full_name': forms.TextInput(attrs={'autocomplete': 'name'}),
            'phone': forms.TextInput(attrs={'autocomplete': 'tel', 'inputmode': 'tel'}),
        }

    def __init__(self, *args, event=None, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)

    def clean_full_name(self):
        value = self.cleaned_data['full_name'].strip()
        if len(value.split()) < 2:
            raise ValidationError('Укажите фамилию и имя (минимум два слова)')
        if not FULL_NAME_RE.fullmatch(value):
            raise ValidationError('ФИО может содержать только буквы, пробелы и дефис')
        return value

    def clean_phone(self):
        value = self.cleaned_data['phone'].strip()
        digits = re.sub(r'\D', '', value)

        if digits.startswith('8') and len(digits) == 11:
            digits = '7' + digits[1:]

        if not (len(digits) == 11 and digits.startswith('7')):
            raise ValidationError('Введите номер телефона в формате +7 900 000-00-00')

        return f'+{digits}'

    def clean_email(self):
        email = self.cleaned_data['email']
        if self.event and WaitlistEntry.objects.filter(event=self.event, email__iexact=email).exists():
            raise ValidationError('С этим email уже есть запись в лист ожидания на это событие')
        return email

    def clean_website(self):
        value = self.cleaned_data.get('website')
        if value:
            raise ValidationError('Обнаружен спам')
        return value
