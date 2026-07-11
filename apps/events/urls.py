from django.urls import path
from .views import EventDetailView

app_name = 'events'

urlpatterns = [
    path('<slug:slug>/', EventDetailView.as_view(), name='detail')
]