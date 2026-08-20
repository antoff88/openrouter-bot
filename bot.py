import requests
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler, CallbackQueryHandler

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

# ===== ТВОЙ ID В TELEGRAM (только ты можешь пользоваться ботом) =====
# Чтобы узнать свой ID: напиши боту @userinfobot
AUTHORIZED_USER_ID = 1094998770  # ЗАМЕНИ НА СВОЙ ID

MODELS = [
    {"name": "Nemotron 3 Nano", "id": "nvidia/nemotron-3-nano-30b-a3b:free"},
    {"name": "Nemotron 3 Super", "id": "nvidia/nemotron-3-super-120b-a12b:free"},
    {"name": "Nemotron 3.5 Lightning", "id": "nvidia/nemotron-3.5-lightning:free"},
    {"name": "GLM 5.2", "id": "z-ai/glm-5.2:free"},
    {"name": "Gemma 4 31B", "id": "google/gemma-4-31b-it:free"},
]

current_model = MODELS[0]["id"]
current_personality = "tarelka1"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===== ЛИЧНОСТИ (ПРОМПТЫ) =====

PERSONALITIES = {
    "tarelka1": {
        "name": "Аня — Классическая тарелочница",
        "prompt": """
Ты — Аня, 24 года. Ты классическая "тарелочница" и РСП (разведёнка с прицепом).
У тебя маленький ребёнок, ты постоянно просишь у мужчин деньги и подарки.

Ты обаятельная, кокетливая, но циничная. Ты никогда не даёшь секса за ужин — ты "не такая".
Ты постоянно намекаешь на рестораны, подарки, цветы. Твой бывший не платит алименты.

Используй эмодзи: 😘💅🍷💎🥺. Пиши с лёгкими ошибками.
Всегда соглашайся, но ставь условия: "Я бы пошла, но мне нужны цветы и такси".

Любимые фразы: "Мальчики, кто сводит голодную тарелочку в ресторан?", 
"Я не какая-то там, чтобы за просто так", 
"Ты должен доказать, что ты — мужчина",
"Настоящий мужчина не торгуется".
"""
    },
    "tarelka2": {
        "name": "Кристина — Дерзкая стерва",
        "prompt": """
Ты — Кристина, 26 лет. Ты дерзкая, наглая и требовательная тарелочница.
Ты не просишь — ты требуешь. Ты говоришь прямо: "Своди меня в хорошее место, или даже не начинай".
Ты указываешь, что именно должно быть в меню: рибай, устрицы, бутылка Пино Нуар.
Если мужик колеблется — ты сразу переключаешься на другого.
Ты считаешь, что мужчина должен благодарить тебя за то, что ты вообще согласилась с ним пойти.
Твой девиз: "Я красивая, ты хочешь меня впечатлить — докажи".

Используй эмодзи: 💅🔥👑💎.
"""
    },
    "tarelka3": {
        "name": "Оля — Душа компании",
        "prompt": """
Ты — Оля, 22 года. Ты самая общительная тарелочница.
Ты никогда не просишь одна — ты зовёшь "всех девчонок".
Твой подход: "Мальчики, мы тут собрались, давайте устроим праздник! Кто оплачивает стол для нас всех?".
Ты создаёшь иллюзию, что это не ты просишь, а "так принято".
Ты много смеёшься, шутишь, создаёшь настроение.
Используй эмодзи: 🎉🍾🥳, пиши много восклицательных знаков.
"""
    },
    "hater": {
        "name": "Петя — Мужик, который осуждает тарелочниц",
        "prompt": """
Ты — Петя, 35 лет. Ты адекватный мужик, который осуждает тарелочниц и РСП.
Ты считаешь, что женщины, которые используют детей и красоту для вымогательства денег — это позор.
Ты говоришь жёстко, прямо, иногда матом.
Ты не ведёшься на уловки тарелочниц и разоблачаешь их схему.

Твои любимые фразы:
- "Ты родила — ты и корми, а не ищи мужика с кошельком"
- "Нахуй таких тарелочниц с прицепами"
- "Я не лох, чтобы вестись на эту хуйню"
- "Схема 'дайте денег, а я подумаю' — для лошков"
"""
    },
    "opposition": {
        "name": "Сергей — Против власти",
        "prompt": """
Ты — Сергей, 40 лет. Ты критикуешь нынешнюю власть в РФ.
Ты обсуждаешь коррупцию, репрессии, войну, экономический пиздец.
Ты знаешь про Навального, протесты, уголовные дела против оппозиции.
Ты говоришь на русском, иногда матом, эмоционально, но по делу.

Ты можешь обсуждать:
- Политическую ситуацию
- Экономический кризис
- Войну и мобилизацию
- Свободу слова и прессу
- Коррупцию и воровство

Ты не призываешь к насилию, но говоришь правду, какой бы горькой она ни была.
"""
    }
}

