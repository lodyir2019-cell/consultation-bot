import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from models import Database

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    db.add_user(user_id, user_name, role='client')
    text = f"Welcome to Consultation Marketplace Bot!\nUse /help for commands"
    await update.message.reply_text(text)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "/start - Start\n/become_consultant - Register as consultant\n/my_consultations - View your consultations\n/payment - Payment info\n/help - Help"
    await update.message.reply_text(text)

async def become_consultant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if db.get_user_role(user_id) == 'consultant':
        await update.message.reply_text("You're already a consultant!")
        return
    text = "To become a consultant, please provide your credentials and specialization."
    await update.message.reply_text(text)

async def my_consultations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    consultations = db.get_user_consultations(user_id)
    if not consultations:
        await update.message.reply_text("No consultations found.")
        return
    text = "Your Consultations:\n"
    for c in consultations:
        text += f"ID: {c['id']}, Title: {c['title']}, Status: {c['status']}\n"
    await update.message.reply_text(text)

async def payment_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Payment Methods:\n- Credit Card\n- Bank Transfer\n- PayPal\nFee: 10% platform, 90% consultant payout"
    await update.message.reply_text(text)

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Message from {update.effective_user.id}: {update.message.text}")
    await update.message.reply_text("Thanks! Use /help for commands.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("become_consultant", become_consultant))
    app.add_handler(CommandHandler("my_consultations", my_consultations))
    app.add_handler(CommandHandler("payment", payment_info))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    logger.info("Starting bot...")
    app.run_polling()

if __name__ == '__main__':
    main()
