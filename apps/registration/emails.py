import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from apps.core.models import SiteSettings

logger = logging.getLogger(__name__)


def send_registration_accepted(registration):
    """Notification right after the registration form is submitted.

    Only for paid events: for free events the first (and only) notification
    is send_payment_confirmed, sent after the admin confirms the participation."""
    if registration.amount is None or registration.amount <= 0:
        return
    subject = f'Заявка на "{registration.event.title}" принята'
    _send(
        registration,
        subject,
        'registration/emails/registration_accepted',
    )


def send_payment_confirmed(registration):
    """Notification after the admin confirmed the payment (bib number assigned)."""
    subject = f'Вы зарегистрированы на "{registration.event.title}" — номер {registration.bib_number}'
    _send(
        registration,
        subject,
        'registration/emails/payment_confirmed',
    )


def _send(registration, subject, template_base):
    if not settings.SEND_REGISTRATION_EMAILS:
        return

    event = registration.event
    context = {
        'registration': registration,
        'event': event,
        'contacts': SiteSettings.objects.first(),
        'base_url': settings.BASE_URL,
    }

    text_body = render_to_string(f'{template_base}.txt', context)
    html_body = render_to_string(f'{template_base}.html', context)

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[registration.email],
    )
    message.attach_alternative(html_body, 'text/html')
    try:
        message.send()
    except Exception:
        # An email failure must never break the registration flow itself
        logger.exception('Failed to send %s email to %s', template_base, registration.email)
