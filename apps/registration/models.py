from django.db import models
from django.core.exceptions import ValidationError
from ..events.models import Event, Distance


class Registration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'ожидает оплаты'),
        ('paid', 'оплачена'),
        ('cancelled', 'отменена'),
    ]

    GENDER_CHOICES = [
        ('male', 'мужской'),
        ('female', 'женский'),
    ]
    event = models.ForeignKey(
        Event,
        related_name='registrations',
        on_delete=models.CASCADE,
        verbose_name='Событие'
    )
    distance = models.ForeignKey(
        Distance,
        related_name='registrations',
        on_delete=models.CASCADE,
        verbose_name='Дистанция'
    )
    status = models.CharField(
        'Статус',
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    full_name = models.CharField('ФИО атлета', max_length=200)
    birth_date = models.DateField('Дата рождения')
    gender = models.CharField('Пол', max_length=10, choices=GENDER_CHOICES)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('E-mail')
    city = models.CharField('Город', max_length=100)
    club = models.CharField('Клуб', max_length=100, blank=True)
    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True)
    amount = models.DecimalField('Сумма к оплате', max_digits=8, decimal_places=2)
    bib_number = models.PositiveIntegerField(
        'Номер участника',
        null=True,
        blank=True,
        help_text='Назначается администратором после подтверждения оплаты'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Регистрация'
        verbose_name_plural = 'Регистрации'
        constraints = [
            models.UniqueConstraint(fields=['distance', 'email'], name='unique_registration_per_distance')
        ]

    @classmethod
    def count_active_for(cls, distance):
        return cls.objects.filter(distance=distance).exclude(status='cancelled').count()

    def clean(self):
        if self.distance_id and self.distance.event_id != self.event_id:
            raise ValidationError('Дистанция не относится к выбранному событию')
        if self.distance_id and self.pk is None:
            max_registrations = self.distance.max_registrations
            if max_registrations is not None and self.count_active_for(self.distance) >= max_registrations:
                raise ValidationError('Достигнут лимит регистраций на эту дистанцию')

    def save(self, *args, **kwargs):
        if self.amount is None and self.distance_id and self.distance.price is not None:
            self.amount = self.distance.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.full_name} — {self.distance} ({self.get_status_display()})'
