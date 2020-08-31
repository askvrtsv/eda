import logging
import os
import re
from dataclasses import dataclass, field
from datetime import date
from functools import lru_cache
from typing import List

import requests
from airtable import Airtable


@dataclass
class Ingredient:
    VALID_UNITS = ['шт.', 'гр.']

    name: str
    amount: float
    unit: str


@dataclass
class Meal:
    name: str
    id: str
    ingredients_str: str
    recipe: str

    @property
    def url(self):
        meals_url = os.getenv('EDA_AIRTABLE_MEALS_URL')
        if not self.id or not meals_url:
            return ''
        return '{0}/{1}'.format(meals_url, self.id)

    @property
    def ingredients(self) -> list:
        result = []
        for ingredient_str in self.ingredients_str.splitlines():
            try:
                group = re.match(
                    r'(?P<name>.*):\s(?P<amount>.*)\s+(?P<unit>.*)',
                    ingredient_str).group
                result.append(Ingredient(
                    name=group('name'),
                    amount=float(group('amount')),
                    unit=group('unit')))
            except (AttributeError, ValueError) as e:
                logging.warning('bad ingredient format for %s', self.name, exc_info=e)
        return result


@dataclass
class Mealtime:
    VALID_NAMES = ['Завтрак', 'Обед', 'Ужин']

    name: str
    meals: List[Meal] = field(default_factory=list)


@dataclass
class Menu:
    menu_date: date
    id: str = None
    mealtimes: List[Mealtime] = field(default_factory=list)

    @property
    def weekday(self) -> str:
        weekdays = (
            'понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота',
            'воскресенье')
        return weekdays[int(self.menu_date.weekday())]

    def to_markdown(self) -> str:
        mealtimes = []
        for mealtime in self.mealtimes:
            if not mealtime.meals:
                continue
            meals = []
            for meal in sorted(mealtime.meals, key=lambda m: m.name):
                # if meal has a recipe
                if meal.recipe and meal.url:
                    meal_name = '<{1}|{0}>'.format(meal.name, meal.url)
                else:
                    meal_name = meal.name
                meals.append(meal_name)
            mealtimes.append(
                '_{0}_\n{1}'.format(mealtime.name, '\n'.join(meals)))
        if mealtimes:
            mealtimes_str = '\n\n'.join(mealtimes)
        else:
            mealtimes_str = 'Ничего не указано'
        return '*{0}*\n{1}'.format(
            self.menu_date.strftime('%d.%m.%Y'), mealtimes_str)

    def as_airtable_dict(self) -> dict:
        try:
            menu_date = self.menu_date.isoformat()
        except AttributeError:
            menu_date = None
        return {
            'Дата': menu_date,
            'День недели': self.weekday,
        }


@lru_cache
def get_airtable_client(tablename: str) -> Airtable:
    return Airtable(
        'appD9wS3HBNcOJNYz', tablename,
        api_key=os.getenv('EDA_AIRTABLE_API_KEY'), timeout=10.0)


def send_text_to_slack(text: str) -> None:
    """Sends a message with text `text` to Slack."""
    resp = requests.post(
        os.environ['EDA_SLACK_WEBHOOK'],
        json={'text': text})
    resp.raise_for_status()
