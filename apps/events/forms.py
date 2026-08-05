from django import forms
from django.core.exceptions import ValidationError
from apps.core.forms import ContactValidationMixin, HoneypotMixin
from .models import WaitlistEntry


class WaitlistForm(ContactValidationMixin, HoneypotMixin, forms.ModelForm):
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

    def clean_email(self):
        email = self.cleaned_data['email']
        if self.event and WaitlistEntry.objects.filter(event=self.event, email__iexact=email).exists():
            raise ValidationError('С этим email уже есть запись в лист ожидания')
        return email