import argparse
import logging
from datetime import date, timedelta
from functools import lru_cache, partial
from typing import List, Iterator, Optional

from .core import (
    get_airtable_client, Menu, Mealtime, Meal, send_text_to_slack)


def insert_dummy_menus_command() -> None:
    try:
        start_date = date.today()
        end_date = start_date + timedelta(days=10)
        menus = _get_missed_menus(start_date, end_date)
    except Exception as e:
        logging.fatal('can\'t get missed menus', exc_info=e)
        return
    for menu in menus:
        try:
            _insert_menu(menu)
        except Exception as e:
            logging.fatal('cat\'t insert menu %s', menu, exc_info=e)


def delete_old_menus_command(older_than_n_days: int = 3) -> None:
    try:
        older_than_date = date.today() - timedelta(days=older_than_n_days)
        menus = _get_outdated_menus(older_than_date)
    except Exception as e:
        logging.fatal('can\'t get outdated menus', exc_info=e)
        return
    for menu in menus:
        try:
            _delete_menu(menu)
        except Exception as e:
            logging.fatal('can\'t delete menu with id %s', menu.id, exc_info=e)


def send_menu_to_slack_command(menu_date: date) -> None:
    try:
        menu = _find_menu_at_date(menu_date)
    except Exception as e:
        logging.fatal('can\'t fetch menu from airtable', exc_info=e)
        return
    if not menu:
        logging.info('no menu at %s', menu_date)
        return
    if _is_menu_empty(menu):
        logging.info('menu at %s is empty', menu_date)
        return
    try:
        send_text_to_slack(menu.to_markdown())
    except Exception as e:
        logging.fatal('can\'t send message to slack', exc_info=e)


def send_product_list_to_slack_command() -> None:
    """Определяет какие ингредиенты потребуются на наделе,
    формирует список покупок и отправляет его в Slack."""
    menus = []
    for date_ in _get_dates(date.today()):
        try:
            menu = _find_menu_at_date(date_)
        except Exception as e:
            logging.error('can\'t fetch menu from airtable', exc_info=e)
        else:
            if menu:
                menus.append(menu)
    ingredients = (
        ingredient.name
        for menu in menus
        for mealtime in menu.mealtimes
        for meal in mealtime.meals
        for ingredient in meal.ingredients)
    ingredients = sorted(set(ingredients))
    if ingredients:
        try:
            send_text_to_slack('*Необходимые продукты*\n' + '\n'.join(ingredients))
        except Exception as e:
            logging.fatal('can\'t send message to slack', exc_info=e)


def _get_dates(start_date: date, until_next_iso_weekday: int = 5) -> List[date]:
    # todo: docstring and renaming
    result = [start_date]
    current_date = start_date + timedelta(days=1)
    while current_date.weekday() != until_next_iso_weekday:
        result.append(current_date)
        current_date += timedelta(days=1)
    return result


def _is_menu_empty(menu: Menu) -> bool:
    result = True
    for mealtime in menu.mealtimes:
        if mealtime.meals:
            result = False
            break
    return result


def _find_menu_at_date(menu_date: date) -> Optional[Menu]:
    for menu_record in _get_all_menu_records():
        if menu_record['fields'].get('Дата') == menu_date.isoformat():
            return _build_menu_from_airtable_data(menu_record)


@lru_cache
def _get_all_menu_records() -> List:
    return get_airtable_client('Меню').get_all()


def _does_menu_at_date_exist(menu_date: date) -> bool:
    for menu_record in _get_all_menu_records():
        if menu_record['fields'].get('Дата') == menu_date.isoformat():
            return True
    return False


def _get_missed_menus(start_date: date, end_date: date) -> Iterator[Menu]:
    current_date = start_date
    while current_date < end_date:
        if not _does_menu_at_date_exist(current_date):
            yield Menu(menu_date=current_date)
        current_date += timedelta(days=1)


@lru_cache
def _get_meal_dict() -> dict:
    result = {}
    for meal_record in get_airtable_client('Блюда').get_all():
        meal_id = meal_record['id']
        meal = {
            f: meal_record['fields'].get(f, '')
            for f in ['Название', 'Ингредиенты', 'Рецепт']}
        result[meal_id] = meal
    return result


def _build_meal_by_id(id_) -> Meal:
    data = _get_meal_dict()[id_]
    meal = Meal(
        name=data['Название'],
        id=id_,
        ingredients_str=data['Ингредиенты'],
        recipe=data['Рецепт'])
    return meal


def _build_mealtime(name: str, meal_ids: List[str]) -> Mealtime:
    mealtime = Mealtime(
        name=name,
        meals=[_build_meal_by_id(i) for i in meal_ids])
    return mealtime


def _build_menu_from_airtable_data(data: dict) -> Menu:
    try:
        menu_date = date.fromisoformat(data['fields'].get('Дата'))
    except TypeError:
        menu_date = None
    mealtimes = [
        _build_mealtime(n, data['fields'].get(n, []))
        for n in Mealtime.VALID_NAMES]
    return Menu(
        menu_date=menu_date,
        id=data['id'],
        mealtimes=mealtimes)


def _get_outdated_menus(older_than_date: date) -> Iterator[Menu]:
    for menu_record in _get_all_menu_records():
        menu = _build_menu_from_airtable_data(menu_record)
        if menu.menu_date and menu.menu_date <= older_than_date:
            yield menu


def _insert_menu(menu: Menu) -> None:
    get_airtable_client('Меню').insert(menu.as_airtable_dict())


def _delete_menu(menu: Menu) -> None:
    get_airtable_client('Меню').delete(menu.id)


if __name__ == '__main__':
    COMMAND_MAP = {
        'insert_dummy_menus': insert_dummy_menus_command,
        'delete_old_menus': delete_old_menus_command,
        'send_today_menu_to_slack': partial(
            send_menu_to_slack_command, date.today()),
        'send_product_list_to_slack': send_product_list_to_slack_command,
    }
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=COMMAND_MAP.keys())
    args = parser.parse_args()
    command = COMMAND_MAP[args.command]
    command()
