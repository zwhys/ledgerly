import asyncio
import re
from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from pipeline.database import connect_user_sheet, save_email, save_user_sheet
from telegrambot.utils import start_cmd, cancel_cmd, CANCEL_PARTICULARS_INLINE, MAIN_KEYBOARD, PARTICULARS_INLINE, AWAITING_EMAIL, AWAITING_SHEET_URL, AWAITING_NEW_EMAIL, AWAITING_NEW_SHEET_URL

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SHEET_ID_RE = re.compile(r"/spreadsheets/d/([a-zA-Z0-9-_]+)")


def extract_sheet_id(url: str) -> str | None:
    match = SHEET_ID_RE.search(url)
    return match.group(1) if match else None


# ── Entry point: reply keyboard button tap ──────────────────────────
async def handle_update_particulars(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "What would you like to update?",
        reply_markup=PARTICULARS_INLINE,
    )


# ── Inline submenu selections ────────────────────────────────────────
async def update_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Enter your new email address:",
                                  reply_markup=CANCEL_PARTICULARS_INLINE)

    return AWAITING_NEW_EMAIL


async def update_sheets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Enter the new Google Sheets URL:",
                                  reply_markup=CANCEL_PARTICULARS_INLINE)
    return AWAITING_NEW_SHEET_URL


async def receive_email(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    is_new_email: bool = False,
) -> int:

    email = update.message.text.strip()

    if not EMAIL_RE.match(email):
        await update.message.reply_text(
            "That doesn't look like a valid email address. Please try again:"
        )
        return AWAITING_NEW_EMAIL if is_new_email else AWAITING_EMAIL

    chat_id = str(update.effective_chat.id)

    await asyncio.to_thread(save_email, chat_id, email)
    context.user_data["email"] = email

    if is_new_email:
        await update.message.reply_text("✅ Email updated successfully.")
        return ConversationHandler.END

    await update.message.reply_text(
        "Thanks! Now please paste the URL of your Google Sheets file and send:"
    )
    return AWAITING_SHEET_URL


async def receive_sheet_url(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    is_new_sheet: bool = False,
) -> int:

    sheets_url = update.message.text.strip()
    sheet_id = extract_sheet_id(sheets_url)

    if sheet_id is None:
        await update.message.reply_text(
            "That doesn't look like a Google Sheets link. Please paste the full URL, "
            "e.g. https://docs.google.com/spreadsheets/d/…"
        )
        return AWAITING_NEW_SHEET_URL if is_new_sheet else AWAITING_SHEET_URL

    chat_id = str(update.effective_chat.id)

    if is_new_sheet:
        await asyncio.to_thread(connect_user_sheet, chat_id, sheet_id)

        await update.message.reply_text(
            "✅ Google Sheet updated successfully."
        )
    else:
        await asyncio.to_thread(connect_user_sheet, chat_id, sheet_id)

        await update.message.reply_text(
            "✅ Got it, sheet connected! Use the buttons below to get started.",
            reply_markup=MAIN_KEYBOARD,
        )

    return ConversationHandler.END


async def receive_new_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await receive_email(update, context, is_new_email=True)


async def receive_new_sheet_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await receive_sheet_url(update, context, is_new_sheet=True)


async def cancel_particulars(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:

    query = update.callback_query

    await query.answer()
    await query.edit_message_text("Cancelled, nothing changed.")

    return ConversationHandler.END

update_particulars_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(update_email,
                             pattern="^update_email$"),
        CallbackQueryHandler(update_sheets,
                             pattern="^update_sheets$"),
        CallbackQueryHandler(cancel_particulars,
                             pattern="^cancel_particulars$"
                             )
    ],
    states={
        AWAITING_NEW_EMAIL: [
            MessageHandler(filters.TEXT & ~filters.COMMAND,
                           receive_new_email),
            CallbackQueryHandler(
                cancel_particulars,
                pattern="^cancel_particulars$"
            ),
        ],
        AWAITING_NEW_SHEET_URL: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receive_new_sheet_url,
            ),
            CallbackQueryHandler(
                cancel_particulars,
                pattern="^cancel_particulars$"
            ),
        ],

    },
    fallbacks=[CommandHandler("cancel", cancel_cmd)],

)

onboarding_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start_cmd)],
    states={
        AWAITING_EMAIL: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email),
            # When the conversation is in the state, if the user sends (condition), call (function).
        ],
        AWAITING_SHEET_URL: [
            MessageHandler(filters.TEXT & ~filters.COMMAND,
                           receive_sheet_url),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_cmd)],
)
