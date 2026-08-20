import requests
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler, CallbackQueryHandler

# ===== ТОКЕНЫ =====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

# ===== СПИСОК БЕСПЛАТНЫХ МОДЕЛЕЙ =====
MODELS = [
    {"name": "Gemini 2.0 Flash", "id": "google/gemini-2.0-flash-exp:free"},
    {"name": "GPT-4o Mini", "id": "openai/gpt-4o-mini"},
    {"name": "Phi-2", "id": "microsoft/phi-2"},
    {"name": "Llama 3 8B", "id": "meta-llama/llama-3-8b-instruct:free"},
    {"name": "Mistral 7B", "id": "mistralai/mistral-7b-instruct:free"},
    {"name": "DeepSeek R1", "id": "deepseek/deepseek-r1:free"},
]

# ===== ТЕКУЩАЯ МОДЕЛЬ (по умолчанию) =====
current_model = MODELS[0]["id"]

# ===== ЛОГИ =====
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ask_ai(question, model_id):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": "Ты — дерзкий собеседник. Отвечай коротко, с юмором, иногда матом. Без воды."},
            {"role": "user", "content": question}
        ]
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        else:
            return None
    except Exception as e:
        return None

async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("🧠 Сменить модель", callback_data="change_model")],
        [InlineKeyboardButton("ℹ️ Текущая модель", callback_data="show_model")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Ну чё, погнали пиздеть? 😎\n\n"
        "Просто пиши — я отвечу. Если одна модель не работает — попробую другую.\n\n"
        f"🧠 Текущая модель: {current_model}",
        reply_markup=reply_markup
    )

async def show_model(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        f"🧠 Текущая модель: {current_model}\n\n"
        "Если модель не отвечает, я автоматически переключусь на другую.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Сменить модель", callback_data="change_model")]
        ])
    )

async def change_model(update, context):
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    for m in MODELS:
        keyboard.append([InlineKeyboardButton(m["name"], callback_data=f"set_model_{m['id']}")])
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_to_start")])
    
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
    
    # Найдём название модели для красивого вывода
    model_name = model_id
    for m in MODELS:
        if m["id"] == model_id:
            model_name = m["name"]
            break
    
    await query.edit_message_text(
        f"✅ Модель изменена на: {model_name}\n\n"
        f"Теперь пиши что угодно — я отвечу.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Назад", callback_data="back_to_start")]
        ])
    )

async def back_to_start(update, context):
    query = update.callback_query
    await query.answer()
    await start(query.message, context)

async def handle_message(update, context):
    global current_model
    user_name = update.message.from_user.first_name
    user_text = update.message.text
    logger.info(f"{user_name}: {user_text}")
    
    await update.message.reply_text("🤔 Думаю...")
    
    # Пробуем текущую модель
    answer = ask_ai(user_text, current_model)
    
    if answer is None:
        # Если текущая модель не работает — перебираем все остальные
        logger.info(f"Модель {current_model} не ответила, переключаем...")
        for model in MODELS:
            if model["id"] == current_model:
                continue
            logger.info(f"Пробуем модель: {model['id']}")
            answer = ask_ai(user_text, model["id"])
            if answer is not None:
                current_model = model["id"]
                await update.message.reply_text(
                    f"⚠️ Модель автоматически переключена на: {model['name']}\n\n"
                    f"{answer}"
                )
                return
        
        # Если ни одна модель не работает
        await update.message.reply_text(
            "⛔ Все модели временно недоступны. Попробуй позже или выбери другую модель через /start."
        )
    else:
        await update.message.reply_text(answer)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_model, pattern="^show_model$"))
    app.add_handler(CallbackQueryHandler(change_model, pattern="^change_model$"))
    app.add_handler(CallbackQueryHandler(set_model, pattern="^set_model_"))
    app.add_handler(CallbackQueryHandler(back_to_start, pattern="^back_to_start$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🚀 Бот с автопереключением моделей запущен!")
    app.run_polling()
