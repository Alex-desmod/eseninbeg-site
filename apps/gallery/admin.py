from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path

from .models import MediaItem
from .forms import BulkPhotoUploadForm


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ['event', 'media_type', 'caption', 'order']
    list_editable = ['order']
    list_filter = ['event', 'media_type']
    list_display_links = ['media_type']
    change_list_template = 'admin/gallery/mediaitem/change_list.html'

    def get_urls(self):
        custom_urls = [
            path('bulk-upload/', self.admin_site.admin_view(self.bulk_upload), name='gallery_mediaitem_bulk_upload'),
        ]
        return custom_urls + super().get_urls()

    def bulk_upload(self, request):
        if request.method == 'POST':
            form = BulkPhotoUploadForm(request.POST, request.FILES)
            if form.is_valid():
                event = form.cleaned_data['event']
                images = form.cleaned_data['images']

                existing_count = MediaItem.objects.filter(event=event, media_type='photo').count()
                created = 0

                for image in images:
                    if existing_count + created >= MediaItem.MAX_PHOTOS_PER_EVENT:
                        messages.warning(
                            request,
                            f'Достигнут лимит {MediaItem.MAX_PHOTOS_PER_EVENT} фото на событие — '
                            f'загружено только {created} из {len(images)} файлов.'
                        )
                        break
                    MediaItem.objects.create(event=event, media_type='photo', image=image)
                    created += 1
                else:
                    messages.success(request, f'Успешно загружено фото: {created}')

                return redirect('admin:gallery_mediaitem_changelist')
        else:
            form = BulkPhotoUploadForm()

        context = dict(
            self.admin_site.each_context(request),
            form=form,
            title='Массовая загрузка фото',
        )
        return render(request, 'admin/gallery/bulk_upload_form.html', context)