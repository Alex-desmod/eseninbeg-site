from django.urls import path
from .views import EventDetailView, participants_list, waitlist_form

app_name = 'events'

urlpatterns = [
    path('<slug:slug>/participants/', participants_list, name='participants'),
    path('<slug:slug>/waitlist/', waitlist_form, name='waitlist'),
    path('<slug:slug>/', EventDetailView.as_view(), name='detail')
]