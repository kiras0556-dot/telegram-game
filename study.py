# luschin_casino_aiogram3_fixed_final.py
# Python 3.8+
# pip install aiogram
# Запуск: python luschin_casino_aiogram3_fixed_final.py

import asyncio
import json
import os
import random
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ---------- Налаштування ----------
# УВАГА: Замість використання справжнього токена, я залишив заглушку.
# Для реальної роботи замініть на свій справжній токен.
# Читаємо токен зі змінної середовища
TOKEN = os.environ.get("BOT_TOKEN") 

if not TOKEN:
    logging.error("❌ Змінна середовища BOT_TOKEN не знайдена. Бот не може запуститися.")
    # Примусове завершення, якщо токена немає
    exit(1) 

# УВАГА: DATA_FILE та CARDS_DIR також повинні бути доступні
DATA_FILE = "users.json"
CARDS_DIR = "cards"
# -----------------------------------

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Глобальні змінні
USERS: Dict[str, Dict[str, Any]] = {}
USER_LEVELS: Dict[str, int] = {}  # Зберігаємо рівні в окремому словнику для простоти

# ---- Пул карток ----
CARD_POOL = [
    {"id": "pasporty", "name": "паспорту", "rarity": "common", "file": "pasporty.jpg"},
    {"id": "zagakovi", "name": "загадковий", "rarity": "medium", "file": "zagakovi.jpg"},
    {"id": "viking", "name": "вікінг", "rarity": "rare", "file": "viking.jpg"},
    {"id": "gadbad", "name": "Утютю", "rarity": "common", "file": "gadbad.jpg"},
    {"id": "holy-moly", "name": "Сігма", "rarity": "medium", "file": "holy-moly.jpg"},
    {"id": "oooyy", "name": "Волтер", "rarity": "rare", "file": "oooyy.jpg"},
    {"id": "ohyrechnik", "name": "ohyrechnik", "rarity": "rare", "file": "ohyrechnik.jpg"},
    {"id": "morjak", "name": "morjak", "rarity": "common", "file": "morjak.jpg"},
    {"id": "lusach", "name": "lusach", "rarity": "rare", "file": "lusach.jpg"},
    {"id": "letsacooke", "name": "letsacooke", "rarity": "medium", "file": "letsacooke.jpg"},
    {"id": "kolaba", "name": "kolaba", "rarity": "common", "file": "kolaba.jpg"},
    {"id": "pikmiband", "name": "pikmiband", "rarity": "rare", "file": "pikmiband.jpg"},
    {"id": "prime", "name": "prime", "rarity": "medium", "file": "prime.jpg"},
    {"id": "sigmafirst", "name": "sigmafirst", "rarity": "common", "file": "sigmafirst.jpg"},
    {"id": "sigmakucherhappy", "name": "sigmakucherhappy", "rarity": "rare", "file": "sigmakucherhappy.jpg"},
    {"id": "sigmalatinys", "name": "sigmalatinys", "rarity": "medium", "file": "sigmalatinys.jpg"},
    {"id": "signakucher", "name": "signakucher", "rarity": "common", "file": "signakucher.jpg"},
    {"id": "SIMAN", "name": "SIMAN", "rarity": "rare", "file": "SIMAN.jpg"},
    {"id": "stylegentelmen", "name": "stylegentelmen", "rarity": "medium", "file": "stylegentelmen.jpg"},
    {"id": "gucul", "name": "gucul", "rarity": "common", "file": "gucul.jpg"},
    {"id": "grizmanylizky", "name": "grizmanylizky", "rarity": "rare", "file": "grizmanylizky.jpg"},
    {"id": "gitarista", "name": "gitarista.", "rarity": "medium", "file": "gitarista.jpg"},
    {"id": "ghost", "name": "ghost.", "rarity": "common", "file": "ghost.jpg"},
    {"id": "floversglovo", "name": "floversglovo.", "rarity": "rare", "file": "floversglovo.jpg"},
    {"id": "color", "name": "color.", "rarity": "medium", "file": "color.jpg"},
    {"id": "brat2", "name": "brat2.", "rarity": "common", "file": "brat2.jpg"},
    {"id": "brat.", "name": "brat..", "rarity": "rare", "file": "brat.jpg"},
    {"id": "bouling", "name": "bouling.", "rarity": "medium", "file": "bouling.jpg"},
    {"id": "beatiful", "name": "beatiful.", "rarity": "common", "file": "beatiful.jpg"},
    {"id": "bandonthebich", "name": "bandonthebich.", "rarity": "rare", "file": "bandonthebich.jpg"},
    {"id": "banda", "name": "banda.", "rarity": "medium", "file": "banda.jpg"},
    {"id": "agrygentelmen", "name": "agrygentelmen.", "rarity": "common", "file": "agrygentelmen.jpg"},
    {"id": "52", "name": "52.", "rarity": "rare", "file": "52.jpg"},
]

