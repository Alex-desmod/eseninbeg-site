from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from apps.events.models import Distance, Event

from .models import Checkpoint, ResultEntry, Split


class ResultsApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.event = Event.objects.create(
            title='Весенний забег',
            slug='spring',
            location='Москва',
        )
        cls.distance = Distance.objects.create(
            event=cls.event,
            name='5 км',
            length_km=Decimal('5.00'),
        )
        cls.other_distance = Distance.objects.create(
            event=cls.event,
            name='10 км',
            length_km=Decimal('10.00'),
        )
        cls.result_date = date(2026, 5, 1)
        cls.checkpoint = Checkpoint.objects.create(
            distance=cls.distance,
            name='Разворот',
            length_km=Decimal('2.50'),
            order=1,
        )

        cls.first = ResultEntry.objects.create(
            distance=cls.distance,
            date=cls.result_date,
            gender='male',
            category='M 18-34',
            place=1,
            gender_place=1,
            category_place=1,
            bib_number=1,
            surname='Иванов',
            name='Иван',
            country='Россия',
            city='Москва',
            club='Клуб',
            chip_time=timedelta(minutes=20),
            gun_time=timedelta(minutes=21),
        )
        Split.objects.create(
            result=cls.first,
            checkpoint=cls.checkpoint,
            time=timedelta(minutes=10),
        )
        cls.second = ResultEntry.objects.create(
            distance=cls.distance,
            date=cls.result_date,
            gender='female',
            category='F 18-34',
            place=2,
            gender_place=1,
            category_place=1,
            bib_number=2,
            surname='Петрова',
            name='Анна',
            chip_time=timedelta(minutes=22),
            gun_time=timedelta(minutes=23),
        )
        cls.dns = ResultEntry.objects.create(
            distance=cls.distance,
            date=cls.result_date,
            gender='male',
            category='M 35-39',
            bib_number=3,
            surname='Сидоров',
            name='Пётр',
            status='DNS',
        )

        # Entries that must not appear in the response.
        ResultEntry.objects.create(
            distance=cls.distance,
            date=date(2026, 5, 2),
            gender='male',
            category='M 18-34',
            place=1,
            gender_place=1,
            category_place=1,
            bib_number=4,
            surname='Другой',
            name='День',
        )
        ResultEntry.objects.create(
            distance=cls.other_distance,
            date=cls.result_date,
            gender='male',
            category='M 18-34',
            place=1,
            gender_place=1,
            category_place=1,
            bib_number=5,
            surname='Другая',
            name='Дистанция',
        )

    def get_results(self, **params):
        query = {
            'distance': self.distance.pk,
            'date': self.result_date.isoformat(),
        }
        query.update(params)
        return self.client.get(reverse('results_api:list'), query)

    def test_returns_results_for_distance_and_date(self):
        response = self.get_results()

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['event']['slug'], self.event.slug)
        self.assertEqual(data['distance']['id'], self.distance.pk)
        self.assertEqual(data['date'], self.result_date.isoformat())
        self.assertEqual(data['count'], 3)
        self.assertEqual(
            [item['id'] for item in data['results']],
            [self.first.pk, self.second.pk, self.dns.pk],
        )
        self.assertEqual(data['totals']['athletes'], 3)
        self.assertEqual(data['totals']['gender'], {'male': 2, 'female': 1})

    def test_serializes_result_details_and_splits(self):
        data = self.get_results().json()
        entry = data['results'][0]

        self.assertEqual(entry['full_name'], 'Иванов Иван')
        self.assertEqual(entry['category_display'], 'М 18-34')
        self.assertEqual(entry['chip_time'], '0:20:00')
        self.assertEqual(entry['chip_time_seconds'], 1200)
        self.assertEqual(entry['chip_pace'], '4:00')
        self.assertEqual(entry['status'], '')
        self.assertEqual(len(entry['splits']), 1)
        self.assertEqual(entry['splits'][0]['checkpoint'], 'Разворот')
        self.assertEqual(entry['splits'][0]['time'], '0:10:00')
        self.assertEqual(entry['splits'][0]['pace'], '4:00')

    def test_gender_filter_uses_gender_place(self):
        data = self.get_results(gender='female').json()

        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['id'], self.second.pk)
        self.assertEqual(data['results'][0]['position'], 1)
        self.assertEqual(data['filters']['gender'], 'female')
        self.assertEqual(
            [item['code'] for item in data['filters']['categories']],
            ['F 18-34'],
        )

    def test_category_filter_uses_category_place(self):
        data = self.get_results(category='M 18-34').json()

        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['id'], self.first.pk)
        self.assertEqual(data['results'][0]['position'], 1)
        self.assertEqual(data['filters']['category'], 'M 18-34')

    def test_unknown_filters_are_ignored(self):
        data = self.get_results(gender='unknown', category='unknown').json()

        self.assertEqual(data['count'], 3)
        self.assertEqual(data['filters']['gender'], '')
        self.assertEqual(data['filters']['category'], '')

    def test_pagination(self):
        with patch('apps.results.views.RESULTS_PER_PAGE', 2):
            first_page = self.get_results().json()
            second_page = self.get_results(page=2).json()

        self.assertEqual(first_page['pages'], 2)
        self.assertEqual(first_page['per_page'], 2)
        self.assertEqual(first_page['next'], 2)
        self.assertIsNone(first_page['previous'])
        self.assertEqual(len(first_page['results']), 2)

        self.assertEqual(second_page['page'], 2)
        self.assertEqual(second_page['previous'], 1)
        self.assertIsNone(second_page['next'])
        self.assertEqual(len(second_page['results']), 1)

    def test_no_results_returns_empty_list(self):
        response = self.get_results(date='2026-01-01')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 0)
        self.assertEqual(data['results'], [])
        self.assertEqual(data['totals']['athletes'], 0)

    def test_requires_distance_and_date(self):
        response = self.client.get(reverse('results_api:list'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('distance', response.json()['error'])

        response = self.client.get(
            reverse('results_api:list'),
            {'distance': self.distance.pk},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('date', response.json()['error'])

        response = self.client.get(
            reverse('results_api:list'),
            {'distance': self.distance.pk, 'date': '01.05.2026'},
        )
        self.assertEqual(response.status_code, 400)

    def test_unknown_distance_returns_404(self):
        response = self.get_results(distance='999999')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'Дистанция не найдена.')

    def test_non_get_method_not_allowed(self):
        response = self.client.post(reverse('results_api:list'))

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response['Allow'], 'GET')
