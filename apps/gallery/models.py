from django.core.exceptions import ValidationError
from django.db import models

from apps.events.models import Event


# Create your models here.
class MediaItem(models.Model):
    TYPE_CHOICES = [
        ('photo', 'Фото'),
        ('video', 'Видео'),
    ]
    MAX_PHOTOS_PER_EVENT = 32

    event = models.ForeignKey(Event, related_name='media_items', on_delete=models.CASCADE)
    media_type = models.CharField('Тип', max_length=10, choices=TYPE_CHOICES)
    image = models.ImageField(
        'Фото', upload_to='gallery/photo/', blank=True,
        help_text='Обязательно для типа "Фото"'
    )
    caption = models.CharField('Подпись', max_length=200, blank=True)
    video_embed_url = models.URLField(
        'Ссылка для встраивания видео', blank=True,
        help_text='Для типа "Видео". Например, embed-ссылка с vkvideo.ru или youTube'
    )
    order = models.SmallIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Медиафайл'
        verbose_name_plural = 'Галерея'

    def __str__(self):
        return f'{self.event.title} — {self.get_media_type_display()} #{self.pk}'

    def clean(self):
        if self.media_type == 'photo' and not self.image:
            raise ValidationError('Для типа "Фото" нужно загрузить изображение.')
        if self.media_type == 'video' and not self.video_embed_url:
            raise ValidationError('Для типа "Видео" нужна ссылка для встраивания.')

        if self.media_type == 'photo':
            photos_count = MediaItem.objects.filter(
                event=self.event, media_type='photo'
            ).exclude(pk=self.pk).count()

            if photos_count >= self.MAX_PHOTOS_PER_EVENT:
                raise ValidationError(
                    f'Достигнут лимит: не более {self.MAX_PHOTOS_PER_EVENT} фото на одно событие.'
                )

