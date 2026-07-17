from django.core.cache import cache
from .models import SiteSettings


def site_settings(request):
    settings_obj = cache.get('site_settings')
    if not settings_obj:
        settings_obj = SiteSettings.objects.first()
        cache.set('site_settings', settings_obj, 3600)
    return {'site_settings': settings_obj}