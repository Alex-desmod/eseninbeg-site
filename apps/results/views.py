from django.core.paginator import Paginator
from django.db.models import Case, Count, F, IntegerField, Prefetch, Value, When
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.dateparse import parse_date

from apps.events.models import Distance, Event
from .models import ResultEntry, Split

RESULTS_PER_PAGE = 50

GENDERS = {value for value, _ in ResultEntry.GENDER_CHOICES}
CATEGORY_LABELS = dict(ResultEntry.CAT_CHOICES)
STATUS_ORDER = {
    '': 0,
    'DNF': 1,
    'DSQ': 2,
    'DNS': 3,
}


def _order_results(queryset, place_field):
    """Order protocol entries by status, place and name."""
    status_order = Case(
        *[
            When(status=status, then=Value(order))
            for status, order in STATUS_ORDER.items()
        ],
        default=Value(len(STATUS_ORDER)),
        output_field=IntegerField(),
    )

    return queryset.annotate(
        position=F(place_field),
        status_order=status_order,
    ).order_by(
        'status_order',
        F('position').asc(nulls_last=True),
        'surname',
        'name',
        'bib_number',
    ).select_related('distance').prefetch_related(
        Prefetch(
            'splits',
            queryset=Split.objects.select_related('checkpoint').order_by(
                'checkpoint__order'
            ),
        )
    )


def _format_duration(value):
    """Format a timedelta as ``H:MM:SS`` (or ``None``)."""
    if value is None:
        return None
    total = int(value.total_seconds())
    hours, remainder = divmod(total, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours}:{minutes:02d}:{seconds:02d}'


def _duration_seconds(value):
    return int(value.total_seconds()) if value is not None else None


def _serialize_split(split):
    return {
        'checkpoint': split.checkpoint.name,
        'length_km': float(split.checkpoint.length_km),
        'order': split.checkpoint.order,
        'time': _format_duration(split.time),
        'time_seconds': _duration_seconds(split.time),
        'pace': split.pace,
    }


def _serialize_result(entry):
    return {
        'id': entry.pk,
        'place': entry.place,
        'gender_place': entry.gender_place,
        'category_place': entry.category_place,
        'position': entry.position,
        'bib_number': entry.bib_number,
        'surname': entry.surname,
        'name': entry.name,
        'full_name': entry.full_name,
        'gender': entry.gender,
        'gender_display': entry.get_gender_display(),
        'category': entry.category,
        'category_display': entry.get_category_display(),
        'country': entry.country,
        'city': entry.city,
        'club': entry.club,
        'chip_time': _format_duration(entry.chip_time),
        'chip_time_seconds': _duration_seconds(entry.chip_time),
        'gun_time': _format_duration(entry.gun_time),
        'gun_time_seconds': _duration_seconds(entry.gun_time),
        'chip_pace': entry.chip_pace,
        'gun_pace': entry.gun_pace,
        'status': entry.status,
        'splits': [
            _serialize_split(split)
            for split in entry.splits.all()
            if split.time is not None
        ],
    }


def protocol(request, slug, year):
    event = get_object_or_404(Event, slug=slug)
    event_results = ResultEntry.objects.filter(
        distance__event=event,
        date__year=year,
    )
    if not event_results.exists():
        raise Http404

    distances = list(
        Distance.objects.filter(event=event, results__date__year=year)
        .distinct()
        .order_by('pk')
    )

    distance_id = request.GET.get('distance')
    distance = next(
        (item for item in distances if str(item.pk) == distance_id),
        distances[0],
    )

    results = event_results.filter(distance=distance)
    result_date = results.order_by('date').values_list('date', flat=True).first()

    gender = request.GET.get('gender', '')
    if gender not in GENDERS:
        gender = ''

    category = request.GET.get('category', '')

    filtered_results = results
    if gender:
        filtered_results = filtered_results.filter(gender=gender)

    available_category_codes = list(
        filtered_results.exclude(category='')
        .values_list('category', flat=True)
        .distinct()
        .order_by('category')
    )
    categories = [
        (code, CATEGORY_LABELS.get(code, code))
        for code in available_category_codes
    ]

    if category not in available_category_codes:
        category = ''
    if category:
        filtered_results = filtered_results.filter(category=category)

    if category:
        place_field = 'category_place'
    elif gender:
        place_field = 'gender_place'
    else:
        place_field = 'place'

    filtered_results = _order_results(filtered_results, place_field)

    results_page = Paginator(filtered_results, RESULTS_PER_PAGE).get_page(
        request.GET.get('page')
    )

    # Totals for the whole protocol (unaffected by the table filters) so the
    # athlete details can show places as "15/500".
    protocol_results = results.filter(date=result_date)
    total_athletes = protocol_results.count()
    gender_totals = dict(
        protocol_results.values_list('gender').annotate(total=Count('pk'))
    )
    category_totals = dict(
        protocol_results.exclude(category='')
        .values_list('category')
        .annotate(total=Count('pk'))
    )
    for entry in results_page:
        entry.total_athletes = total_athletes
        entry.gender_athletes = gender_totals.get(entry.gender, 0)
        entry.category_athletes = category_totals.get(entry.category, 0)

    return render(
        request,
        'results/protocol.html',
        {
            'event': event,
            'year': year,
            'result_date': result_date,
            'distances': distances,
            'distance': distance,
            'gender': gender,
            'gender_choices': ResultEntry.GENDER_CHOICES,
            'category': category,
            'categories': categories,
            'results_page': results_page,
        },
    )


