from django.urls import path
from .views import registration_form

app_name = 'registration'

urlpatterns = [
    path('<slug:slug>/', registration_form, name='form'),
]