# ---- Трофейна ліга ----
PRIZE_TIERS = {
    5: {"type": "weekly_sub", "title": "Тижневий абонемент — 'Ти завжди права'"},
    10: {"type": "pack", "title": "✨ Трійка Щасливчиків ✨(3 картки)"},
    15: {"type": "horror_movie", "title": "Перегляд будь-якого фільму жахів"},
    20: {"type": "pack", "title": "💖 Сюрпризний Букет Карт (3 картки)"},
    25: {"type": "romantic_dinner", "title": "Абонемент на романтичну вечерю (по приїзду)"},
    30: {"type": "pack", "title": "😻 Мур-Пак  (3 картки)"},
    35: {"type": "pack", "title": "🌈 Порція Удачі (3 Картки)"},
    40: {"type": "floating_prize", "title": "Плавучий приз (для отримання призу зверніться до розробників)"},
    55: {"type": "pack", "title": "🎁 Містері-Пак: Тріо Карт!"},
    60: {"type": "pack", "title": "✨ Зібрано з Любов'ю (3 картки)"},
    65: {"type": "pack", "title": "✨ Трійка Щасливчиків ✨"},
    70: {"type": "pack", "title": "💖 Сюрпризний Букет Карт (3 картки)"},
    75: {"type": "pack", "title": "😻 Мур-Пак  (3 картки)"},
    80: {"type": "pack", "title": "🌈 Порція Удачі (3 Картки)"},
    85: {"type": "pack", "title": "🎁 Містері-Пак: Тріо Карт!"},
    90: {"type": "pack", "title": "🍀 Картковий Комплімент (3 картки)"},
    95: {"type": "pack", "title": "✨ Зібрано з Любов'ю (3 картки)"},
    100: {"type": "pack", "title": "✨ Трійка Щасливчиків ✨"},
}


def generate_collection_text(uid: int) -> str:
    """Генерує текстове представлення колекції користувача."""
    user = ensure_user(uid)

    collection_ids = user.get('collection', [])
    txt = f"🗂 Твоя колекція: **{len(collection_ids)}/{len(CARD_POOL)}** карток\n\n"

    if not collection_ids:
        txt += "Поки що порожньо!"
    else:
        # Логіка сортування та відображення карток
        collected_cards = [next(x for x in CARD_POOL if x['id'] == cid) for cid in collection_ids if
                           next((x for x in CARD_POOL if x['id'] == cid), None)]
        collected_cards.sort(key=lambda c: ({"common": 0, "medium": 1, "rare": 2}.get(c['rarity'], 3), c['name']))

        for card in collected_cards:
            rarity_label = card['rarity'].upper()
            txt += f"— **{card['name']}** ({rarity_label})\n"

    return txt

# ---- FSM для покеру ----
class PokerStates(StatesGroup):
    waiting_for_replace = State()


# Глобальний словник для рук у покері (тимчасове зберігання)
USER_HANDS: Dict[int, List[str]] = {}


# ==================================
# БЛОК РОБОТИ З ДАНИМИ
# ==================================

def load_data():
    """Завантажує дані користувачів та рівнів."""
    global USERS, USER_LEVELS
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                USERS = data.get('users', {})
                USER_LEVELS = {str(uid): int(lvl) for uid, lvl in data.get('levels', {}).items()}

            # ******* БЛОК ПЕРЕВІРКИ ТА ВИПРАВЛЕННЯ ДАНИХ *******
            for uid_str, user_data in USERS.items():
                # Гарантуємо, що 'collection' є списком
                if 'collection' in user_data and not isinstance(user_data['collection'], list):
                    user_data['collection'] = []

                    # 🔴 НОВЕ ВИПРАВЛЕННЯ: Додаємо відсутнє поле 'last_card_photo_id'
                if 'last_card_photo_id' not in user_data:
                    user_data['last_card_photo_id'] = None
            # ******* КІНЕЦЬ БЛОКУ *******

            logging.info("✅ Дані користувачів та рівнів успішно завантажено.")
        else:
            USERS = {}
            USER_LEVELS = {}
            logging.warning("⚠️ Файл users.json не знайдено. Створено порожні словники.")
    except Exception as e:
        logging.error(f"Помилка при завантаженні даних: {e}")
        USERS = {}
        USER_LEVELS = {}


