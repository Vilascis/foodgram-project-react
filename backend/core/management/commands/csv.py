from csv import DictReader

from django.conf import settings
from django.core.management import BaseCommand

from core.cookbook.models import Ingredient, Tag

DATA_DB = {
    Ingredient: 'ingredients.csv',
    Tag: 'tags.csv',
}
"""Словарь для записи данных в БД."""


class Command(BaseCommand):
    """Команда для записи данные в БД из файлов csv."""

    def handle(self, *args, **kwargs):
        try:
            for model, name_csv in DATA_DB.items():
                with open(
                    f'{settings.BASE_DIR}/data/{name_csv}', 'r', encoding='utf-8'
                ) as csv_file:
                    reader = DictReader(csv_file)
                    model.objects.bulk_create(model(**data) for data in reader)
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR_OUTPUT(
                    'Ошибка при импорте данных в базу данных. '
                    'Отсутствуют нужные файлы!'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Данные успешно загружены в базу данных')
            )
