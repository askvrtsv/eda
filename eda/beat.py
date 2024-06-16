import django

django.setup()

import asyncio
import datetime as dt
import os

import pytz
from asgiref.sync import sync_to_async
from scheduler.asyncio import Scheduler
from telegram.constants import ParseMode

from eda.bot import application
from eda.food import models, services
from eda.telegrambot.messages import generate_menu_message

CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

get_menu_recipes_at = sync_to_async(
    services.get_menu_recipes_at, thread_sensitive=False
)


async def send_tomorrow_menu() -> None:
    menu_date = dt.date.today() + dt.timedelta(days=1)

    try:
        menu = await get_menu_recipes_at(menu_date)
    except models.Menu.DoesNotExist:
        return None

    if message := generate_menu_message(menu):
        await application.bot.send_message(CHAT_ID, f"Меню на {menu_date:%d.%m}")
        await application.bot.send_message(
            CHAT_ID, message, parse_mode=ParseMode.MARKDOWN_V2
        )


async def main():
    schedule = Scheduler(tzinfo=dt.UTC)

    schedule.daily(
        dt.time(hour=17, tzinfo=pytz.timezone("Europe/Moscow")),
        send_tomorrow_menu,
    )

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
