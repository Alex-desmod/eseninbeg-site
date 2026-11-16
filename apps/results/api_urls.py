from django.urls import path

from .views import api_results

app_name = 'results_api'

urlpatterns = [
    path('', api_results, name='list'),
]
