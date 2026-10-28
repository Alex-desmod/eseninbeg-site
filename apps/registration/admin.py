from import_export import resources
from import_export.admin import ExportMixin
from django import forms
from django.contrib import admin
from .models import Registration


class RegistrationForm(forms.ModelForm):
    """Validates bib number uniqueness at the form level so the admin shows a field
    error instead of a 500 from the DB constraint."""

    class Meta:
        model = Registration
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        bib_number = cleaned_data.get('bib_number')
        event = cleaned_data.get('event') or self.instance.event
        if bib_number is not None and event is not None:
            duplicate = Registration.objects.filter(
                event=event,
                bib_number=bib_number,
            ).exclude(pk=self.instance.pk)
            if duplicate.exists():
                self.add_error(
                    'bib_number',
                    'Этот номер участника уже используется в этом событии',
                )
        return cleaned_data


class RegistrationResource(resources.ModelResource):
    class Meta:
        model = Registration


@admin.register(Registration)
class RegistrationAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = RegistrationResource
    form = RegistrationForm
    list_display = [
        'full_name', 'event', 'distance', 'status', 'gender',
        'birth_date', 'email', 'phone', 'amount', 'bib_number', 'created_at'
    ]
    list_filter = ['event', 'distance', 'status', 'gender']
    list_editable = ['status', 'bib_number']
    search_fields = ['surname', 'name', 'patronymic', 'email', 'phone', 'city', 'club']
    readonly_fields = ['created_at']

    @admin.display(description='ФИО атлета', ordering='surname')
    def full_name(self, obj):
        return obj.full_name

    def get_changelist_form(self, request, **kwargs):
        """Changelist editing must use the same validating form."""
        return RegistrationForm

