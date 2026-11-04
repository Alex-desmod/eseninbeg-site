from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .forms import ResultConfirmImportForm, ResultImportForm
from .models import ResultEntry
from .resources import ResultEntryResource


@admin.register(ResultEntry)
class ResultEntryAdmin(ImportExportModelAdmin):
    resource_classes = [ResultEntryResource]
    import_form_class = ResultImportForm
    confirm_form_class = ResultConfirmImportForm

    list_display = [
        'place', 'bib_number', 'full_name', 'distance', 'date', 'gender',
        'category', 'chip_time', 'gun_time', 'status',
    ]
    list_filter = ['date', 'gender', 'status', 'distance__event']
    search_fields = ['surname', 'name', 'city', 'club']
    list_select_related = ['distance', 'distance__event']
    ordering = ['-date', 'place']

    @admin.display(description='ФИО', ordering='surname')
    def full_name(self, obj):
        return obj.full_name

    def get_import_data_kwargs(self, request, form, **kwargs):
        """Pass the chosen distance and date to the resource on both import steps."""
        data = super().get_import_data_kwargs(request=request, **kwargs)
        data['distance'] = form.cleaned_data['distance']
        data['date'] = form.cleaned_data['date']
        return data

    def get_confirm_form_initial(self, request, import_form):
        """Carry the distance and date over to the confirm step."""
        initial = super().get_confirm_form_initial(request, import_form)
        if import_form is not None:
            initial['distance'] = import_form.cleaned_data['distance'].pk
            initial['date'] = import_form.cleaned_data['date'].isoformat()
        return initial
