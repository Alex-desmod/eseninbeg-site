from django.shortcuts import render
from django.views.generic import DetailView
from .models import Event, DistanceRecord


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