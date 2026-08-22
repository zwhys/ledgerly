import os
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv

from telegrambot.update_particulars import handle_update_particulars, particulars_back, update_particulars_handler

load_dotenv()

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_BOT_NAME = os.environ["TELEGRAM_BOT_NAME"]


def main():
    application = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .read_timeout(10)
        .write_timeout(10)
        .concurrent_updates(True)
        .build()
    )

    # edit_categories_handler = MessageHandler(filters.Text(
    #     ["Edit Categories"]), handle_edit_categories)
    # add_transaction_handler = MessageHandler(filters.Text(
    #     ["Add transaction"]), handle_add_transaction)
    # back_to_menu_handler = MessageHandler(
    #     filters.Text(["« Back to menu"]), handle_back_to_menu)

    # application.add_handler(onboarding_handler)
    # Commented out for easier testing

    # Reply-keyboard button handlers (only reached once a user is
    # no longer inside the onboarding conversation)
    application.add_handler(update_particulars_handler)
    application.add_handler(MessageHandler(filters.Text(
        ["Update particulars"]), handle_update_particulars))
    application.add_handler(CallbackQueryHandler(
        particulars_back, pattern="^particulars_back$"))

    # application.add_handler(edit_categories_handler)
    # application.add_handler(add_transaction_handler)
    # application.add_handler(back_to_menu_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
