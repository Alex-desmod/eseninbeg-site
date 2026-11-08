from django.core.paginator import Paginator
from django.db.models import Case, Count, F, IntegerField, Value, When
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from apps.events.models import Distance, Event
from .models import ResultEntry

RESULTS_PER_PAGE = 50

GENDERS = {value for value, _ in ResultEntry.GENDER_CHOICES}
CATEGORY_LABELS = dict(ResultEntry.CAT_CHOICES)
STATUS_ORDER = {
    '': 0,
    'DNF': 1,
    'DSQ': 2,
    'DNS': 3,
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

    status_order = Case(
        *[
            When(status=status, then=Value(order))
            for status, order in STATUS_ORDER.items()
        ],
        default=Value(len(STATUS_ORDER)),
        output_field=IntegerField(),
    )

    filtered_results = filtered_results.annotate(
        position=F(place_field),
        status_order=status_order,
    ).order_by(
        'status_order',
        F('position').asc(nulls_last=True),
        'surname',
        'name',
        'bib_number',
    )

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
