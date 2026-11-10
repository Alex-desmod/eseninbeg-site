from django import template

register = template.Library()


@register.filter
def duration_hms(value):
    """timedelta → H:MM:SS"""
    if value is None or value == '':
        return ''
    total = int(value.total_seconds())
    hours, remainder = divmod(total, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours}:{minutes:02d}:{seconds:02d}'