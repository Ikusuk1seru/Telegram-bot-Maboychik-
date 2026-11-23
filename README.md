# Telegram-bot-Maboychik-

Стек технологий
Язык: Python 3.10+

Telegram API: aiogram

База данных: sqlite3

Обработка изображений: Pillow (PIL)

Асинхронность: asyncio, nest_asyncio

Структура проекта
codemaboynew.py — основной файл с логикой бота, работой с БД, генератором изображений и хэндлерами.

bot_memory.db — локальная база данных SQLite (создаётся автоматически при запуске).

<мабой пик ава (из парной со стрилкой).png> — локальное изображение, указанное в LOCAL_AVATAR_PATH, для генерации цитат.

Запуск проекта
Установите зависимости:
pip install aiogram pillow nest-asyncio

Положите файл аватарки рядом со скриптом и проверьте путь в LOCAL_AVATAR_PATH.

Запустите бота:
python codemaboynew.py
