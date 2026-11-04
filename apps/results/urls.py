from django.urls import path

from .views import protocol

app_name = 'results'

urlpatterns = [
    path('<slug:slug>/<int:year>/', protocol, name='protocol'),
]
