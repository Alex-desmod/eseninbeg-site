from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .forms import ResultConfirmImportForm, ResultImportForm
from .models import Checkpoint, ResultEntry, Split
from .resources import ResultEntryResource


class SplitInline(admin.TabularInline):
    model = Split
    extra = 0
    fields = ['checkpoint', 'time']
    ordering = ['checkpoint__order']

    def get_formset(self, request, obj=None, **kwargs):
        # Keep the parent result so the checkpoint list can be limited to its distance.
        request._split_parent_obj = obj
        return super().get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'checkpoint':
            parent = getattr(request, '_split_parent_obj', None)
            if parent is not None:
                kwargs['queryset'] = Checkpoint.objects.filter(
                    distance=parent.distance
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Checkpoint)
class CheckpointAdmin(admin.ModelAdmin):
    list_display = ['name', 'length_km', 'distance', 'order']
    list_filter = ['distance__event', 'distance']
    search_fields = ['name', 'distance__name']
    list_select_related = ['distance', 'distance__event']
    ordering = ['distance', 'order']


@admin.register(ResultEntry)
class ResultEntryAdmin(ImportExportModelAdmin):
    resource_classes = [ResultEntryResource]
    import_form_class = ResultImportForm
    confirm_form_class = ResultConfirmImportForm
    inlines = [SplitInline]

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