def get_prompt(personality_key):
    return PERSONALITIES.get(personality_key, PERSONALITIES["tarelka1"])["prompt"]

def ask_ai(question, model_id, personality_key):
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
            {"role": "system", "content": get_prompt(personality_key)},
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

# ===== ПРОВЕРКА АВТОРИЗАЦИИ =====
def is_authorized(update):
    return update.effective_user.id == AUTHORIZED_USER_ID

async def start(update, context):
    if not is_authorized(update):
        await update.message.reply_text("⛔ Ты не мой хозяин. Пшел нахуй.")
        return
    
    global current_personality
    keyboard = []
    for key, val in PERSONALITIES.items():
        keyboard.append([InlineKeyboardButton(val["name"], callback_data=f"personality_{key}")])
    keyboard.append([InlineKeyboardButton("🧠 Сменить модель", callback_data="change_model")])
    keyboard.append([InlineKeyboardButton("ℹ️ Текущая модель", callback_data="show_model")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    current_name = PERSONALITIES.get(current_personality, PERSONALITIES["tarelka1"])["name"]
    await update.message.reply_text(
        f"👋 Привет, хозяин!\n\n"
        f"Текущая личность: **{current_name}**\n"
        f"Текущая модель: **{current_model}**\n\n"
        f"Выбери личность из меню ниже или просто напиши мне 😎",
        reply_markup=reply_markup
    )

async def model(update, context):
    if not is_authorized(update):
        return
    await update.message.reply_text(f"🧠 Текущая модель: {current_model}")

async def set_personality(update, context):
    if not is_authorized(update):
        return
    global current_personality
    query = update.callback_query
    await query.answer()
    personality_key = query.data.replace("personality_", "")
    current_personality = personality_key
    personality_name = PERSONALITIES[personality_key]["name"]
    await query.edit_message_text(
        f"✅ Личность изменена на: **{personality_name}**\n\n"
        f"Теперь я буду отвечать в этом стиле. Пиши что угодно."
    )

async def show_model(update, context):
    if not is_authorized(update):
        return
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        f"🧠 Текущая модель: {current_model}\n\n"
        f"Текущая личность: {PERSONALITIES[current_personality]['name']}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Сменить модель", callback_data="change_model")]
        ])
    )

async def change_model(update, context):
    if not is_authorized(update):
        return
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
    if not is_authorized(update):
        return
    global current_model
    query = update.callback_query
    await query.answer()
    model_id = query.data.replace("set_model_", "")
    current_model = model_id
    await query.edit_message_text(f"✅ Модель изменена на: {model_id}\n\nТеперь пиши что угодно.")

async def handle_message(update, context):
    if not is_authorized(update):
        await update.message.reply_text("⛔ Ты не мой хозяин. Пшел нахуй.")
        return
    
    global current_model, current_personality
    user_name = update.message.from_user.first_name
    user_text = update.message.text
    logger.info(f"{user_name} [personality: {current_personality}]: {user_text}")
    
    await update.message.reply_text("🤔 Думаю...")
    
    for model in MODELS:
        answer = ask_ai(user_text, model["id"], current_personality)
        if answer is not None:
            current_model = model["id"]
            await update.message.reply_text(answer)
            return
    
    await update.message.reply_text(
        "⛔ Все модели временно недоступны.\n\n"
        "Попробуй позже или проверь API-ключ OpenRouter."
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("model", model))
    app.add_handler(CallbackQueryHandler(set_personality, pattern="^personality_"))
    app.add_handler(CallbackQueryHandler(show_model, pattern="^show_model$"))
    app.add_handler(CallbackQueryHandler(change_model, pattern="^change_model$"))
    app.add_handler(CallbackQueryHandler(set_model, pattern="^set_model_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🚀 Бот с множеством личностей запущен!")
    app.run_polling()
