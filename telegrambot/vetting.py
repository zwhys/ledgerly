import json
import os
from telegram import Bot, Update
from telegram.ext import ContextTypes

from pipeline.database import get_chat_id, get_db_worksheet
from pipeline.sheets import save_transaction
from telegrambot.utils import build_reject_confirm_keyboard, build_vet_transaction_keyboard


ENV = os.getenv("ENV", "dev")

if ENV == "dev":
    from dotenv import load_dotenv
    load_dotenv()

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]

bot = Bot(token=TELEGRAM_TOKEN)
pending_transactions: dict[str, dict] = {}


def format_entry_message(entry: dict) -> str:
    """Turn a list-style entry into a readable Telegram message.
    Expected order: [date, entry_type, category, amount, currency]
    """
    return (
        f"Date: {entry['date']}\n"
        f"Transaction: {entry['type']}\n"
        f"Amount: {entry['amount']} {entry['currency']}\n"
        f"Category: {entry['category']}\n"
    )


async def send_telegram_message(entry, sheet_id, transaction_id):
    chat_id = get_chat_id(sheet_id)
    if chat_id is None:
        print(
            f"No chat_id found for sheet_id={sheet_id}, skipping Telegram send.")
        return

    text = format_entry_message(entry)
    keyboard = build_vet_transaction_keyboard(transaction_id)

    save_pending_transaction(transaction_id, sheet_id, entry)

    try:
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)
    except Exception as e:
        print(f"Failed to send Telegram message for sheet_id={sheet_id}: {e}")


def save_pending_transaction(transaction_id: str, sheet_id: str, entry) -> None:
    worksheet = get_db_worksheet("pending")

    worksheet.append_row([transaction_id, sheet_id, json.dumps(entry)])


def get_pending_transaction(transaction_id: str) -> dict | None:
    worksheet = get_db_worksheet("pending")

    cell = worksheet.find(transaction_id)

    if cell is None:
        return None

    row = worksheet.row_values(cell.row)
    _, sheet_id, entry_json = row

    return {"sheet_id": sheet_id, "entry": json.loads(entry_json)}


def delete_pending_transaction(transaction_id: str) -> None:
    worksheet = get_db_worksheet("pending")
    cell = worksheet.find(transaction_id)

    if cell is not None:
        worksheet.delete_rows(cell.row)


async def handle_accept(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    transaction_id = query.data.split(":", 1)[1]
    pending = get_pending_transaction(transaction_id)

    if pending is None:
        await query.edit_message_text("This transaction is no longer pending.")
        return

    save_transaction(pending["entry"])
    delete_pending_transaction(transaction_id)

    await query.edit_message_text("✅ Transaction accepted and added to your sheet.")


async def handle_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    transaction_id = query.data.split(":", 1)[1]
    keyboard = build_reject_confirm_keyboard(transaction_id)
    await query.edit_message_reply_markup(reply_markup=keyboard)


async def handle_reject_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    transaction_id = query.data.split(":", 1)[1]
    delete_pending_transaction(transaction_id)

    await query.edit_message_text("❌ Transaction rejected. Nothing was added.")


async def handle_reject_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    transaction_id = query.data.split(":", 1)[1]
    keyboard = build_vet_transaction_keyboard(transaction_id)
    await query.edit_message_reply_markup(reply_markup=keyboard)
