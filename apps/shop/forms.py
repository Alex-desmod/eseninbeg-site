from django import forms
from apps.core.forms import ContactValidationMixin, HoneypotMixin
from .models import Order


class OrderForm(ContactValidationMixin, HoneypotMixin, forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    consent = forms.BooleanField(
        label='Согласие на обработку персональных данных',
        required=True,
        error_messages={'required': 'Нужно согласие на обработку персональных данных'},
    )

    class Meta:
        model = Order
        fields = ['full_name', 'phone', 'email', 'comment']
        widgets = {
            'full_name': forms.TextInput(attrs={'autocomplete': 'name'}),
            'phone': forms.TextInput(attrs={'autocomplete': 'tel', 'inputmode': 'tel'}),
        }