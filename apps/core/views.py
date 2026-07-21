from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from apps.events.models import Event

# Create your views here.
class HomeView(ListView):
    model = Event
    template_name = 'core/home.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.order_by('home_order')


class PrivacyPolicyView(TemplateView):
    template_name = 'core/privacy.html'