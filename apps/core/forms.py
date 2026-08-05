import re
from django.core.exceptions import ValidationError

FULL_NAME_RE = re.compile(r"^[А-ЯЁа-яёA-Za-z\-\s']+$")


class ContactValidationMixin:
    """Name and phone validation for the forms with user contacts."""

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


class HoneypotMixin:
    """Hidden field as a catch for bots."""

    def clean_website(self):
        value = self.cleaned_data.get('website')
        if value:
            raise ValidationError('Обнаружен спам')
        return value