🤖 Бот openrouter881_bot
📌 ОБЩАЯ ИНФОРМАЦИЯ
Что	Где
Имя бота	@openrouter881_bot
Telegram токен	8958751620:AAGpuspg7vSen5vS3xO1JRFmJO5HBFiQ6tA
OpenRouter API ключ	sk-or-v1-1399671...
Репозиторий на GitHub	https://github.com/antoff88/openrouter-bot
Хостинг	Render (Web Service)
Твой Telegram ID	1094998770
Кто может писать	Только ты (в личке) + все (в группе)
📁 ГДЕ ЛЕЖИТ ИСХОДНИК

На ноутбуке:
bash

/home/a1/Личное/1_Разработка/II/openrouter-bot/
├── bot.py
├── requirements.txt
├── render.yaml
└── .gitignore

🔧 КАК ИЗМЕНИТЬ ЛИЧНОСТЬ

    Открой bot.py

    Найди блок PERSONALITIES = { ... }

    Добавь/измени/удали личность по шаблону:

python

"ключ": {
    "name": "Имя — Описание",
    "prompt": """
Ты — персонаж. Твой характер, стиль, фразы.
...
"""
},

    Сохрани файл

🧠 КАК ДОБАВИТЬ НОВУЮ МОДЕЛЬ

    Открой bot.py

    Найди список MODELS

    Добавь новую модель:

python

{"name": "Название", "id": "имя/модели"},

    Посмотреть доступные модели можно командой:

bash

curl https://openrouter.ai/api/v1/models | grep -E '"id".*:free'

🚀 КАК ЗАГРУЗИТЬ ИЗМЕНЕНИЯ НА РЕНДЕР
1. Закоммитить и запушить на GitHub
bash

cd /home/a1/Личное/1_Разработка/II/openrouter-bot
git add .
git commit -m "Краткое описание изменений"
git push

2. Перезапустить на Render

    Зайди на dashboard.render.com

    Найди сервис openrouter-bot

    Нажми "Deploy" → "Deploy latest commit"

    Подожди 2–3 минуты

📌 ГДЕ ХРАНИТЬ ТОКЕНЫ (ВАЖНО!)

Никогда не клади токены в render.yaml или код!

Они уже добавлены в панели Render:

    Зайди в dashboard.render.com

    Выбери сервис → Environment

    Там лежат:

        TELEGRAM_TOKEN

        OPENROUTER_KEY

Чтобы изменить токен — отредактируй значение и нажми Save Changes.
📋 ДОСТУПНЫЕ КОМАНДЫ БОТА
Команда	Что делает
/start	Показывает текущую личность и модель
/help	Все команды
/personality	Выбор личности (кнопки)
/model	Выбор модели (кнопки)
🛠 ЧТО ДЕЛАТЬ, ЕСЛИ БОТ НЕ РАБОТАЕТ

    Проверить логи на Render:

        Зайди в сервис → Logs

    Проверить API ключ:
    bash

curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer ТВОЙ_КЛЮЧ" \
  -H "Content-Type: application/json" \
  -d '{"model": "nvidia/nemotron-3-nano-30b-a3b:free", "messages": [{"role": "user", "content": "Привет"}]}'

Проверить бота:
bash

curl https://api.telegram.org/botТОКЕН/getMe

✅ БЫСТРЫЙ ЧЕК-ЛИСТ
    ✅ Код лежит на ноутбуке
    ✅ Репозиторий на GitHub
    ✅ Бот живёт на Render
    ✅ Токены защищены в Environment
    ✅ Доступ есть только у тебя (в личке)
    ✅ В группах бот отвечает всем
