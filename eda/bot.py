from telegram.ext import Application

from eda.core import settings

application = Application.builder().token(settings.TELEGRAM_TOKEN).build()
