import asyncio
import io
import logging
import random
import sqlite3
import time
from PIL import Image, ImageDraw, ImageFont, ImageOps
import nest_asyncio

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, Filter
from aiogram.types import BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_START_TIME = int(time.time())
nest_asyncio.apply()

BOT_TOKEN = "8153436740:AAHi1c9jOZA6-prGMvP6b-Rv-KnrXZRROuE"

# ⚠️ Список айди владельцев бота
OWNER_IDS = [2076983944, 5998401091]

# Имя вашего файла аватарки в папке с ботом
LOCAL_AVATAR_PATH = "мабой пик ава (из парной со стрилкой).png"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# --- Кастомный фильтр проверки владельцев бота ---
class IsOwner(Filter):
    async def __call__(self, message: types.Message) -> bool:
        return message.from_user is not None and message.from_user.id in OWNER_IDS


# --- Конфигурация и константы ---
DEFAULT_CHANCE = 25
ALLOWED_CHANCES = [0, 10, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100]

MULTI_MSG_CHANCE = 0.25
MEDIA_REPLY_CHANCE = 0.30
EMOJI_CHANCE = 0.3
TRIGGER_CHANCE = 1.0
PHOTO_CAPTION_CHANCE = 0.4
CHOICE_GAME_CHANCE = 0.15

MAX_TIME_GAP = 3600

SEPARATORS = [
    "... ",
    "~ ",
    " ",
    "\n",
    " | ",
    " блять ",
    " сука ",
    " ну этот ",
    " типа ",
    " *думает* ",
    " эм-м.. ",
    " крч ",
    " и ",
    " бляяяяяя ",
    " сосо ",
    " я ",
]
START_ANNOUNCEMENT = "‼️Внимание-Внимание, МаБойЧик на связи‼️"

EMOJI_LIST = [
    "🐷",
    "😡😡😡",
    "💀",
    "🤡",
    "👻",
    "💩",
    "😈",
    "❤",
    "💦",
    "💪💪💪",
    "🐶",
    "✌️🤓",
    "☠️☠️☠️",
    "🖕",
    " *хитро улыбается*",
    " *подмигивает* ",
    " *делает милое личико* ",
    " *топает ножкой* ",
    " *хмыкнул и обиженно отвернулся* ",
    " *пиздит тебя* ",
    " *кусает за ногу* ",
    " *показывает 🖕* ",
    " блять",
    "я так говорю😉😉",
    ", понимаешь???",
    "))))",
    "XDxD",
]

STICKER_RESPONSES = [
    "УДАЛИ ЭТОТ ПОЗОР",
    "вау, это прекрасно!",
    "👍",
    "Мой любимый стикер кста.",
    "да пошел ты нахуй",
    "М-М-мм~ ✨🥵",
]
PHOTO_RESPONSES = [
    "да всем насрать.",
    "📸",
    "Красава",
    "Осеменить✨",
    "вырвите мне глаза нахуй...",
]
VIDEO_RESPONSES = [
    "Сорян сложно смотреть, когда одна рука занята))😉",
    "бля какую же хуйню ты сейчас скинул...",
    "🍿",
    "Absolute cinema!!!",
]
GIF_RESPONSES = [
    "Херня гифка, у меня лучше.",
    "🔥",
    "Спасибо",
    "Сохранить-сохранить",
    "бля удали это нахуй чувырла",
]
VOICE_RESPONSES = [
    "Заткнись нахуй, никто твой высер слушать не будет!!!",
    "Опять пукает...",
    "пикми щовель выдавливает голосок",
    "🔊 Включил на полную громкость",
    "да тише 🙏🙏🙏",
]

