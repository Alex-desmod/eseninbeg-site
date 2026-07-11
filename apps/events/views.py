from django.shortcuts import render
from django.views.generic import DetailView
from .models import Event

# Create your views here.
class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'