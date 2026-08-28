import asyncio
from datetime import datetime
import uuid
from telegram import Update
from telegram.ext import ContextTypes

from pipeline.database import get_sheet_id
from telegrambot.vetting import save_pending_transaction


def get_datetime() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S (SGT)")


async def handle_add_transaction(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    transaction_id = str(uuid.uuid4())
    chat_id = str(update.effective_chat.id)

    sheet_id = await asyncio.to_thread(get_sheet_id, chat_id=chat_id)

    await asyncio.to_thread(save_pending_transaction, transaction_id, sheet_id)

    context.chat_data["awaiting_transaction"] = transaction_id

    prefill_text = (
        f"Date: {get_datetime()}\n"
        f"Transaction: Expense/Income\n"
        f"Category: \n"
        f"Amount: <amount> <currency>\n"
        f"Description: "
    )

    await update.message.reply_text(
        "Send the new entry in this format (tap to copy):\n\n"
        f"```text\n{prefill_text}\n```",
        parse_mode="Markdown",
    )
