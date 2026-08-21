import os
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv

from start import AWAITING_EMAIL, AWAITING_SHEET_URL, cancel_cmd, receive_email, receive_sheet_url, start_cmd

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

    # ConversationHandler to handle the state machine
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_cmd)],
        states={
            AWAITING_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email),
            ],
            AWAITING_SHEET_URL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND,
                               receive_sheet_url),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_cmd)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
