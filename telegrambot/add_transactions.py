from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters

from telegrambot.keyboards import MAIN_KEYBOARD


async def handle_add_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Let's add a transaction...")

# async def handle_update_particulars(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     await update.message.reply_text(
#         "What would you like to update?",
#         reply_markup=PARTICULARS_INLINE,
#     )


add_transaction_handler = MessageHandler(filters.Text(
    ["Add transaction"]), handle_add_transaction)

