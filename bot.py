import requests
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler, CallbackQueryHandler

# ===== ТОКЕНЫ =====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

# ===== СПИСОК РАБОЧИХ БЕСПЛАТНЫХ МОДЕЛЕЙ (из твоего лога) =====
MODELS = [
    {"name": "Nemotron 3 Nano", "id": "nvidia/nemotron-3-nano-30b-a3b:free"},
    {"name": "Nemotron 3 Super", "id": "nvidia/nemotron-3-super-120b-a12b:free"},
    {"name": "Nemotron 3 Nano Omni", "id": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"},
    {"name": "GLM 5.2", "id": "z-ai/glm-5.2:free"},
    {"name": "Laguna XS 2.1", "id": "poolside/laguna-xs-2.1:free"},
    {"name": "LFM2.5", "id": "liquid/lfm-2.5-2.6b:free"},
    {"name": "Gemma 4 26B", "id": "google/gemma-4-26b-a4b-it:free"},
    {"name": "Gemma 4 31B", "id": "google/gemma-4-31b-it:free"},
]

current_model = MODELS[0]["id"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ask_ai(question, model_id):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "HTTP-Referer": "https://t.me/openrouter881_bot",
        "X-Title": "OpenRouter Bot",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": "Ты — дерзкий собеседник. Отвечай коротко, с юмором, иногда матом. Без воды. Максимум 2-3 предложения."},
            {"role": "user", "content": question}
        ]
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        else:
            logger.error(f"OpenRouter error: {r.status_code} - {r.text}")
            return None
    except Exception as e:
        logger.error(f"OpenRouter exception: {e}")
        return None

async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("🧠 Сменить модель", callback_data="change_model")],
        [InlineKeyboardButton("ℹ️ Текущая модель", callback_data="show_model")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Ну чё, погнали пиздеть? 😎\n\n"
        f"🧠 Текущая модель: {current_model}\n"
        "Если одна модель не работает — попробую другую.",
        reply_markup=reply_markup
    )

async def show_model(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        f"🧠 Текущая модель: {current_model}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Сменить", callback_data="change_model")]
        ])
    )

async def change_model(update, context):
    query = update.callback_query
    await query.answer()
    keyboard = []
    for m in MODELS:
        keyboard.append([InlineKeyboardButton(m["name"], callback_data=f"set_model_{m['id']}")])
    await query.edit_message_text(
        "Выбери модель:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def set_model(update, context):
    global current_model
    query = update.callback_query
    await query.answer()
    model_id = query.data.replace("set_model_", "")
    current_model = model_id
    await query.edit_message_text(f"✅ Модель изменена.\n\nТеперь пиши что угодно.")

async def handle_message(update, context):
    global current_model
    user_name = update.message.from_user.first_name
    user_text = update.message.text
    logger.info(f"{user_name}: {user_text}")
    
    await update.message.reply_text("🤔 Думаю...")
    
    # Пробуем все модели по очереди
    tried_models = []
    for model in MODELS:
        tried_models.append(model["name"])
        answer = ask_ai(user_text, model["id"])
        if answer is not None:
            current_model = model["id"]
            await update.message.reply_text(answer)
            return
    
    await update.message.reply_text(
        "⛔ Все модели временно недоступны.\n"
        f"Проверено: {', '.join(tried_models)}\n\n"
        "Попробуй позже или проверь API-ключ OpenRouter."
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_model, pattern="^show_model$"))
    app.add_handler(CallbackQueryHandler(change_model, pattern="^change_model$"))
    app.add_handler(CallbackQueryHandler(set_model, pattern="^set_model_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🚀 Бот с автопереключением моделей запущен!")
    app.run_polling()