TRIGGER_RESPONSES = {
    "мабойчик": [
        "Да-да, что те надо?",
        "Да че те надо заебал(-а)?",
        "На связи!",
    ],
    "стрилка": [
        "в жопе пиписька",
        "CAACAgIAAxkBAAEDzK9qaL1Jg4U-i_xsml0FrKR8wIMFkAAC54MAAqYa8UlPvX90Er6B-z0E",
    ],
    "админ": [
        "Админа нет, я за него 😈",
        "админы хуесосы",
        "CAACAgIAAxkBAAED0INqcizgJiqrQJe_267Z6ERr9vSe4gAC2UoAAgLI8EiMR2d5kFp7lD0E",
    ],
    "@itsd4wg": [
        "гога нюхает яйца",
        "моя любимая лизочка",
        "CAACAgIAAxkBAAEDzKtqaL0ZIwfRu7phjVtbpdycRBB9hAACwI4AAr3UkUj66IrC5PiTgj0E",
    ],
    "почему ты такой": ["потому что тебя это ебать не должно.", "Я идеализирован"],
    "забаньте": ["может сука тебя забанить, мымра?", "нет, я не разрешаю."],
    "ты свин": ["рот свой закрыла пиздючка", "не подписывай меня своим видом)"],
    "пошел нахуй": [
        "CAACAgIAAxkBAAEDzJ1qaLU046_G5YWVchCEUEDpCMdcSgACbpoAAl9ySEpun819mUe-Fz0E",
        "пошёл нахуй",
        "нет,ты пошел нахуй",
        "Да сама нахуй иди, ебашака😉",
    ],
    "забанить": ["может сука тебя забанить, мимра?", "хуй тебе😈"],
    "идиотина": ["сама такая ебани сыр!!!", "завали ебучку блять"],
    "твар": ["не пукай мне тут 👻", "тварь тут только твоя мамааша"],
    "тварь": ["не пукай мне тут 👻", "тварь тут только твоя мамааша"],
    "бан": [
        "Хуй тебе пизда непобритая😈😈😈",
        "CAACAgIAAxkBAAED0Idqci34rqkeccezyiALtPYh2Er-lAACAwAD7EI1H9t1-zREr9jWPQQ",
    ],
    "тупица": [
        "да рот свой закрой со своей тупицей",
        "CAACAgIAAxkBAAED0phqd0VelZPFjqbB3MCg_5cY4ORhggACTC8AAs_CGErRE5fxN63xsD0E",
    ],
    "сирота": [
        "не принуждай меня опускаться на твой ничтожный уровень, где у тебя дуры отца и матери нет, блин 😤",
        "CAACAgIAAxkBAAEhgRpqexwdUeK_0jaqSbmr4kke69RQtwACD1kAAieJgUtwbgjijqJefT0E",
    ],
}

DEFAULT_MESSAGES = ["🤔", "Тишина в зале..."]

last_chat_messages: dict[int, tuple[str, float]] = {}

