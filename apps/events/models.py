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