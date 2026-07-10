from django.db import models
from django.utils.text import slugify


# Create your models here.

class Event(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'предстоящее'),
        ('past', 'прошедшее')
    ]

    title = models.CharField('Название', max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    date = models.DateField('Дата')
    location = models.CharField('Место', max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    description = models.TextField('Описание', blank=True)
    cover_image = models.ImageField('Обложка', upload_to='events/covers')
    registration_url = models.URLField('Ссылка на регистрацию', blank=True)
    results_url = models.URLField('Ссылка на результаты', blank=True)

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Distance(models.Model):
    event = models.ForeignKey(Event, related_name='distances', on_delete=models.CASCADE)
    name = models.CharField('Название', max_length=100)
    length_km = models.DecimalField(max_digits=5, decimal_places=2)
    start_time = models.TimeField(null=True, blank=True)
    route_map_image = models.ImageField('Схема трассы', upload_to='events/routes', blank=True)
    gpx_file = models.FileField('GPX трек', upload_to='events/gpx', blank=True)

    def __str__(self):
        return f'{self.event.title} - {self.name}'


class DistanceRecord(models.Model):
    GENDER_CHOICES = [
        ('male', 'мужчины'),
        ('female', 'женщины'),
    ]

    distance = models.ForeignKey(Distance, related_name='records', on_delete=models.CASCADE)
    gender = models.CharField('Категория', choices=GENDER_CHOICES, max_length=10)
    athlete = models.CharField('Имя спортсмена', max_length=100)
    result_time = models.DurationField('Результат')
    date = models.DateField('Дата')
    photo = models.ImageField('Фото', upload_to='events/records', blank=True)

    class Meta:
        unique_together = [('distance', 'gender')]  # one record for gender
        verbose_name = 'Рекорд дистанции'
        verbose_name_plural = 'Рекорды дистанции'

    def __str__(self):
        return f'{self.distance} - {self.get_gender_display()}: {self.athlete} ({self.result_time})'


class ScheduleItem(models.Model):
    event = models.ForeignKey(Event, related_name='schedule_items', on_delete=models.CASCADE)
    time = models.TimeField('Время')
    title = models.CharField('Событие в программе', max_length=200)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Пункт программы'
        verbose_name_plural = 'Программа'

    def __str__(self):
        return f'{self.event.title} - {self.time} {self.title}'


class BibPickupInfo(models.Model):
    event = models.OneToOneField(Event, related_name='bib_pickup', on_delete=models.CASCADE)
    description = models.TextField('Инфо о выдаче номеров', blank=True)

    class Meta:
        verbose_name = 'Выдача номеров'
        verbose_name_plural = 'Выдача номеров'

    def __str__(self):
        return f'Выдача номеров: {self.event.title}'


class VenueInfo(models.Model):
    event = models.OneToOneField(Event, related_name='venue', on_delete=models.CASCADE)
    address = models.CharField('Адрес', max_length=300)
    latitude = models.DecimalField('Широта', max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField('Долгота', max_digits=9, decimal_places=6, blank=True, null=True)
    directions_text = models.TextField('Как добраться', blank=True)
    parking_info = models.TextField('Парковка', blank=True)

    class Meta:
        verbose_name = 'Инфо о месте старта'
        verbose_name_plural = 'Инфо о месте старта'

    def __str__(self):
        return f'Как добраться: {self.event.title}'

