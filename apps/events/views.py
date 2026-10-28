from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView
from .models import Event, DistanceRecord, WaitlistEntry
from .forms import WaitlistForm

PARTICIPANTS_PER_PAGE = 25


def get_participants_context(event, request):
    """Paid registrations of the event, paginated 25 per page and grouped
    by distance within the current page (for per-distance tables)."""
    registrations = (
        event.registrations
        .filter(status='paid')
        .select_related('distance')
        .order_by(
            'distance_id',
            F('bib_number').asc(nulls_last=True),
            'surname',
            'name',
        )
    )
    paginator = Paginator(registrations, PARTICIPANTS_PER_PAGE)
    page = paginator.get_page(request.GET.get('participants_page'))

    groups = []
    for registration in page.object_list:
        if not groups or groups[-1]['distance'] != registration.distance:
            groups.append({'distance': registration.distance, 'athletes': []})
        groups[-1]['athletes'].append(registration)

    return {
        'participants_page': page,
        'participant_groups': groups,
        'has_participants': page.paginator.count > 0,
    }


def participants_list(request, slug):
    event = get_object_or_404(Event, slug=slug)
    context = get_participants_context(event, request)
    context['event'] = event
    return render(request, 'events/partials/participants_list.html', context)


# Create your views here.
class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['records'] = DistanceRecord.objects.filter(
            distance__event=self.object
        ).select_related('distance')
        context.update(get_participants_context(self.object, self.request))
        return context


def waitlist_form(request, slug):
    event = get_object_or_404(Event, slug=slug, waitlist_enabled=True)

    if request.method == 'POST':
        form = WaitlistForm(request.POST, event=event)
        if form.is_valid():
            if event.waitlist_entries.count() >= WaitlistEntry.MAX_ENTRIES_PER_EVENT:
                return render(request, 'events/partials/waitlist_full.html', {'event': event})

            entry = form.save(commit=False)
            entry.event = event
            try:
                entry.save()
            except IntegrityError:
                form.add_error('email', 'С этим email уже есть запись в лист ожидания на это событие')
                return render(request, 'events/partials/waitlist_form.html', {'form': form, 'event': event})

            return render(request, 'events/partials/waitlist_success.html', {'event': event})
        return render(request, 'events/partials/waitlist_form.html', {'form': form, 'event': event})

    if event.waitlist_entries.count() >= WaitlistEntry.MAX_ENTRIES_PER_EVENT:
        return render(request, 'events/partials/waitlist_full.html', {'event': event})

    form = WaitlistForm(event=event)
    return render(request, 'events/partials/waitlist_form.html', {'form': form, 'event': event})
