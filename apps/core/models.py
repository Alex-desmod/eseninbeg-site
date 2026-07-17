from django.db import models

# Create your models here.
class SiteSettings(models.Model):
    email = models.EmailField('Почта зачинщиков', blank=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    tg_url = models.URLField('Telegram', blank=True)
    vk_url = models.URLField('VK', blank=True)

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return 'Настройки сайта'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass