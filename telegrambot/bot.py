import os
from telegram import ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv

from telegrambot.start import AWAITING_EMAIL, AWAITING_SHEET_URL, cancel_cmd, receive_email, receive_sheet_url, start_cmd
from telegrambot.handlers import handle_add_transaction, handle_edit_categories, handle_update_particulars

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
    onboarding_handler = ConversationHandler(
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

    update_particulars_handler = MessageHandler(filters.Text(
        # Turn all there into conversation handlers
        ["Update particulars"]), handle_update_particulars)
    edit_categories_handler = MessageHandler(filters.Text(
        ["Edit Categories"]), handle_edit_categories)
    add_transaction_handler = MessageHandler(filters.Text(
        ["Add transaction"]), handle_add_transaction)

    application.add_handler(onboarding_handler)

    # Reply-keyboard button handlers (only reached once a user is
    # no longer inside the onboarding conversation)
    application.add_handler(update_particulars_handler)
    application.add_handler(edit_categories_handler)
    application.add_handler(add_transaction_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
