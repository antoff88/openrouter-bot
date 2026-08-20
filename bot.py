import requests
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler

# ===== ТОКЕНЫ =====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
MODEL = "deepseek/deepseek-r1:free"

# ===== ЛОГИ =====
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ask_ai(question):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Ты — дерзкий собеседник. Отвечай коротко, с юмором, иногда матом."},
            {"role": "user", "content": question}
        ]
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        return f"⛔ Ошибка API: {r.status_code}"
    except Exception as e:
        return f"⚠️ Ошибка: {str(e)}"

async def start(update, context):
    await update.message.reply_text("Ну чё, погнали пиздеть? 😎")

async def handle(update, context):
    user = update.message.from_user.first_name
    text = update.message.text
    logger.info(f"{user}: {text}")
    await update.message.reply_text("🤔 Думаю...")
    answer = ask_ai(text)
    await update.message.reply_text(answer)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    logger.info("🚀 Бот запущен на Render!")
    app.run_polling()
