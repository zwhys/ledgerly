from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from telegrambot.update_particulars import AWAITING_EMAIL, AWAITING_SHEET_URL, receive_email, receive_sheet_url



async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Welcomes user, asks for email then google sheets'''
    await update.message.reply_text(
        "Hi! I'm the Ledgerly bot. To connect this chat to your account, "
        "please send me the email address you use for Ledgerly:"
    )
    return AWAITING_EMAIL


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Okay, cancelled.")
    return ConversationHandler.END

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
