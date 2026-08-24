from django import forms
from apps.events.models import Event


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return single_file_clean(data, initial)


class BulkPhotoUploadForm(forms.Form):
    event = forms.ModelChoiceField(queryset=Event.objects.all(), label='Событие')
    images = MultipleFileField(label='Фотографии')