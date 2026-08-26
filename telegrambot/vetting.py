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
    Expected order: [date, type, category, amount, currency]
    """
    return (
        f"Date: {entry['date']}\n"
        f"Transaction: {entry['type']}\n"
        f"Amount: {entry['amount']} {entry['currency']}\n"
        f"Category: {entry['category']}\n"
        f"Description: {entry.get('description', '-')}"
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


def update_pending_transaction(transaction_id: str, entry) -> bool:
    """Overwrites the entry for an existing pending transaction.
    Returns True if the row was found and updated, False if no such transaction_id exists.
    """
    worksheet = get_db_worksheet("pending")
    cell = worksheet.find(transaction_id)

    if cell is None:
        return False

    worksheet.update_cell(cell.row, 3, json.dumps(entry))
    return True


async def handle_accept(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    transaction_id = query.data.split(":", 1)[1]
    pending = get_pending_transaction(transaction_id)

    if pending is None:
        await query.edit_message_text("This transaction is no longer pending.")
        return

    save_transaction(pending["sheet_id"], pending["entry"])
    delete_pending_transaction(transaction_id)

    await query.edit_message_text("✅ Transaction added successfully.")


async def handle_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    transaction_id = query.data.split(":", 1)[1]
    keyboard = build_reject_confirm_keyboard(transaction_id)
    await query.edit_message_reply_markup(reply_markup=keyboard)


async def handle_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    transaction_id = query.data.split(":", 1)[1]
    pending = get_pending_transaction(transaction_id)

    if pending is None:
        await query.edit_message_text("This transaction is no longer pending.")
        return

    context.chat_data["awaiting_edit"] = transaction_id

    entry = pending["entry"]

    prefill_text = (
        f"Date: {entry['date']}\n"
        f"Transaction: {entry['type']}\n"
        f"Category: {entry['category']}\n"
        f"Amount: {entry['amount']} {entry['currency']}\n"
        f"Description: {entry.get('description', '-')}"
    )

    await query.edit_message_text(
        "Send the corrected details in this format (tap to copy):\n\n"
        f"```text\n{prefill_text}\n```",
        parse_mode="Markdown",
    )


async def handle_edit_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    transaction_id = context.chat_data.get("awaiting_edit")

    if transaction_id is None:
        return

    text = update.message.text.strip()

    # Remove Markdown code block markers if the user copied the code block
    if text.startswith("```") and text.endswith("```"):
        text = text[3:-3].strip()

    new_entry = parse_edit_text(text)

    if new_entry is None:
        await update.message.reply_text(
            "Couldn't parse that. Please use the format:\n\n"
            "```text\n"
            "Date: ...\n"
            "Transaction: ...\n"
            "Category: ...\n"
            "Amount: ... ...\n"
            "Description: ...\n"
            "```",
            parse_mode="Markdown",
        )
        return

    update_pending_transaction(transaction_id, new_entry)
    del context.chat_data["awaiting_edit"]

    text_preview = format_entry_message(new_entry)
    keyboard = build_vet_transaction_keyboard(transaction_id)

    await update.message.reply_text(
        f"Updated:\n\n{text_preview}",
        reply_markup=keyboard,
    )


def parse_edit_text(text: str) -> dict | None:
    """Parses the prefilled edit format into an entry dictionary."""

    fields = {}

    for line in text.strip().splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        fields[key.strip().lower()] = value.strip()

    # Transaction -> type
    if "transaction" in fields:
        fields["type"] = fields.pop("transaction")

    if "amount" in fields:
        amount_parts = fields["amount"].split()

        if len(amount_parts) == 2:
            fields["amount"] = amount_parts[0]
            fields["currency"] = amount_parts[1]

    required_fields = [
        "date",
        "type",
        "category",
        "amount",
        "currency",
    ]

    if any(not fields.get(field) for field in required_fields):
        return None

    return {
        "date": fields["date"],
        "type": fields["type"],
        "category": fields["category"],
        "amount": fields["amount"],
        "currency": fields["currency"],
        "description": fields.get("description", "-"),
    }


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
