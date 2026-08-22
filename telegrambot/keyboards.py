from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["Update particulars", "Edit Categories"],
        ["Add transaction"],
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
)


PARTICULARS_INLINE = InlineKeyboardMarkup([
    [InlineKeyboardButton("Change email", callback_data="update_email")],
    [InlineKeyboardButton("Change Google Sheet",
                          callback_data="update_sheets")],
    [InlineKeyboardButton("« Back", callback_data="particulars_back")],
])
