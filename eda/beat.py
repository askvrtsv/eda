import asyncio
import collections
import datetime as dt

import django
import pytz
from scheduler.asyncio import Scheduler
from telegram.constants import ParseMode

django.setup()

from eda.core import settings  # noqa: E402
from eda.food import models, services  # noqa: E402
from eda.telegrambot import messages, utils  # noqa: E402


async def _send_menu(
    menu: collections.defaultdict[str, list[str]], menu_date: dt.date
) -> None:
    if menu_message := messages.menu(menu):
        bot = utils.get_telegram().bot
        await bot.send_message(settings.TELEGRAM_CHAT_ID, messages.menu_date(menu_date))
        await bot.send_message(
            settings.TELEGRAM_CHAT_ID, menu_message, parse_mode=ParseMode.MARKDOWN_V2
        )


async def send_today_menu() -> None:
    menu_date = dt.date.today()
    try:
        menu = await services.get_menu_recipes_at(menu_date)
    except models.Menu.DoesNotExist:
        return None
    else:
        await _send_menu(menu, menu_date)


async def main():
    schedule = Scheduler(tzinfo=dt.UTC)

    schedule.daily(
        dt.time(hour=7, minute=30, tzinfo=pytz.timezone("Europe/Moscow")),
        send_today_menu,
    )

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
