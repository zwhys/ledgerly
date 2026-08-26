import os
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from telegrambot.update_particulars import handle_update_particulars, onboarding_handler, update_particulars_handler
from telegrambot.vetting import handle_accept, handle_edit_message, handle_reject, handle_edit, handle_reject_cancel, handle_reject_confirm

ENV = os.getenv("ENV", "dev")

if ENV == "dev":
    from dotenv import load_dotenv
    load_dotenv()

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_BOT_NAME = os.environ["TELEGRAM_BOT_NAME"]


def main():
    application = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .read_timeout(30)
        .write_timeout(30)
        .connect_timeout(30)
        .pool_timeout(30)
        .concurrent_updates(True)
        .build()
    )

    application.add_handler(onboarding_handler)

    # Reply-keyboard button handlers (only reached once a user is
    # no longer inside the onboarding conversation)
    application.add_handler(update_particulars_handler)
    application.add_handler(MessageHandler(filters.Text(
        ["Update particulars"]), handle_update_particulars))
    application.add_handler(CallbackQueryHandler(
        handle_accept, pattern=r"^accept:"))
    application.add_handler(CallbackQueryHandler(
        handle_reject, pattern=r"^reject:"))
    application.add_handler(CallbackQueryHandler(
        handle_edit, pattern=r"^edit:"))
    application.add_handler(CallbackQueryHandler(
        handle_reject_confirm, pattern=r"^reject_confirm:"))
    application.add_handler(CallbackQueryHandler(
        handle_reject_cancel, pattern=r"^reject_cancel:"))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_message),
        group=1,
        # handle_edit_message uses a broad filter so it catches the reply after "Edit" is tapped
        # Putting it in its own group (instead of default group=0) stops it from competing with
        # more specific text handlers like "Update particulars" — PTB only runs one match per
        # group, so without this, the broad filter could swallow messages meant for those handlers.
        # Both groups get checked independently, so nothing gets stolen.
    )

    application.run_polling()


if __name__ == "__main__":
    main()
