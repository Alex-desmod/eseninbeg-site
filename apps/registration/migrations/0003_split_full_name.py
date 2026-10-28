"""Split full_name into surname, name, patronymic (optional)."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0002_alter_registration_bib_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='name',
            field=models.CharField(default='', max_length=100, verbose_name='Имя'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registration',
            name='patronymic',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Отчество'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registration',
            name='surname',
            field=models.CharField(default='', max_length=100, verbose_name='Фамилия'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='registration',
            name='full_name',
        ),
    ]
