from django.db import models

# Create your models here.
class Partner(models.Model):
    name = models.CharField('Название', max_length=200)
    logo = models.ImageField('Лого', upload_to='partners/logos')
    website_url = models.URLField('Ссылка', blank=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)
    is_global = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']
        verbose_name = 'Партнёр'
        verbose_name_plural = 'Партнёры'

    def __str__(self):
        return self.name