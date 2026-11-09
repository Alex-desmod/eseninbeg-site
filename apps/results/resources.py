"""Import configuration for race protocols (Excel/CSV) of previous years.

The protocol file columns are matched by their Russian headers. The distance and
event date are not part of the file; they are chosen by the admin in the import
form and passed to ``import_data()`` as kwargs.
"""
import datetime
import re

from import_export import fields, resources, widgets

from .models import Checkpoint, ResultEntry, Split

# Values that protocols use to mark an empty cell.
EMPTY_VALUES = {'', '-', '—', '–'}

# Split columns are named like "CP1_Разворот". Only the part after the
# underscore is the checkpoint name; the CP number is just a column label.
SPLIT_COLUMN_RE = re.compile(r'^CP\d+_(.+)$', re.IGNORECASE)
# Key used to pass parsed split times from before_import_row to after_save_instance.
SPLIT_ROW_KEY = '__split_times__'

# Columns the protocol must contain.
REQUIRED_COLUMNS = (
    'Номер',
    'Фамилия',
    'Имя',
    'Категория',
)

CLUB_PLACEHOLDERS = {'нет клуба', 'no club', 'нет клуба/no club'}
# Statuses are sometimes written into the "Результат" column instead of a time.
STATUS_IN_RESULT = {'DNF', 'DNS', 'DSQ'}

CATEGORY_VALUES = {code for code, _ in ResultEntry.CAT_CHOICES}

TIME_RE = re.compile(r'^(?:(\d+):)?(\d{1,2}):(\d{2})(?:[.,](\d{1,6}))?$')

# Cyrillic letters are translated to their Latin counterparts used by the model.
CATEGORY_TRANSLATION = str.maketrans({'Ж': 'F', 'М': 'M'})

# City names often carry a "г." / "город" marker: "г Москва", "Москва г.".
CITY_PREFIX_RE = re.compile(r'^(?:г\.\s*|г\s+|город\s+)', re.IGNORECASE)
CITY_SUFFIX_RE = re.compile(r'(?:[,\s]+)(?:г\.?|город)$', re.IGNORECASE)


def is_empty(value):
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() in EMPTY_VALUES
    return False


def cleanup_text(value):
    """Collapse whitespace (including non-breaking spaces) into single spaces."""
    if value is None:
        return ''
    return ' '.join(str(value).replace('\xa0', ' ').split())


def normalize_category(value):
    """Normalize a category like ``F18-34`` / ``ж 60 +`` to ``F 18-34`` / ``F 60+``."""
    text = cleanup_text(value).upper().translate(CATEGORY_TRANSLATION)
    if not text:
        return ''
    # Drop every space, then always format as "<gender letter> <age group>".
    text = re.sub(r'\s+', '', text)
    category = f'{text[0]} {text[1:]}'
    if category not in CATEGORY_VALUES:
        raise ValueError(f'Неизвестная категория: «{value}»')
    return category


def gender_from_category(value):
    """Determine gender from the first letter: F/Ж -> female, M/М -> male."""
    text = cleanup_text(value).upper().translate(CATEGORY_TRANSLATION)
    if not text:
        raise ValueError('Не указана категория — невозможно определить пол')
    if text[0] == 'F':
        return 'female'
    if text[0] == 'M':
        return 'male'
    raise ValueError(f'Не удалось определить пол по категории: «{value}»')


class TextWidget(widgets.Widget):
    """Text value with trimmed/collapsed whitespace; empty cells become ''."""

    def clean(self, value, row=None, **kwargs):
        text = cleanup_text(value)
        return '' if text in EMPTY_VALUES else text


class IntegerValueWidget(widgets.Widget):
    """Integer that tolerates empty cells, dashes and Excel float cells."""

    def clean(self, value, row=None, **kwargs):
        if is_empty(value):
            return None
        if isinstance(value, float):
            if not value.is_integer():
                raise ValueError(f'Ожидается целое число, получено: «{value}»')
            return int(value)
        try:
            return int(str(value).strip())
        except (TypeError, ValueError):
            raise ValueError(f'Ожидается целое число, получено: «{value}»')


class BibNumberWidget(IntegerValueWidget):
    """Bib number is mandatory."""

    def clean(self, value, row=None, **kwargs):
        number = super().clean(value, row, **kwargs)
        if number is None:
            raise ValueError('Номер участника не указан')
        return number


class ClubWidget(TextWidget):
    """'нет клуба' / 'no club' mean the athlete has no club."""

    def clean(self, value, row=None, **kwargs):
        text = super().clean(value, row, **kwargs)
        if text.lower() in CLUB_PLACEHOLDERS:
            return ''
        return text


class CityWidget(TextWidget):
    """Strip the "г." / "город" marker: "г Москва" / "Москва г." → "Москва"."""

    def clean(self, value, row=None, **kwargs):
        text = super().clean(value, row, **kwargs)
        if not text:
            return text
        text = CITY_PREFIX_RE.sub('', text)
        text = CITY_SUFFIX_RE.sub('', text)
        return text.strip(' ,.')


class CategoryWidget(TextWidget):
    def clean(self, value, row=None, **kwargs):
        return normalize_category(value)


class StatusWidget(widgets.Widget):
    def clean(self, value, row=None, **kwargs):
        if is_empty(value):
            return ''
        status = cleanup_text(value).upper()
        if status not in {code for code, _ in ResultEntry.STATUS_CHOICES}:
            raise ValueError(
                f'Неизвестный статус: «{value}» (ожидается DNF, DSQ или DNS)'
            )
        return status