def save_data():
    """Зберігає дані користувачів та рівнів."""
    data_to_save = {
        'users': USERS,
        'levels': USER_LEVELS
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Помилка при збереженні даних: {e}")


def ensure_user(uid: int) -> Dict[str, Any]:
    """Перевіряє наявність користувача та ініціалізує, якщо відсутній."""
    uid_str = str(uid)
    if uid_str not in USERS:
        USERS[uid_str] = {
            "last_slot_msg_id": None,
            "poker_history_msg_ids": [],
            'last_cookie_msg_id': None,
            "points": 0,
            "wins": 0,
            "collection": [],
            "prizes": [],
            "awarded_tiers": [],
            "subscriptions": {},
            "last_card_photo_id": None,
        }
        # Ініціалізуємо рівень, якщо його немає
        if uid_str not in USER_LEVELS:
            USER_LEVELS[uid_str] = 1
        save_data()
    return USERS[uid_str]


def get_level(uid: int) -> int:
    """Отримує рівень користувача, за замовчуванням 1."""
    return USER_LEVELS.get(str(uid), 1)


def level_up(uid: int):
    """Підвищує рівень користувача."""
    uid_str = str(uid)
    USER_LEVELS[uid_str] = USER_LEVELS.get(uid_str, 1) + 1
    save_data()


def award_points_and_check(uid: int, points_gain: int = 1, win: bool = False) -> List[Tuple[int, Dict[str, str]]]:
    """Нараховує бали/виграші та перевіряє на нові призи."""
    user = ensure_user(uid)
    user['points'] += points_gain
    if win:
        user['wins'] += 1

    newly_awarded = []
    # Сортування для коректного послідовного нарахування
    for threshold in sorted(PRIZE_TIERS.keys()):
        if user['wins'] >= threshold and threshold not in user['awarded_tiers']:
            prize = PRIZE_TIERS[threshold]
            user['awarded_tiers'].append(threshold)
            user['prizes'].append(prize)
            newly_awarded.append((threshold, prize))

    save_data()
    return newly_awarded


def give_pack_to_user(uid: int, pack_count: int = 1):
    """Видає пак карток користувачеві як приз."""
    user = ensure_user(uid)
    for _ in range(pack_count):
        user['prizes'].append({"type": "pack", "title": "Пак карток (3 картки)"})
    save_data()


def open_pack_for_user(uid: int) -> Optional[List[str]]:
    """Відкриває один пак карток і додає їх до колекції."""
    user = ensure_user(uid)

    # Визначаємо всі можливі ID карток у пулі
    # Цей список автоматично оновлюється при додаванні нових карток до CARD_POOL
    all_card_ids = [card['id'] for card in CARD_POOL]

    idx = None
    for i, p in enumerate(user['prizes']):
        if isinstance(p, dict) and p.get("type") == "pack":
            idx = i
            break
    if idx is None:
        return None

    user['prizes'].pop(idx)

    # 1. КОРЕКТНА ГЕНЕРАЦІЯ: Вибираємо 3 унікальних ID з усього пулу
    new_card_ids = random.sample(all_card_ids, 3)

    # 2. Додавання до колекції
    for card_id in new_card_ids:
        if card_id not in user['collection']:
            user['collection'].append(card_id)

    save_data()

    # Повертаємо ID, які випали (для відображення користувачу)
    return new_card_ids


def card_file_path(card_id: str) -> Optional[str]:
    """Повертає повний шлях до файлу картки."""
    for c in CARD_POOL:
        if c['id'] == card_id:
            return os.path.join(CARDS_DIR, c['file'])
    return None


# ==================================
# БЛОК ПОКЕР-ЛОГІКИ
# ==================================

def get_card_rank(card):
    """Витягує номінал карти, припускаючи, що масть - останній символ."""
    # '10♥️' -> '10', 'A♠️' -> 'A'
    return card[:-1]


def get_rank_value(rank):
    """Конвертує номінал карти (2-A) у числовий ранг (2-14)."""
    if rank.isdigit():
        return int(rank)
    return {'J': 11, 'Q': 12, 'K': 13, 'A': 14}.get(rank.upper(), 0)


def evaluate_hand(hand):
    """Оцінює покерну комбінацію та повертає (ранг_комбінації, бали_виграшу, назва)."""

    if len(hand) != 5:
        # Захист від невірної кількості карт
        return (0, 0, "Некоректна рука (не 5 карт)")

    ranks = []
    suits = []
    for card in hand:
        rank = get_card_rank(card)
        ranks.append(rank)

        # Масть = Усе, що залишається після вилучення номіналу (рангу)
        # Це єдиний надійний спосіб, що працює з багатобайтовими символами
        suit = card[len(rank):]
        suits.append(suit)
    values = sorted([get_rank_value(r) for r in ranks])

    # 1. Частота номіналів
    rank_counts = {}
    for r in ranks:
        rank_counts[r] = rank_counts.get(r, 0) + 1

    counts = sorted(rank_counts.values(), reverse=True)

    # 2. Перевірка Флешу (всі масті однакові)
    is_flush = len(set(suits)) == 1

    # 3. Перевірка Стрейту (5 карт поспіль)
    is_straight = len(set(values)) == 5 and (values[-1] - values[0] == 4)
    # Перевірка для A, 2, 3, 4, 5 (Туз як одиниця)
    if not is_straight and set(values) == {14, 2, 3, 4, 5}:
        is_straight = True

    # -----------------------------------
    # ІЄРАРХІЯ КОМБІНАЦІЙ (від найвищої до найнижчої)
    # -----------------------------------

    # 9. Стрейт-Флеш
    if is_straight and is_flush:
        return (9, 10, "Стрейт-Флеш! 👑")

    # 8. Каре
    if counts[0] == 4:
        return (8, 8, "Каре! 🤯")

    # 7. Фул-Хаус (3 однакових + 2 однакових)
    # Використовуємо len(counts) > 1 для безпеки, хоча counts[1] має бути доступний
    if counts[0] == 3 and len(counts) > 1 and counts[1] == 2:
        return (7, 7, "Фул-Хаус! 🥳")

    # 6. Флеш (5 карт однієї масті)
    if is_flush:
        return (6, 6, "Флеш! 💖")

    # 5. Стрейт (5 карт поспіль)
    if is_straight:
        return (5, 5, "Стрейт! 🎲")

    # 4. Трійка
    if counts[0] == 3:
        return (4, 4, "Трійка!")

    # 3. Дві пари (2 однакових + 2 однакових)
    if counts[0] == 2 and len(counts) > 1 and counts[1] == 2:
        return (3, 3, "Дві пари!")

    # 2. Пара
    if counts[0] == 2:
        return (2, 2, "Пара!")

    # 1. Старша карта
    return (1, 0, "Старша карта.")


# ==================================
# БЛОК ІНТЕРФЕЙСУ ТА ОБРОБНИКІВ
# ==================================

def main_menu() -> InlineKeyboardMarkup:
    """Головне меню з іграми та колекцією."""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎰 Слот із завозом", callback_data="slot"),
                InlineKeyboardButton(text="🃏 Покер із Волтером", callback_data="poker"),
                InlineKeyboardButton(text="🍪 Печеньковий сюрприз", callback_data="cookie")
            ],
            [
                InlineKeyboardButton(text="📦 Відкрити пак", callback_data="open_pack"),
                InlineKeyboardButton(text="🗂 Колекція", callback_data="collection")
            ]
        ]
    )
    return kb


