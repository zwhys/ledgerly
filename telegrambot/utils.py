from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler


# ── States ──────────────────────────


AWAITING_EMAIL, AWAITING_SHEET_URL = range(2)
AWAITING_NEW_EMAIL, AWAITING_NEW_SHEET_URL = range(100, 102)

# ── Keyboards ──────────────────────────


MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [["⚙️ Update particulars", "➕ Add transaction"]],
    resize_keyboard=True,
    one_time_keyboard=False,
)

PARTICULARS_INLINE = InlineKeyboardMarkup([
    [InlineKeyboardButton("Update email", callback_data="update_email")],
    [InlineKeyboardButton("Update Google Sheet",
                          callback_data="update_sheets")],
    [InlineKeyboardButton("Cancel", callback_data="cancel_particulars")]
])

CANCEL_PARTICULARS_INLINE = InlineKeyboardMarkup([[InlineKeyboardButton(
    "Cancel",
    callback_data="cancel_particulars")]
])


def build_vet_transaction_keyboard(transaction_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "✅ Accept", callback_data=f"accept:{transaction_id}"),
        InlineKeyboardButton(
            "❌ Reject", callback_data=f"reject:{transaction_id}"),
        InlineKeyboardButton(
            "✏️ Edit", callback_data=f"edit:{transaction_id}"),
    ]])


def build_reject_confirm_keyboard(transaction_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "Confirm", callback_data=f"reject_confirm:{transaction_id}"),
        InlineKeyboardButton(
            "Cancel", callback_data=f"reject_cancel:{transaction_id}"),
    ]])


# ── Global Commands ──────────────────────────


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


async def help_cmd(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:

    await update.message.reply_text(
        "Here are the available commands:\n\n"
        "/start — Connect your Telegram chat to Ledgerly.\n"
        "/help — Show this help message.\n"
        "/cancel — Cancel the current operation.\n\n"
        "You can also use the buttons in the menu to:\n"
        "• Update your email or Google Sheet"
        "• Add a transaction\n"
    )

    return ConversationHandler.END
