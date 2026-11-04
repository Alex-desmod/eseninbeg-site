from django.http import Http404
from django.shortcuts import get_object_or_404, render

from apps.events.models import Event
from .models import ResultEntry


def protocol(request, slug, year):
    """Placeholder protocol page until the full results page is implemented."""
    event = get_object_or_404(Event, slug=slug)
    if not ResultEntry.objects.filter(distance__event=event, date__year=year).exists():
        raise Http404

    return render(
        request,
        'results/protocol_coming_soon.html',
        {'event': event, 'year': year},
    )
