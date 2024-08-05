import datetime as dt
import re

from telegram.ext import Application

from eda.core import settings


def get_telegram() -> Application:
    return Application.builder().token(settings.TELEGRAM_TOKEN).build()


def escape_markdown(string: str) -> str:
    return re.sub(r"[_*[\]()~>#\+\-=|{}.!]", lambda x: "\\" + x.group(), string)


def format_date(date: dt.date) -> str:
    if date == dt.date.today():
        return "сегодня"
    elif date == dt.date.today() + dt.timedelta(days=1):
        return "завтра"
    else:
        return date.strftime(r"%d.%m")