class ResultTimeWidget(widgets.Widget):
    """Parse a result time from text (``1:23:45`` / ``23:45``), Excel time cells
    or Excel day fractions. Status markers and empty cells become ``None``."""

    def clean(self, value, row=None, **kwargs):
        if is_empty(value):
            return None

        if isinstance(value, datetime.timedelta):
            return value
        if isinstance(value, datetime.datetime):
            value = value.time()
        if isinstance(value, datetime.time):
            return datetime.timedelta(
                hours=value.hour,
                minutes=value.minute,
                seconds=value.second,
                microseconds=value.microsecond,
            )
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            # Excel stores a time as a fraction of a day.
            return datetime.timedelta(days=float(value))

        text = str(value).strip().replace(',', '.')
        if text.upper() in STATUS_IN_RESULT:
            return None

        match = TIME_RE.fullmatch(text)
        if not match:
            raise ValueError(
                f'Не удалось распознать результат «{value}». '
                'Ожидается время вида 1:23:45 или 23:45'
            )

        hours, minutes, seconds, fraction = match.groups()
        hours = int(hours) if hours else 0
        minutes = int(minutes)
        seconds = int(seconds)
        microseconds = int(fraction.ljust(6, '0')) if fraction else 0

        if seconds > 59 or (hours and minutes > 59):
            raise ValueError(f'Некорректное время: «{value}»')

        return datetime.timedelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            microseconds=microseconds,
        )


SPLIT_TIME_WIDGET = ResultTimeWidget()


class ResultEntryResource(resources.ModelResource):
    """Imports a protocol file for the distance and date passed in kwargs."""

    place = fields.Field(
        attribute='place', column_name='Место', widget=IntegerValueWidget()
    )
    bib_number = fields.Field(
        attribute='bib_number', column_name='Номер', widget=BibNumberWidget()
    )
    surname = fields.Field(attribute='surname', column_name='Фамилия', widget=TextWidget())
    name = fields.Field(attribute='name', column_name='Имя', widget=TextWidget())
    country = fields.Field(attribute='country', column_name='Страна', widget=TextWidget())
    city = fields.Field(attribute='city', column_name='Город', widget=CityWidget())
    club = fields.Field(attribute='club', column_name='Клуб', widget=ClubWidget())
    category = fields.Field(
        attribute='category', column_name='Категория', widget=CategoryWidget()
    )
    category_place = fields.Field(
        attribute='category_place',
        column_name='Место в категории',
        widget=IntegerValueWidget(),
    )
    gender_place = fields.Field(
        attribute='gender_place', column_name='Место М/Ж', widget=IntegerValueWidget()
    )
    chip_time = fields.Field(
        attribute='chip_time', column_name='Результат', widget=ResultTimeWidget()
    )
    gun_time = fields.Field(
        attribute='gun_time', column_name='Абсолютный результат', widget=ResultTimeWidget()
    )
    status = fields.Field(
        attribute='status', column_name='Статус', widget=StatusWidget()
    )
    gender = fields.Field(attribute='gender', column_name='Пол')

    class Meta:
        model = ResultEntry
        # The protocols have no primary keys, so every row creates a new entry.
        import_id_fields = ['id']

    def before_import(self, dataset, **kwargs):
        if kwargs.get('distance') is None or kwargs.get('date') is None:
            raise ValueError('Не выбраны дистанция и дата импорта')

        headers = [cleanup_text(header) for header in (dataset.headers or [])]
        dataset.headers = headers

        missing = [column for column in REQUIRED_COLUMNS if column not in headers]
        if missing:
            raise ValueError('В файле отсутствуют колонки: ' + ', '.join(missing))

        # Match "CP<n>_<name>" columns to checkpoints of the selected distance.
        # Columns whose checkpoint does not exist are ignored.
        checkpoints = {
            cleanup_text(checkpoint.name).casefold(): checkpoint
            for checkpoint in Checkpoint.objects.filter(distance=kwargs['distance'])
        }
        self.split_columns = {}
        for header in headers:
            match = SPLIT_COLUMN_RE.match(header)
            if not match:
                continue
            name = cleanup_text(match.group(1))
            checkpoint = checkpoints.get(name.casefold())
            if checkpoint is not None:
                self.split_columns[header] = checkpoint

    def before_import_row(self, row, **kwargs):
        category = normalize_category(row.get('Категория'))
        row['Категория'] = category
        # Gender is derived from the category, not from a separate column.
        row['Пол'] = gender_from_category(category)
        # Some protocols have no "Статус" column: the status is then written
        # into the result column (for example "DNF" instead of a time).
        if 'Статус' not in row:
            result_status = cleanup_text(row.get('Результат')).upper()
            if result_status in STATUS_IN_RESULT:
                row['Статус'] = result_status

        # Parse split times now so a bad value invalidates the whole row.
        split_times = []
        for column, checkpoint in getattr(self, 'split_columns', {}).items():
            split_time = SPLIT_TIME_WIDGET.clean(row.get(column), row=row)
            if split_time is not None:
                split_times.append((checkpoint, split_time))
        row[SPLIT_ROW_KEY] = split_times

    def before_save_instance(self, instance, row, **kwargs):
        instance.distance = kwargs['distance']
        instance.date = kwargs['date']

    def after_save_instance(self, instance, row, **kwargs):
        if kwargs.get('dry_run') or instance.pk is None:
            return
        for checkpoint, time in row.get(SPLIT_ROW_KEY, ()):
            Split.objects.update_or_create(
                result=instance,
                checkpoint=checkpoint,
                defaults={'time': time},
            )