# --- Работа с базой данных (SQLite) ---
DB_NAME = "bot_memory.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                media_type TEXT DEFAULT 'text'
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context_pairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                trigger_text TEXT NOT NULL,
                response_text TEXT NOT NULL,
                media_type TEXT DEFAULT 'text'
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_settings (
                chat_id INTEGER PRIMARY KEY,
                response_chance INTEGER DEFAULT 25
            )
        """)
        conn.commit()


def save_message(chat_id: int, content: str, media_type: str = "text"):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (chat_id, text, media_type) VALUES (?, ?,"
            " ?)",
            (chat_id, content, media_type),
        )
        conn.commit()


def save_context_pair(
    chat_id: int,
    trigger_text: str,
    response_text: str,
    media_type: str = "text",
):
    trigger_clean = trigger_text.strip().lower()
    response_clean = response_text.strip()
    if not trigger_clean or not response_clean:
        return
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM context_pairs WHERE chat_id = ? AND trigger_text ="
            " ? AND response_text = ?",
            (chat_id, trigger_clean, response_clean),
        )
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO context_pairs (chat_id, trigger_text,"
                " response_text, media_type) VALUES (?, ?, ?, ?)",
                (chat_id, trigger_clean, response_clean, media_type),
            )
            conn.commit()


def find_context_responses(chat_id: int, text: str) -> list[tuple[str, str]]:
    clean_text = text.strip().lower()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT response_text, media_type FROM context_pairs WHERE chat_id"
            " = ? AND trigger_text = ?",
            (chat_id, clean_text),
        )
        return cursor.fetchall()


def delete_target_messages(chat_id: int, content: str) -> int:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM messages WHERE chat_id = ? AND text = ?",
            (chat_id, content),
        )
        deleted_msgs = cursor.rowcount
        cursor.execute(
            "DELETE FROM context_pairs WHERE chat_id = ? AND (trigger_text = ?"
            " OR response_text = ?)",
            (chat_id, content.lower(), content),
        )
        deleted_pairs = cursor.rowcount
        conn.commit()
        return deleted_msgs + deleted_pairs


def get_chat_text_messages(chat_id: int) -> list[str]:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT text FROM messages WHERE chat_id = ? AND media_type ="
            " 'text'",
            (chat_id,),
        )
        return [row[0] for row in cursor.fetchall()]


def get_random_chat_media(chat_id: int) -> tuple[str, str] | None:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT text, media_type FROM messages WHERE chat_id = ? AND"
            " media_type != 'text' ORDER BY RANDOM() LIMIT 1",
            (chat_id,),
        )
        row = cursor.fetchone()
        return (row[0], row[1]) if row else None


def get_chat_stats(chat_id: int) -> dict:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM messages WHERE chat_id = ? AND media_type ="
            " 'text'",
            (chat_id,),
        )
        text_count = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM messages WHERE chat_id = ? AND media_type !="
            " 'text'",
            (chat_id,),
        )
        media_count = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM context_pairs WHERE chat_id = ?", (chat_id,)
        )
        context_count = cursor.fetchone()[0]
        return {
            "text": text_count,
            "media": media_count,
            "context": context_count,
            "total": text_count + media_count,
        }


def get_all_active_chats() -> list[int]:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM chat_settings")
        return [row[0] for row in cursor.fetchall()]


def clear_chat_messages(chat_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        cursor.execute(
            "DELETE FROM context_pairs WHERE chat_id = ?", (chat_id,)
        )
        conn.commit()


def get_chat_chance(chat_id: int) -> int:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT response_chance FROM chat_settings WHERE chat_id = ?",
            (chat_id,),
        )
        row = cursor.fetchone()
        if row:
            return row[0]
        cursor.execute(
            "INSERT INTO chat_settings (chat_id, response_chance) VALUES (?,"
            " ?)",
            (chat_id, DEFAULT_CHANCE),
        )
        conn.commit()
        return DEFAULT_CHANCE


def should_respond(chat_id: int) -> bool:
    chance = get_chat_chance(chat_id)
    if chance <= 0:
        return False
    if chance >= 100:
        return True
    return random.randint(1, 100) <= chance


def set_chat_chance(chat_id: int, new_chance: int):
    get_chat_chance(chat_id)
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE chat_settings SET response_chance = ? WHERE chat_id = ?",
            (new_chance, chat_id),
        )
        conn.commit()


# --- Вспомогательные функции ---
def attach_emoji(text: str) -> str:
    if random.random() < EMOJI_CHANCE:
        return f"{text} {random.choice(EMOJI_LIST)}"
    return text


def check_triggers(text: str) -> str | None:
    if random.random() > TRIGGER_CHANCE:
        return None
    lowered_text = text.lower()
    for trigger, responses in TRIGGER_RESPONSES.items():
        if trigger in lowered_text:
            return random.choice(responses)
    return None


def generate_text_response(chat_id: int) -> str:
    messages = get_chat_text_messages(chat_id)
    if not messages:
        base_reply = random.choice(DEFAULT_MESSAGES)
    elif random.random() < MULTI_MSG_CHANCE and len(messages) >= 2:
        count_to_pick = min(random.randint(2, 5), len(messages))
        chosen_messages = random.sample(messages, count_to_pick)
        result = chosen_messages[0]
        for i in range(1, len(chosen_messages)):
            result += random.choice(SEPARATORS) + chosen_messages[i]
        base_reply = result
    else:
        base_reply = random.choice(messages)
    return attach_emoji(base_reply)


async def send_media_by_type(
    chat_id: int,
    file_id: str,
    media_type: str,
    caption: str | None = None,
    reply_to_message_id: int | None = None,
):
    if media_type == "sticker":
        await bot.send_sticker(
            chat_id, file_id, reply_to_message_id=reply_to_message_id
        )
    elif media_type == "photo":
        await bot.send_photo(
            chat_id,
            file_id,
            caption=caption,
            reply_to_message_id=reply_to_message_id,
        )
    elif media_type == "video":
        await bot.send_video(
            chat_id,
            file_id,
            caption=caption,
            reply_to_message_id=reply_to_message_id,
        )
    elif media_type == "animation":
        await bot.send_animation(
            chat_id,
            file_id,
            caption=caption,
            reply_to_message_id=reply_to_message_id,
        )
    elif media_type == "voice":
        await bot.send_voice(
            chat_id,
            file_id,
            caption=caption,
            reply_to_message_id=reply_to_message_id,
        )


# --- Генерация цитаты-картинки (Без блюра, с 40% затемнения) ---
async def generate_quote_image(text: str) -> BufferedInputFile | None:
    try:
        width, height = 700, 400

        # 1. Загрузка исходного изображения
        try:
            raw_avatar = Image.open(LOCAL_AVATAR_PATH).convert("RGBA")
        except FileNotFoundError:
            logging.error(f"Файл {LOCAL_AVATAR_PATH} не найден!")
            return None

        # 2. ФОН: Растягиваем аватар на весь холст БЕЗ размытия
        bg_image = ImageOps.fit(
            raw_avatar, (width, height), method=Image.Resampling.LANCZOS
        )

        # 3. Накладываем 5% черного затемнения
        dark_overlay = Image.new(
            "RGBA", (width, height), (0, 0, 0, int(255 * 0.5))
        )
        bg_image = Image.alpha_composite(bg_image, dark_overlay)

        image = bg_image.copy()
        draw = ImageDraw.Draw(image)

        # 4. Подбор шрифта
        font_path = None
        for font_name in ["comicbd.ttf", "impact.ttf", "arialbd.ttf", "arial.ttf"]:
            try:
                ImageFont.truetype(font_name, 10)
                font_path = font_name
                break
            except OSError:
                continue

        if font_path:
            quote_font = ImageFont.truetype(font_path, 65)
            text_font = ImageFont.truetype(font_path, 26)
            watermark_font = ImageFont.truetype(font_path, 18)
        else:
            quote_font = text_font = watermark_font = ImageFont.load_default()

        # Кавычки по углам
        draw.text((220, 30), "“", font=quote_font, fill=(255, 255, 255, 200))
        draw.text((620, 300), "”", font=quote_font, fill=(255, 255, 255, 200))

        # 5. Круглая аватарка слева
        avatar_img = raw_avatar.resize((160, 160), Image.Resampling.LANCZOS)
        mask = Image.new("L", (160, 160), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 160, 160), fill=255)

        image.paste(avatar_img, (40, 100), mask)

        # 6. Подписи слева снизу
        draw.text(
            (40, 290),
            "© Maboychik",
            font=watermark_font,
            fill=(255, 255, 255, 255),
        )
        draw.text(
            (40, 315),
            "@fromXspeeLbot",
            font=watermark_font,
            fill=(200, 200, 200, 255),
        )

        # 7. Текст справа по центру
        max_width = 380
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=text_font)
            if bbox[2] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        line_height = text_font.getbbox("A")[3] + 8
        total_text_height = len(lines) * line_height
        start_y = (height - total_text_height) // 2

        for i, line in enumerate(lines):
            line_y = start_y + (i * line_height)
            draw.text(
                (250, line_y), line, font=text_font, fill=(255, 255, 255, 255)
            )

        # 8. Сохранение
        final_image = image.convert("RGB")
        buffer = io.BytesIO()
        final_image.save(buffer, format="PNG")
        buffer.seek(0)
        return BufferedInputFile(buffer.getvalue(), filename="quote.png")

    except Exception as e:
        logging.error(f"Ошибка при создании цитаты: {e}")
        return None


# --- Обработчик Интерактивной игры "Персональный Выбор" ---
async def send_choice_game(incoming_message: types.Message):
    user = incoming_message.from_user
    username_mention = f"@{user.username}" if user.username else user.first_name

    text = (
        f"‼️Опачки! {username_mention} получил шанс стать ТЕМ, кто выберет мой следующий ответ, еби его НАХУЙ за ногу‼️"
    )

    kb = InlineKeyboardBuilder()
    kb.button(text="1️⃣", callback_data=f"choice:1:{user.id}")
    kb.button(text="2️⃣", callback_data=f"choice:2:{user.id}")
    kb.button(text="3️⃣", callback_data=f"choice:3:{user.id}")
    kb.adjust(3)

    await incoming_message.reply(text, reply_markup=kb.as_markup())


@dp.callback_query(F.data.startswith("choice:"))
async def handle_choice_callback(callback: types.CallbackQuery):
    _, choice_num, target_user_id = callback.data.split(":")

    if str(callback.from_user.id) != target_user_id:
        await callback.answer(
            "❌ Иди нахуй, это не твой выбор!",
            show_alert=True,
        )
        return

    await callback.answer()
    chat_id = callback.message.chat.id

    reply_to_msg_id = (
        callback.message.reply_to_message.message_id
        if callback.message.reply_to_message
        else None
    )

    try:
        await callback.message.delete()
    except Exception:
        pass

    # Отправляем строго 1 тип ответа
    outcome_type = random.choice(["quote", "media", "text"])

    if outcome_type == "quote":
        text_resp = generate_text_response(chat_id)
        quote_img = await generate_quote_image(text_resp)
        if quote_img:
            await bot.send_photo(
                chat_id, photo=quote_img, reply_to_message_id=reply_to_msg_id
            )
        else:
            await bot.send_message(
                chat_id, text_resp, reply_to_message_id=reply_to_msg_id
            )

    elif outcome_type == "media":
        random_media = get_random_chat_media(chat_id)
        if random_media:
            file_id, media_type = random_media
            caption_text = None

            if random.random() < PHOTO_CAPTION_CHANCE:
                text_msgs = get_chat_text_messages(chat_id)
                if text_msgs:
                    caption_text = attach_emoji(random.choice(text_msgs))

            await send_media_by_type(
                chat_id,
                file_id,
                media_type,
                caption=caption_text,
                reply_to_message_id=reply_to_msg_id,
            )
        else:
            text_resp = generate_text_response(chat_id)
            await bot.send_message(
                chat_id, text_resp, reply_to_message_id=reply_to_msg_id
            )

    elif outcome_type == "text":
        text_resp = generate_text_response(chat_id)
        await bot.send_message(
            chat_id, text_resp, reply_to_message_id=reply_to_msg_id
        )


# --- Анализатор и запоминатель контекста ---
def process_incoming_context(
    message: types.Message, current_content: str, media_type: str = "text"
):
    chat_id = message.chat.id
    now = time.time()

    if message.reply_to_message and message.reply_to_message.text:
        parent_text = message.reply_to_message.text.strip()
        save_context_pair(chat_id, parent_text, current_content, media_type)
        logging.info(
            f"🔗 [Контекст] Reply-связка: '{parent_text}' -> '{current_content}'"
        )
    elif chat_id in last_chat_messages:
        prev_text, prev_time = last_chat_messages[chat_id]
        if now - prev_time <= MAX_TIME_GAP:
            save_context_pair(chat_id, prev_text, current_content, media_type)
            logging.info(
                "🔗 [Контекст] Последовательная связка:"
                f" '{prev_text}' -> '{current_content}'"
            )

    if message.text:
        last_chat_messages[chat_id] = (message.text.strip(), now)


# --- Главный контроллер ответов ---
async def process_and_respond(
    incoming_message: types.Message, default_response_pool: list[str] = None
):
    chat_id = incoming_message.chat.id

    if incoming_message.date.timestamp() < BOT_START_TIME:
        return

    # 1. Триггеры
    if incoming_message.text:
        trigger_reply = check_triggers(incoming_message.text)
        if trigger_reply:
            if trigger_reply.startswith("CAAC"):
                await incoming_message.reply_sticker(trigger_reply)
            else:
                await incoming_message.reply(attach_emoji(trigger_reply))
            return

    # 2. Шанс ответа чата
    if not should_respond(chat_id):
        return

    # 3. Шанс запустить Игру с Выбором (50%)
    if random.random() < CHOICE_GAME_CHANCE:
        await send_choice_game(incoming_message)
        return

    caption_text = None
    if random.random() < PHOTO_CAPTION_CHANCE:
        text_msgs = get_chat_text_messages(chat_id)
        if text_msgs:
            caption_text = attach_emoji(random.choice(text_msgs))

    # 4. Умный контекст
    if incoming_message.text:
        context_matches = find_context_responses(
            chat_id, incoming_message.text
        )
        if context_matches:
            resp_content, resp_media_type = random.choice(context_matches)
            if resp_media_type == "text":
                await incoming_message.reply(attach_emoji(resp_content))
            else:
                await send_media_by_type(
                    chat_id,
                    resp_content,
                    resp_media_type,
                    caption=caption_text,
                    reply_to_message_id=incoming_message.message_id,
                )
            return

    # 5. Медиа из базы
    random_media = get_random_chat_media(chat_id)
    if random_media and random.random() < MEDIA_REPLY_CHANCE:
        file_id, media_type = random_media
        await send_media_by_type(
            chat_id,
            file_id,
            media_type,
            caption=caption_text,
            reply_to_message_id=incoming_message.message_id,
        )
        return

    # 6. Реакции на форматы / Случайный текст
    if default_response_pool:
        reply_text = random.choice(default_response_pool)
        await incoming_message.reply(attach_emoji(reply_text))
    else:
        reply_text = generate_text_response(chat_id)
        await bot.send_message(
            chat_id, reply_text, reply_to_message_id=incoming_message.message_id
        )


# --- Команды ---
@dp.message(Command("db", "database"), IsOwner())
async def cmd_get_db_stats(message: types.Message):
    stats = get_chat_stats(message.chat.id)
    text_res = (
        "📊 **Состояние базы данных для этого чата:**\n\n"
        f"💬 Текстовых сообщений: `{stats['text']}`\n"
        f"🖼 Сохранённых медиа: `{stats['media']}`\n"
        f"🔗 Контекстных связей: `{stats['context']}`\n"
        f"📈 **Всего сохраненных записей:** `{stats['total']}`"
    )
    await message.reply(text_res, parse_mode="Markdown")


@dp.message(Command("del", "delete"), IsOwner())
async def cmd_delete_message(message: types.Message):
    if not message.reply_to_message:
        await message.reply(
            "⚠️ Ответьте этой командой (`/del`) на сообщение, которое нужно"
            " удалить из базы."
        )
        return

    target_msg = message.reply_to_message
    content_to_delete = None

    if target_msg.text:
        content_to_delete = target_msg.text.strip()
    elif target_msg.caption:
        content_to_delete = target_msg.caption.strip()
    elif target_msg.sticker:
        content_to_delete = target_msg.sticker.file_id
    elif target_msg.animation:
        content_to_delete = target_msg.animation.file_id
    elif target_msg.photo:
        content_to_delete = target_msg.photo[-1].file_id
    elif target_msg.video:
        content_to_delete = target_msg.video.file_id
    elif target_msg.voice:
        content_to_delete = target_msg.voice.file_id

    if not content_to_delete:
        await message.reply(
            "⚠️ Не удалось извлечь содержимое сообщения для удаления."
        )
        return

    deleted_count = delete_target_messages(message.chat.id, content_to_delete)
    if deleted_count > 0:
        await message.reply(
            f"🗑 Успешно удалено совпадений из базы: **{deleted_count}** шт.",
            parse_mode="Markdown",
        )
    else:
        await message.reply("❓ Такого сообщения не было в базе.")


@dp.message(Command("set_chance", "set_interval"), IsOwner())
async def cmd_set_chance(message: types.Message):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.reply(
            "⚠️ Укажите значение вероятности.", parse_mode="Markdown"
        )
        return
    val = int(args[1])
    if val not in ALLOWED_CHANCES:
        await message.reply(
            "⚠️ Допустимые значения вероятности: **0, 10, 20, 30, 40, 50, 60, 70,"
            " 80, 90, 100**%",
            parse_mode="Markdown",
        )
        return
    set_chat_chance(message.chat.id, val)
    await message.reply(
        f"✅ Вероятность ответов установлена на **{val}%**.", parse_mode="Markdown"
    )


@dp.message(Command("clear_db"), IsOwner())
async def cmd_clear_db(message: types.Message):
    clear_chat_messages(message.chat.id)
    await message.reply("🧹 Память сообщений этого чата очищена!")


# --- Хэндлеры сообщений ---
@dp.message(F.text & ~F.text.startswith("/"))
async def handle_text_message(message: types.Message):
    text = message.text.strip()
    if len(text) <= 300:
        save_message(message.chat.id, text, media_type="text")
        process_incoming_context(message, text, media_type="text")
    await process_and_respond(message)


@dp.message(F.sticker)
async def handle_sticker_message(message: types.Message):
    file_id = message.sticker.file_id
    save_message(message.chat.id, file_id, media_type="sticker")
    process_incoming_context(message, file_id, media_type="sticker")
    await process_and_respond(message, default_response_pool=STICKER_RESPONSES)


@dp.message(F.photo)
async def handle_photo_message(message: types.Message):
    file_id = message.photo[-1].file_id
    save_message(message.chat.id, file_id, media_type="photo")
    process_incoming_context(message, file_id, media_type="photo")
    await process_and_respond(message, default_response_pool=PHOTO_RESPONSES)


@dp.message(F.video)
async def handle_video_message(message: types.Message):
    file_id = message.video.file_id
    save_message(message.chat.id, file_id, media_type="video")
    process_incoming_context(message, file_id, media_type="video")
    await process_and_respond(message, default_response_pool=VIDEO_RESPONSES)


@dp.message(F.animation)
async def handle_animation_message(message: types.Message):
    file_id = message.animation.file_id
    save_message(message.chat.id, file_id, media_type="animation")
    process_incoming_context(message, file_id, media_type="animation")
    await process_and_respond(message, default_response_pool=GIF_RESPONSES)


@dp.message(F.voice)
async def handle_voice_message(message: types.Message):
    file_id = message.voice.file_id
    save_message(message.chat.id, file_id, media_type="voice")
    process_incoming_context(message, file_id, media_type="voice")
    await process_and_respond(message, default_response_pool=VOICE_RESPONSES)


async def notify_start():
    active_chats = get_all_active_chats()
    for chat_id in active_chats:
        try:
            await bot.send_message(chat_id, attach_emoji(START_ANNOUNCEMENT))
        except Exception as e:
            logging.warning(
                f"Не удалось отправить анонс в чат {chat_id}: {e}"
            )


async def main():
    global BOT_START_TIME
    init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    BOT_START_TIME = int(time.time())
    await notify_start()
    print(f"Бот запущен в {BOT_START_TIME}...")
    await dp.start_polling(bot, drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())