from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from telegrambot.states import AWAITING_EMAIL


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
