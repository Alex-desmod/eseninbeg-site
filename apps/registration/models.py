from django.db import IntegrityError, models, transaction
from django.db.models import Q
from decimal import Decimal

from django.core.exceptions import ValidationError
from ..events.models import Event, Distance


class Registration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'ожидает оплаты'),
        ('paid', 'оплачена'),
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
    surname = models.CharField('Фамилия', max_length=100)
    name = models.CharField('Имя', max_length=100)
    patronymic = models.CharField('Отчество', max_length=100, blank=True)
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
        help_text='Назначается автоматически после подтверждения оплаты. '
                  'Можно изменить вручную; номера должны быть уникальны в рамках события'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Регистрация'
        verbose_name_plural = 'Регистрации'
        constraints = [
            models.UniqueConstraint(fields=['distance', 'email'], name='unique_registration_per_distance'),
            models.UniqueConstraint(
                fields=['event', 'bib_number'],
                condition=Q(bib_number__isnull=False),
                name='unique_bib_number_per_event',
            ),
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
        if self.amount is None and self.distance_id:
            self.amount = self.distance.price if self.distance.price is not None else Decimal('0.00')

        payment_confirmed = False
        if (
            self.bib_number is None
            and self.status == 'paid'
            and self.distance_id
        ):
            was_paid = self.__class__.objects.filter(pk=self.pk, status='paid').exists()
            payment_confirmed = not was_paid

        if payment_confirmed:
            # The assigned number must actually be persisted
            update_fields = kwargs.get('update_fields')
            if update_fields is not None and 'bib_number' not in update_fields:
                kwargs = dict(kwargs, update_fields=[*update_fields, 'bib_number'])

        for attempt in range(3):
            try:
                with transaction.atomic():
                    if payment_confirmed:
                        self.assign_bib_number()
                    super().save(*args, **kwargs)
                break
            except IntegrityError as e:
                if not payment_confirmed:
                    # A manually set number collided with an existing one;
                    # surface a proper validation error instead of a 500.
                    if self._is_bib_number_conflict(e):
                        raise ValidationError('Этот номер участника уже используется в этом событии')
                    raise
                # A concurrent payment confirmation assigned the same number;
                # pick the next free one and try again.
                if attempt == 2:
                    raise
                self.bib_number = None

    @staticmethod
    def _is_bib_number_conflict(error):
        text = str(error)
        return 'unique_bib_number_per_event' in text or 'bib_number' in text

    def assign_bib_number(self):
        """Assign the next free bib number for the event, starting from the distance's start number."""
        if self.bib_number is not None or not self.event_id:
            return self.bib_number
        used = set(
            Registration.objects.filter(
                event_id=self.event_id,
                bib_number__isnull=False,
            ).exclude(pk=self.pk).values_list('bib_number', flat=True)
        )
        number = self.distance.bib_start_number
        while number in used:
            number += 1
        self.bib_number = number
        return number

    @property
    def full_name(self):
        """'Фамилия Имя Отчество' for display."""
        return ' '.join(part for part in (self.surname, self.name, self.patronymic) if part)

    def __str__(self):
        return f'{self.full_name} — {self.distance} ({self.get_status_display()})'
