from django.db import models
from django.utils.text import slugify


# Create your models here.

class Event(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'предстоящее'),
        ('past', 'прошедшее')
    ]

    WEEKDAY_CHOICES = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    ]

    WEEKDAY_PHRASES = {
        0: 'Каждый понедельник',
        1: 'Каждый вторник',
        2: 'Каждую среду',
        3: 'Каждый четверг',
        4: 'Каждую пятницу',
        5: 'Каждую субботу',
        6: 'Каждое воскресенье',
    }

    title = models.CharField('Название', max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    date = models.DateField('Дата', blank=True, null=True)
    is_recurring = models.BooleanField('Периодическое событие', default=False)
    recurrence_weekday = models.PositiveSmallIntegerField(
        'День недели', choices=WEEKDAY_CHOICES, blank=True, null=True
    )
    recurrence_text = models.CharField(
        'Текст расписания (переопределение)',
        max_length=100,
        blank=True,
        help_text='Если пусто — сформируется автоматически, например "Каждую субботу". '
                  'Заполни вручную для нестандартных случаев ("Каждую 1-ю субботу месяца").'
    )
    location = models.CharField('Место', max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    description = models.TextField('Описание', blank=True)
    cover_image = models.ImageField(
        'Обложка',
        upload_to='events/covers/',
        help_text='~1000px по ширине, квадрат или 4/5, JPG/PNG'
    )
    home_banner = models.ImageField(
        'Баннер на главной',
        upload_to='events/banners/',
        help_text='~1900×300px, оставь место по краям, JPG/PNG',
        blank=True
    )
    bottom_image = models.ImageField(
        'Картинка внизу страницы',
        upload_to='events/covers/',
        help_text='~400px по ширине, PNG с прозрачным фоном',
        blank=True
    )
    home_order = models.PositiveSmallIntegerField('Порядок на главной', default=0)
    waitlist_enabled = models.BooleanField(
        'Лист ожидания',
        default=False,
        help_text='Показывать кнопку записи в лист ожидания на странице события'
    )
    registration_url = models.URLField('Ссылка на регистрацию', blank=True)
    results_url = models.URLField('Ссылка на результаты', blank=True)
    partners = models.ManyToManyField(
        'partners.Partner',
        related_name='events',
        blank=True,
        verbose_name='Партнёры'
    )

    class Meta:
        ordering = ['home_order', 'date']

    @property
    def schedule_display(self):
        if self.is_recurring:
            if self.recurrence_text:
                return self.recurrence_text
            if self.recurrence_weekday is not None:
                return self.WEEKDAY_PHRASES[self.recurrence_weekday]
        return ''

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
    route_map_image = models.ImageField(
        'Схема трассы',
        upload_to='events/routes/',
        help_text='~600px по ширине, JPG/PNG',
        blank=True
    )
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
    photo = models.ImageField(
        'Фото',
        upload_to='events/records/',
        help_text='~400px по ширине, 3/4, JPG/PNG',
        blank=True)

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
    start_map_image = models.ImageField(
        'Схема стартового городка',
        upload_to='events/routes/',
        help_text='~480px по ширине, JPG/PNG',
        blank=True
    )

    class Meta:
        verbose_name = 'Инфо о месте старта'
        verbose_name_plural = 'Инфо о месте старта'

    def __str__(self):
        return f'Как добраться: {self.event.title}'


class WaitlistEntry(models.Model):
    MAX_ENTRIES_PER_EVENT = 1000

    event = models.ForeignKey(Event, related_name='waitlist_entries', on_delete=models.CASCADE)
    full_name = models.CharField('ФИО', max_length=200)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email')
    created_at = models.DateTimeField('Дата записи', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Запись в лист ожидания'
        verbose_name_plural = 'Лист ожидания'
        constraints = [
            models.UniqueConstraint(fields=['event', 'email'], name='unique_waitlist_entry')
        ]

    def __str__(self):
        return f'{self.full_name} — {self.event.title}'

