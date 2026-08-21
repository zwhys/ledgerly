import re
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from pipeline.database import save_user_email, save_user_sheet, get_email_for_chat

AWAITING_EMAIL, AWAITING_SHEET_URL = range(2)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def extract_sheet_id(url: str) -> str | None:
    match = re.compile(r"/spreadsheets/d/([a-zA-Z0-9-_]+)").search(url)
    return match.group(1) if match else None


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Hi! I'm the Ledgerly bot. To connect this chat to your account, "
        "please send me the email address you use for Ledgerly:"
    )
    return AWAITING_EMAIL


async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_email = update.message.text.strip()

    if not EMAIL_RE.match(user_email):
        await update.message.reply_text(
            "That doesn't look like a valid email address. Please try again:"
        )
        return AWAITING_EMAIL

    chat_id = update.effective_chat.id
    save_user_email(user_email, chat_id)
    context.user_data["user_email"] = user_email  # Saves email to cache

    await update.message.reply_text(
        "Thanks! Now please paste the url of your Google Sheets File and send:"
    )
    return AWAITING_SHEET_URL


async def receive_sheet_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    sheets_url = update.message.text.strip()
    sheet_id = extract_sheet_id(sheets_url)

    if sheet_id is None:
        await update.message.reply_text(
            "That doesn't look like a Google Sheets link. Please paste the full URL, "
            "e.g. https://docs.google.com/spreadsheets/d/…"
        )
        return AWAITING_SHEET_URL

    user_email = context.user_data.get("user_email")
    if user_email is None:
        # conversation state lost (e.g. bot restarted) — fall back to chat_id lookup
        user_email = get_email_for_chat(update.effective_chat.id)

    if user_email is None:
        await update.message.reply_text(
            "Something went wrong — please send /start again."
        )
        return ConversationHandler.END

    save_user_sheet(user_email, sheet_id)

    await update.message.reply_text("✅ Got it, sheet connected!")
    return ConversationHandler.END


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Okay, cancelled.")
    return ConversationHandler.END
