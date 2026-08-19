from .models import Event


def nav_events(request):
    return {
        'nav_events': Event.objects.all()
    }
