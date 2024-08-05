import datetime as dt

from . import utils

HELP = """\
Бот для управления https://github.com/askvrtsv/eda
"""


def menu(menu: dict[str, list[str]]) -> str:
    lines = [
        "*{}*\n{}".format(
            mealtime.capitalize(),
            "\n".join(utils.escape_markdown(recipe) for recipe in recipes),
        )
        for mealtime, recipes in menu.items()
        if recipes
    ]
    return "\n\n".join(lines).strip()


def menu_date(menu_date: dt.date) -> str:
    return f"Меню на {utils.format_date(menu_date)}"
