from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

async def handle_update_particulars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Let's update your particulars...")

async def handle_edit_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Let's edit your categories...")

async def handle_add_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Let's add a transaction...")
