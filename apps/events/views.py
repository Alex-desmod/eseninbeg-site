from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView
from .models import Event, DistanceRecord, WaitlistEntry
from .forms import WaitlistForm


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