def api_results(request):
    """Return protocol results as JSON for a distance and date.

    Query parameters:
        distance: ``Distance`` pk (required).
        date: event date in ``YYYY-MM-DD`` format (required).
        gender: optional ``male`` / ``female`` filter.
        category: optional category code filter (for example ``M 18-34``).
        page: optional page number (``RESULTS_PER_PAGE`` entries per page).
    """
    if request.method != 'GET':
        response = JsonResponse(
            {'error': 'Метод не поддерживается. Используйте GET.'},
            status=405,
        )
        response['Allow'] = 'GET'
        return response

    distance_id = (request.GET.get('distance') or '').strip()
    if not distance_id.isdigit():
        return JsonResponse(
            {'error': 'Параметр distance обязателен и должен быть числом.'},
            status=400,
        )

    result_date = parse_date((request.GET.get('date') or '').strip())
    if result_date is None:
        return JsonResponse(
            {'error': 'Параметр date обязателен и должен быть в формате YYYY-MM-DD.'},
            status=400,
        )

    try:
        distance = Distance.objects.select_related('event').get(pk=distance_id)
    except Distance.DoesNotExist:
        return JsonResponse({'error': 'Дистанция не найдена.'}, status=404)

    results = ResultEntry.objects.filter(distance=distance, date=result_date)

    gender = request.GET.get('gender', '')
    if gender not in GENDERS:
        gender = ''

    category = request.GET.get('category', '')

    filtered_results = results
    if gender:
        filtered_results = filtered_results.filter(gender=gender)

    available_category_codes = list(
        filtered_results.exclude(category='')
        .values_list('category', flat=True)
        .distinct()
        .order_by('category')
    )

    if category not in available_category_codes:
        category = ''
    if category:
        filtered_results = filtered_results.filter(category=category)

    if category:
        place_field = 'category_place'
    elif gender:
        place_field = 'gender_place'
    else:
        place_field = 'place'

    filtered_results = _order_results(filtered_results, place_field)
    paginator = Paginator(filtered_results, RESULTS_PER_PAGE)
    results_page = paginator.get_page(request.GET.get('page'))

    # Totals are for the whole protocol, not affected by the table filters.
    total_athletes = results.count()
    gender_totals = dict(
        results.values_list('gender').annotate(total=Count('pk'))
    )
    category_totals = dict(
        results.exclude(category='')
        .values_list('category')
        .annotate(total=Count('pk'))
    )

    return JsonResponse(
        {
            'event': {
                'id': distance.event_id,
                'slug': distance.event.slug,
                'title': distance.event.title,
            },
            'distance': {
                'id': distance.pk,
                'name': distance.name,
                'length_km': float(distance.length_km),
            },
            'date': result_date.isoformat(),
            'filters': {
                'gender': gender,
                'category': category,
                'categories': [
                    {'code': code, 'label': CATEGORY_LABELS.get(code, code)}
                    for code in available_category_codes
                ],
            },
            'totals': {
                'athletes': total_athletes,
                'gender': {
                    code: gender_totals.get(code, 0)
                    for code, _ in ResultEntry.GENDER_CHOICES
                },
                'category': category_totals,
            },
            'count': paginator.count,
            'page': results_page.number,
            'pages': paginator.num_pages,
            'per_page': RESULTS_PER_PAGE,
            'next': (
                results_page.next_page_number()
                if results_page.has_next()
                else None
            ),
            'previous': (
                results_page.previous_page_number()
                if results_page.has_previous()
                else None
            ),
            'results': [_serialize_result(entry) for entry in results_page],
        },
        json_dumps_params={'ensure_ascii': False},
    )
