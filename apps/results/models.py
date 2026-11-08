from django.db import models
from apps.events.models import Distance

class ResultEntry(models.Model):
    GENDER_CHOICES = [
        ('male', 'мужчины'),
        ('female', 'женщины'),
    ]
    CAT_CHOICES = [
        ('F 16-17', 'Ж 16-17'),
        ('F 17', 'Ж 17'),
        ('F 18-34', 'Ж 18-34'),
        ('F 18-29', 'Ж 18-29'),
        ('F 30-34', 'Ж 30-34'),
        ('F 35-39', 'Ж 35-39'),
        ('F 40-44', 'Ж 40-44'),
        ('F 45-49', 'Ж 45-49'),
        ('F 50-54', 'Ж 50-54'),
        ('F 55-59', 'Ж 55-59'),
        ('F 60+', 'Ж 60+'),
        ('F 60-64', 'Ж 60-64'),
        ('F 65-69', 'Ж 65-69'),
        ('F 70+', 'Ж 70+'),
        ('M 16-17', 'М 16-17'),
        ('M 17', 'М 17'),
        ('M 18-34', 'М 18-34'),
        ('M 18-29', 'М 18-29'),
        ('M 30-34', 'М 30-34'),
        ('M 35-39', 'М 35-39'),
        ('M 40-44', 'М 40-44'),
        ('M 45-49', 'М 45-49'),
        ('M 50-54', 'М 50-54'),
        ('M 55-59', 'М 55-59'),
        ('M 60+', 'М 60+'),
        ('M 60-64', 'М 60-64'),
        ('M 65-69', 'М 65-69'),
        ('M 70+', 'М 70+'),
    ]
    STATUS_CHOICES = [
        ('DNF', 'DNF'),
        ('DSQ', 'DSQ'),
        ('DNS', 'DNS'),
    ]

    distance = models.ForeignKey(Distance, related_name='results', on_delete=models.CASCADE)
    date = models.DateField('Дата события', db_index=True)
    gender = models.CharField('Пол', choices=GENDER_CHOICES, max_length=8)
    category = models.CharField('Категория', choices=CAT_CHOICES, max_length=8, blank=True)
    place = models.PositiveSmallIntegerField('Место в абсолюте', null=True, blank=True)
    gender_place = models.PositiveSmallIntegerField('Место М/Ж', null=True, blank=True)
    category_place = models.PositiveSmallIntegerField('Место в категории', null=True, blank=True)
    bib_number = models.PositiveSmallIntegerField('Номер')
    surname = models.CharField('Фамилия', max_length=100)
    name = models.CharField('Имя', max_length=100)
    country = models.CharField('Страна', max_length=100, blank=True)
    city = models.CharField('Город', max_length=100, blank=True)
    club = models.CharField('Клуб', max_length=100, blank=True)
    chip_time = models.DurationField('Результат', null=True, blank=True)
    gun_time = models.DurationField('Абсолютный результат', null=True, blank=True)
    status = models.CharField('Статус', choices=STATUS_CHOICES, max_length=5, blank=True)

    class Meta:
        ordering = ['date', 'place']
        verbose_name = 'Результат'
        verbose_name_plural = 'Результаты'
        constraints = [
            models.UniqueConstraint(fields=['distance', 'date', 'place'], name='unique_place_per_distance_date'),
        ]
        indexes = [models.Index(fields=['distance', 'date', 'place'])]

    @property
    def full_name(self):
        return f'{self.surname} {self.name}'.strip()

    def __str__(self):
        return f'{self.date:%d.%m.%Y} · {self.distance} · {self.place}. {self.full_name}'