# ---- Команди ----
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    ensure_user(message.from_user.id)
    await message.answer("Вітаю в *Лущін Казино* КОХАННЯ МОЄ 🎰\nОбери гру:", parse_mode="Markdown",
                         reply_markup=main_menu())


# --- Знайдіть та замініть цей блок ---

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command  # Переконайтесь, що це імпортовано!


@dp.callback_query(lambda c: c.data.startswith("view_card_"))
async def cb_view_card(callback: types.CallbackQuery):
    """Обробляє натискання на кнопку картки, видаляє попереднє фото та надсилає нове."""

    # 0. 🔴 ВИПРАВЛЕННЯ: Ініціалізуємо uid та user
    uid = callback.from_user.id
    user = ensure_user(uid)

    # 1. Витягуємо ID картки
    card_id = callback.data.split("_")[-1]

    # 2. Знаходимо повний об'єкт картки
    card = next((x for x in CARD_POOL if x['id'] == card_id), None)

    if not card:
        await callback.answer("Помилка: Картку не знайдено.", show_alert=True)
        return

    # 3. ВИДАЛЕННЯ ПОПЕРЕДНЬОГО ФОТО
    if user['last_card_photo_id']:
        try:
            # Видаляємо старе фото
            await callback.bot.delete_message(chat_id=uid, message_id=user['last_card_photo_id'])
        except Exception:
            pass  # Ігноруємо помилки

    # 4. Знаходимо шлях до файлу
    file_path = os.path.join(CARDS_DIR, card['file'])

    # 5. 🔴 ВИПРАВЛЕННЯ: Логіка обробки файлу та збереження ID
    if os.path.exists(file_path):
        caption = (
            f"🃏 **{card['name']}**\n"
            f"✨ Рідкість: {card['rarity'].upper()}"
        )

        # Надсилання фото
        sent_photo = await callback.bot.send_photo(
            chat_id=uid,  # Використовуємо uid
            photo=FSInputFile(file_path),
            caption=caption,
            parse_mode="Markdown"
        )

        # 🔴 ЗБЕРЕЖЕННЯ ID НОВОГО ФОТО
        user['last_card_photo_id'] = sent_photo.message_id
        save_data()

    else:
        # Якщо файл картки відсутній на диску
        await callback.message.answer(f"Помилка: Файл {file_path} не знайдено. Зверніться до адміністратора.")

    # 6. Закриття callback-запиту
    await callback.answer()


