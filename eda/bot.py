import os

from telegram.ext import Application

TOKEN = os.environ["TELEGRAM_TOKEN"]

application = Application.builder().token(TOKEN).build()
