from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render

from apps.events.models import Event
from .emails import send_registration_accepted
from .forms import RegistrationForm, available_distances


def registration_form(request, slug):
    event = get_object_or_404(Event, slug=slug, registration_mode='internal')

    if request.method == 'POST':
        form = RegistrationForm(request.POST, event=event)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = event
            try:
                registration.save()
            except IntegrityError:
                form.add_error(
                    'email',
                    'На эту дистанцию уже есть регистрация с этим email',
                )
                return render(
                    request,
                    'registration/partials/registration_form.html',
                    {'form': form, 'event': event},
                )

            send_registration_accepted(registration)

            return render(
                request,
                'registration/partials/registration_success.html',
                {'form': form, 'event': event, 'registration': registration},
            )
        return render(
            request,
            'registration/partials/registration_form.html',
            {'form': form, 'event': event},
        )

    if not available_distances(event):
        return render(
            request,
            'registration/partials/registration_full.html',
            {'event': event},
        )

    form = RegistrationForm(event=event)
    return render(
        request,
        'registration/partials/registration_form.html',
        {'form': form, 'event': event},
    )