# Цей обробник треба додати до ВСІХ інших обробників, перед async def main()

@dp.callback_query(lambda c: c.data == "main_menu_back")
async def cb_main_menu_back(callback: types.CallbackQuery):
    """Видаляє фото картки та повертає до головного меню, редагуючи повідомлення."""
    uid = callback.from_user.id
    user = ensure_user(uid)

    await callback.answer()

    # 🔴 ВИДАЛЕННЯ ПОПЕРЕДНЬОГО ФОТО
    if user['last_card_photo_id']:
        try:
            await callback.bot.delete_message(chat_id=uid, message_id=user['last_card_photo_id'])
        except Exception:
            pass
        user['last_card_photo_id'] = None # Обнуляємо
        save_data()

    # Редагуємо поточне повідомлення (меню колекції)
    await callback.bot.edit_message_text(
        chat_id=uid,
        message_id=callback.message.message_id,
        text="Вітаю в *Лущін Казино* КОХАННЯ МОЄ 🎰\nОбери гру:",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

@dp.callback_query(lambda c: c.data == "collection")
async def cb_collection(callback: types.CallbackQuery):
    """Обробник кнопки 'Колекція'. Створює інтерактивну клавіатуру, редагуючи повідомлення."""
    uid = callback.from_user.id
    user = ensure_user(uid)
    collection_ids = user.get('collection', [])

    await callback.answer()  # Відповідаємо одразу

    # 1. Початковий текст та лічильник
    total_cards = len(CARD_POOL)
    collected_count = len(collection_ids)

    # 2. Якщо колекція порожня, просто редагуємо текст
    if not collection_ids:
        text = f"🗂 Твоя колекція: **0/{total_cards}** карток. Поки що порожньо!"
        # 🔴 Редагуємо ТІЛЬКИ текст, клавіатура зникне, тому додамо меню
        return await callback.bot.edit_message_text(
            chat_id=uid,
            message_id=callback.message.message_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=main_menu()  # Повертаємо головне меню
        )

    # ... (Логіка збору та сортування collected_cards) ...
    collected_cards = [
        card for card in CARD_POOL if card['id'] in collection_ids
    ]
    rarity_map = {"common": 0, "medium": 1, "rare": 2}
    collected_cards.sort(key=lambda c: (rarity_map.get(c['rarity'], 3), c['name']))

    # 3. Створення кнопок для кожної картки
    keyboard_buttons = []
    for card in collected_cards:
        callback_data = f"view_card_{card['id']}"
        btn = InlineKeyboardButton(
            text=f"🃏 {card['name']} ({card['rarity']})",
            callback_data=callback_data
        )
        keyboard_buttons.append([btn])

    # 🔴 ДОДАЄМО КНОПКУ ПОВЕРНЕННЯ 🔴
    keyboard_buttons.append(
        [InlineKeyboardButton(text="◀️ Назад до ігор", callback_data="main_menu_back")]
    )

    kb = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    new_text = (
        f"🗂 Твоя колекція: **{collected_count}/{total_cards}** карток.\n"
        "Натисни на картку, щоб переглянути її фото:"
    )

    # 4. Редагування повідомлення (ЗМІНЮЄМО ТЕКСТ ТА КЛАВІАТУРУ ОДНОЧАСНО)
    await callback.bot.edit_message_text(
        chat_id=uid,
        message_id=callback.message.message_id,
        text=new_text,
        reply_markup=kb,
        parse_mode="Markdown"
    )


@dp.callback_query(lambda c: c.data == "open_pack")
async def handle_open_pack(callback: types.CallbackQuery):
    """Обробник відкриття пака карток."""
    uid = callback.from_user.id
    await callback.answer()  # Відповідаємо одразу, щоб не було "очікування"

    res = open_pack_for_user(uid)

    if not res:
        await callback.message.answer("У тебе немає пака 😢")
        return

    await callback.message.answer("📦 Ти відкрила пак! Дивись, що всередині:")

    # --- ЛОГІКА ПОЧЕРГОВОГО НАДСИЛАННЯ ---
    for i, cid in enumerate(res):
        card = next((x for x in CARD_POOL if x['id'] == cid), None)

        if card:
            path = card_file_path(cid)
            caption = (
                f"🎉 Картка #{i + 1} з 3\n"
                f"**Назва**: {card['name']}\n"
                f"**Рідкість**: {card['rarity'].upper()}"
            )

            if path and os.path.exists(path):
                try:
                    # Надсилаємо ОДНЕ фото з описом
                    await callback.bot.send_photo(
                        chat_id=uid,
                        photo=FSInputFile(path),
                        caption=caption,
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logging.error(f"Помилка при надсиланні фото: {e}")
                    await callback.message.answer(f"Отримано картку: {card['name']} (помилка файлу).")
            else:
                await callback.message.answer(f"Отримано картку: {card['name']} (файл не знайдено).")

        # Додаємо затримку
        if i < len(res) - 1:
            await asyncio.sleep(1.5)

    await callback.message.answer("\n\n🎉 Всі картки відкрито! 🎉")
    await callback.message.answer("🎮 Обери наступну гру:", reply_markup=main_menu())


@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    """Відображає поточний статус користувача."""
    user = ensure_user(message.from_user.id)
    uid = message.from_user.id

    txt = f"📊 **Статус**\n"
    txt += f"**Бали**: {user['points']}\n"
    txt += f"**Виграші** (для призів): {user['wins']}\n"
    txt += f"**Рівень слота**: {get_level(uid)}\n\n"
    txt += f"**Призи** ({len(user['prizes'])}):\n"

    if not user['prizes']:
        txt += "— Немає\n"
    else:
        for p in user['prizes']:
            if isinstance(p, dict):
                txt += f"— {p.get('title', '(невідомий приз)')}\n"

    await message.answer(txt, parse_mode="Markdown")


@dp.message(Command("give_pack"))
async def cmd_give_pack(message: types.Message):
    """Тестова команда для видачі пака."""
    give_pack_to_user(message.from_user.id)
    await message.answer("Ти отримала 1 тестовий пак 🎁")


# ---- Слот ----
@dp.callback_query(lambda c: c.data == "slot")
async def play_slot(callback: types.CallbackQuery):
    """Гра в слот."""
    uid = callback.from_user.id
    user = ensure_user(uid)
    SLOT_COST = 1

    # Видалення старого повідомлення
    if user.get('last_slot_msg_id'):
        try:
            await callback.bot.delete_message(chat_id=uid, message_id=user['last_slot_msg_id'])
        except Exception:
            pass

    await callback.answer()  # Відповідаємо одразу

    # Перевірка вартості
    if user['points'] < SLOT_COST:
        await callback.message.answer(f"❌ Недостатньо балів! Потрібно {SLOT_COST}, у тебе {user['points']}.")
        return

    # Списання балу
    user['points'] -= SLOT_COST
    save_data()

    # Надсилання "Крутимо барабани..."
    spinning_msg = await callback.message.answer(f"🎰 Крутимо барабани... (-{SLOT_COST} бал)")
    user['last_slot_msg_id'] = spinning_msg.message_id
    save_data()

    await asyncio.sleep(1.5)  # Додаємо невелику затримку

    # Логіка слота
    level = get_level(uid)
    symbols = ["💋", "🍓", "💎", "🔥", "🍀", "⭐", "🍪", "🎲"]
    # Шанс на трійку зменшується з рівнем
    win_chance_percent = max(15 - (level - 1) * 2, 5)  # Наприклад, 15%, мінімум 5%

    # Генерація результату
    result = [random.choice(symbols) for _ in range(3)]

    # Перевірка виграшу
    if len(set(result)) == 1 and random.randint(1, 100) <= win_chance_percent:
        newly = award_points_and_check(uid, points_gain=5, win=True)
        level_up(uid)
        msg = f"Три {result[0]}! 🎉 **+5 балів**! Рівень підвищено до {get_level(uid)}."
    elif len(set(result)) == 2:
        newly = award_points_and_check(uid, points_gain=2, win=False)
        msg = f"Майже виграли! **+2 бали**. Поточний рівень: {get_level(uid)}."
    else:
        newly = award_points_and_check(uid, points_gain=0, win=False)
        msg = f"Нічого не випало 😢 Поточний рівень: {get_level(uid)}."

    # Формування фінального тексту
    final_text = f"Ваш результат: **{' | '.join(result)}**\n\n"
    final_text += msg
    final_text += f"\nПоточні бали: **{ensure_user(uid)['points']}**"

    prize_texts = [f"🎁 Ви отримали приз: {prize['title']}" for threshold, prize in newly]

    if prize_texts:
        final_text += "\n\n**Отримані призи:**\n" + "\n".join(prize_texts)

    # Редагування повідомлення
    await callback.bot.edit_message_text(
        chat_id=uid,
        message_id=spinning_msg.message_id,
        text=final_text,
        parse_mode="Markdown"
    )

    # Додаткове меню
    await callback.message.answer("🎮 Обери наступну гру:", reply_markup=main_menu())


# ---- Покер ----
@dp.callback_query(lambda c: c.data == "poker")
async def cb_poker(callback: types.CallbackQuery, state: FSMContext):
    """Початок гри в покер: роздача карт."""
    uid = callback.from_user.id
    user = ensure_user(uid)

    await callback.answer()  # Відповідаємо одразу

    # Видалення всієї історії попередньої гри
    for msg_id in user.get('poker_history_msg_ids', []):
        try:
            await callback.bot.delete_message(chat_id=uid, message_id=msg_id)
        except Exception:
            pass

    user['poker_history_msg_ids'] = []
    history = []

    # Логіка початку гри (колода та роздача)
    suits = ["♥", "♦", "♣", "♠"]
    values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    deck = [f"{v}{s}" for v in values for s in suits]
    hand = random.sample(deck, 5)  # Вибираємо 5 унікальних карт

    USER_HANDS[uid] = hand.copy()

    m1 = await callback.message.answer("🃏 Волтер роздає карти...")
    history.append(m1.message_id)

    await asyncio.sleep(1)

    numbered_hand = "\n".join([f"**{i + 1}**: {card}" for i, card in enumerate(hand)])
    m2 = await callback.message.answer(f"Ваші карти:\n{numbered_hand}", parse_mode="Markdown")
    history.append(m2.message_id)

    m3 = await callback.message.answer(
        "**Щоб замінити:** Надішліть **номери** карт (від 1 до 5), які хочете замінити, через пробіл. *Наприклад: 1 3 5*\n"
        "**Щоб залишити:** Надішліть слово `ні`.",
        parse_mode="Markdown"
    )
    history.append(m3.message_id)

    user['poker_history_msg_ids'] = history
    save_data()

    await state.set_state(PokerStates.waiting_for_replace)


@dp.message(PokerStates.waiting_for_replace)
async def poker_replace(message: types.Message, state: FSMContext):
    uid = message.from_user.id
    user = ensure_user(uid)
    hand = USER_HANDS.get(uid)
    suits = ["♥", "♦", "♣", "♠"]
    values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    history = user.get('poker_history_msg_ids', [])

    history.append(message.message_id)

    # Захист: якщо руки немає, виходимо
    if not hand:
        await message.answer("⚠️ Помилка! Гра в покер не ініціалізована. Спробуйте /start.")
        await state.clear()
        return

    text = message.text.strip().lower()

    if text != "ні":

        # Створюємо повну колоду та виключаємо карти, що вже є в руці.
        deck = [f"{v}{s}" for v in values for s in suits]
        available_cards = [c for c in deck if c not in hand]

        try:
            indexes = [int(x) - 1 for x in text.split()]

            # Заміна карт
            for i in set(indexes):
                if 0 <= i < 5:
                    if available_cards:
                        # Беремо унікальну карту, що не була в руці
                        new_card = random.choice(available_cards)
                        hand[i] = new_card
                        available_cards.remove(new_card)  # Видаляємо її з пулу

        except Exception:
            m_err = await message.answer("⚠️ Некоректний вибір. Карти залишились ті самі.")
            history.append(m_err.message_id)

    # ... (решта логіки оцінки комбінації) ...

    # Зберігаємо фінальну руку
    USER_HANDS[uid] = hand

    # 1. КОНСОЛІДАЦІЯ ФІНАЛЬНОГО ТЕКСТУ
    numbered_hand = "\n".join([f"**{i + 1}**: {card}" for i, card in enumerate(hand)])
    final_text = f"🃏 **Ваш фінальний набір:**\n{numbered_hand}\n\n"

    # --- ЛОГІКА ОЦІНКИ ---
    rank, points_gain, combo_name = evaluate_hand(hand)
    win_flag = rank >= 3

    newly = award_points_and_check(uid, points_gain=points_gain, win=win_flag)

    if points_gain > 0:
        result_msg = f"🎉 Комбінація: **{combo_name}**! Ви отримуєте **+{points_gain} балів**."
    else:
        result_msg = f"😈 Волтер переміг цього разу. Комбінація: {combo_name}."

    final_text += result_msg
    final_text += f"\nПоточні бали: **{ensure_user(uid)['points']}**"

    # Призи
    prize_texts = [f"🎁 {p['title']}" for t, p in newly]

    if prize_texts:
        final_text += "\n\n**Отримані призи:**\n" + "\n".join(prize_texts)

    # 2. НАДСИЛАННЯ РЕЗУЛЬТАТУ
    result_msg = await message.answer(final_text, parse_mode="Markdown")
    history.append(result_msg.message_id)

    menu_msg = await message.answer("🎮 Обери наступну гру:", reply_markup=main_menu())
    history.append(menu_msg.message_id)

    user['poker_history_msg_ids'] = history
    save_data()

    # Очистка стану FSM
    await state.clear()


# ---- Печеньковий сюрприз ----
@dp.callback_query(lambda c: c.data == "cookie")
async def cookie_surprise(callback: types.CallbackQuery):
    """Гра в печеньковий сюрприз."""
    uid = callback.from_user.id
    user = ensure_user(uid)

    # Видалення старого результату
    if user.get('last_cookie_msg_id'):
        try:
            await callback.bot.delete_message(chat_id=uid, message_id=user['last_cookie_msg_id'])
        except Exception:
            pass

    await callback.answer()  # Відповідаємо одразу

    # Надсилання "В ПРОЦЕСІ"
    cookie_msg = await callback.message.answer("🍪 Працівниця Лущін дістала печеньку...")
    user['last_cookie_msg_id'] = cookie_msg.message_id
    save_data()

    await asyncio.sleep(1.5)

    # Логіка результату
    fortunes = [
        "Тобі скоро завезуть удачу 😘", "Хто сьогодні няшка? Ти 💅",
        "Сігма спостерігає 😎", "Дзвінок від працівниці ❤️📞",
        "Лущін каже: пий водичку й залишайся печенькою 🍪"
    ]

    fortune = random.choice(fortunes)
    points_gain = 2 if random.random() < 0.25 else 0  # 25% шанс отримати 2 бали

    newly = award_points_and_check(uid, points_gain=points_gain, win=points_gain > 0)

    # Консолідація тексту
    final_text = f"✨ **Ваше передбачення:** {fortune}\n\n"

    if points_gain > 0:
        final_text += f"🎉 За вдале передбачення! Ви отримуєте **+{points_gain} балів**."
    else:
        final_text += f"Балів не додано, але пам'ятай: доля у твоїх руках!"

    final_text += f"\nПоточні бали: **{ensure_user(uid)['points']}**"

    prize_texts = [f"🎁 {p['title']}" for t, p in newly]
    if prize_texts:
        final_text += "\n\n**Отримані призи:**\n" + "\n".join(prize_texts)

    # Редагування повідомлення
    await callback.bot.edit_message_text(
        chat_id=uid,
        message_id=cookie_msg.message_id,
        text=final_text,
        parse_mode="Markdown"
    )

    await callback.message.answer("🎮 Обери наступну гру:", reply_markup=main_menu())


# ==================================
# БЛОК ЗАПУСКУ
# ==================================

async def main():
    """Основна функція запуску бота."""
    Path(CARDS_DIR).mkdir(parents=True, exist_ok=True)
    load_data()
    logging.info("Бот запущено!")
    # Використовуємо skip_updates=False для обробки черги під час простою,
    # але можна використати True, якщо ви не хочете обробляти повідомлення, які накопичилися,
    # поки бот був офлайн.
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    try:
        # Використовуємо asyncio.run() для сучасного асинхронного запуску
        asyncio.run(main())
    except KeyboardInterrupt:

        logging.info("Бот зупинено")
