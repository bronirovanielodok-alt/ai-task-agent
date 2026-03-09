"""
Telegram Bot для AI агента
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = "491092207:AAEYBQmJLZr3HrhSvRkurB2qQFYhL9aJPsg"

if not OPENAI_API_KEY:
    print("ERROR: Установите OPENAI_API_KEY")
    exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я AI бот. Напишите мне задачу.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Просто напишите задачу, и я её выполню!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    await update.message.reply_text("Думаю...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_message}],
            temperature=0.7
        )
        
        result = response.choices[0].message.content
        await update.message.reply_text(result)
        
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Бот запущен! Напишите ему в Telegram.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
