from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler


# ── States ──────────────────────────


AWAITING_EMAIL, AWAITING_SHEET_URL = range(2)
AWAITING_NEW_EMAIL, AWAITING_NEW_SHEET_URL = range(100, 102)

# ── Keyboards ──────────────────────────


MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [["Update particulars", "Add transaction"]],
    resize_keyboard=True,
    one_time_keyboard=False,
)

PARTICULARS_INLINE = InlineKeyboardMarkup([
    [InlineKeyboardButton("Change email", callback_data="update_email")],
    [InlineKeyboardButton("Change Google Sheet",
                          callback_data="update_sheets")],
    [InlineKeyboardButton("Cancel", callback_data="cancel_particulars")]
])

CANCEL_PARTICULARS_INLINE = InlineKeyboardMarkup([[InlineKeyboardButton(
    "Cancel",
    callback_data="cancel_particulars")]
])

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
