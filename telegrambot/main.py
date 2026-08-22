import os
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv

from telegrambot.update_particulars import handle_update_particulars, onboarding_handler, update_particulars_handler

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

    application.add_handler(onboarding_handler)
    # Commented out for easier testing

    # Reply-keyboard button handlers (only reached once a user is
    # no longer inside the onboarding conversation)
    application.add_handler(update_particulars_handler)
    application.add_handler(MessageHandler(filters.Text(
        ["Update particulars"]), handle_update_particulars))

    application.run_polling()


if __name__ == "__main__":
    main()
