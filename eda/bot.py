import datetime as dt

import django
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, filters

django.setup()

from eda.core import settings  # noqa: E402
from eda.food import models, services  # noqa: E402
from eda.telegrambot import messages  # noqa: E402
from eda.telegrambot.utils import get_telegram  # noqa: E402


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.get_bot().send_message(update.message.chat_id, messages.HELP)


async def grocery_list_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    from_date = dt.date.today()
    to_date = from_date + dt.timedelta(days=1)
    if products := await services.get_grocery_list(from_date, to_date):
        await update.message.reply_text("\n".join(products))
    else:
        await update.message.reply_text("Список покупок пуст")


async def _send_menu_at(menu_date: dt.date, update: Update) -> None:
    try:
        menu = await services.get_menu_recipes_at(menu_date)
        if not (message := messages.menu(menu)):
            assert ValueError
    except (models.Menu.DoesNotExist, ValueError):
        await update.message.reply_text("Меню не сформировано")
    else:
        await update.message.reply_markdown_v2(message)


async def today_menu_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await _send_menu_at(dt.date.today(), update)


async def tomorrow_menu_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await _send_menu_at(dt.date.today() + dt.timedelta(days=1), update)


def main() -> None:
    application = get_telegram()

    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("start", help_command))

    chat_filter = filters.Chat(settings.TELEGRAM_CHAT_ID)
    application.add_handler(
        CommandHandler("list", grocery_list_command, filters=chat_filter)
    )
    application.add_handler(
        CommandHandler("today", today_menu_command, filters=chat_filter)
    )
    application.add_handler(
        CommandHandler("tomorrow", tomorrow_menu_command, filters=chat_filter)
    )

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
