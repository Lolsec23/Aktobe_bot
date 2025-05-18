import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import aiohttp
from bs4 import BeautifulSoup

API_TOKEN = "8026542920:AAGqYDnySvV3aQKmc4NwrirY3Ywq9YCOdjI"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Главное меню с кнопкой "Афиша событий"
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("Афиша событий"))

# Хранилища для интересов пользователей
user_interests = {}
user_reminders = {}

# Глобальная переменная для хранения текущих событий (обновляется в фоне)
current_events = "Афиша пока не загружена. Подождите..."

# Асинхронный парсер событий с сайта ticketon.kz
async def fetch_events():
    global current_events
    url = "https://ticketon.kz/aktobe"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    }
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logging.error(f"Ошибка HTTP: статус {resp.status}")
                    current_events = "Не удалось получить афишу (ошибка сервера)."
                    return
                html = await resp.text()
                soup = BeautifulSoup(html, "html.parser")
                events_list = []
                # Обрати внимание, что класс для событий может измениться — проверь структуру сайта
                for event_div in soup.select(".card-event"):  
                    title = event_div.select_one(".card-event__title")
                    date = event_div.select_one(".card-event__date")
                    place = event_div.select_one(".card-event__place")
                    if title and date and place:
                        events_list.append(f"{date.text.strip()} - {title.text.strip()} ({place.text.strip()})")
                if events_list:
                    current_events = "Афиша событий в Актобе:\n\n" + "\n".join(events_list)
                else:
                    current_events = "Афиша пока пуста или структура сайта изменилась."
    except Exception as e:
        logging.exception("Ошибка при обновлении афиши:")
        current_events = "Ошибка при обновлении афиши."

# Пример данных событий для раздела интересов
events_by_interest = {
    "концерт": ["Концерт группы А - 25 мая", "Концерт группы Б - 30 мая"],
    "выставка": ["Выставка картин - 22 мая", "Фотовыставка - 28 мая"],
    "спорт": ["Матч по футболу - 27 мая", "Теннисный турнир - 29 мая"]
}

@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    await message.answer(
        "Добро пожаловать в Цифровой Актобе!\n"
        "Нажмите кнопку 'Афиша событий', чтобы увидеть актуальные мероприятия.\n"
        "Или введите /interests чтобы выбрать интересы.",
        reply_markup=main_menu
    )

@dp.message_handler(lambda message: message.text == "Афиша событий")
async def send_events(message: types.Message):
    await message.answer(current_events)

@dp.message_handler(commands=["interests"])
async def start_interest_selection(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=3)
    buttons = [
        InlineKeyboardButton(text="Концерты", callback_data="interest_концерт"),
        InlineKeyboardButton(text="Выставки", callback_data="interest_выставка"),
        InlineKeyboardButton(text="Спорт", callback_data="interest_спорт"),
    ]
    keyboard.add(*buttons)
    await message.answer("Выберите ваши интересы (можно несколько):", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("interest_"))
async def process_interest(callback_query: types.CallbackQuery):
    interest = callback_query.data[len("interest_"):]
    user_id = callback_query.from_user.id
    if user_id not in user_interests:
        user_interests[user_id] = set()
    if interest in user_interests[user_id]:
        user_interests[user_id].remove(interest)
        await callback_query.answer(f"Удалено: {interest}")
    else:
        user_interests[user_id].add(interest)
        await callback_query.answer(f"Добавлено: {interest}")
    chosen = ", ".join(user_interests[user_id]) if user_interests[user_id] else "ничего не выбрано"
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=f"Выберите ваши интересы (можно несколько):\n\nВыбрано: {chosen}",
        reply_markup=callback_query.message.reply_markup
    )

@dp.message_handler(commands=["myevents"])
async def send_personal_events(message: types.Message):
    user_id = message.from_user.id
    interests = user_interests.get(user_id, set())
    if not interests:
        await message.answer("Вы еще не выбрали интересы. Введите /interests и выберите их.")
        return
    text = "События по вашим интересам:\n\n"
    for interest in interests:
        text += f"--- {interest.upper()} ---\n"
        for event in events_by_interest.get(interest, []):
            text += f"{event}\n"
        text += "\n"
    await message.answer(text)

@dp.message_handler(commands=["remind"])
async def remind(message: types.Message):
    user_id = message.from_user.id
    await message.answer("Напоминание установлено через 10 секунд!")
    await asyncio.sleep(10)
    await bot.send_message(user_id, "Напоминание: событие начинается скоро!")

# Фоновая задача для периодического обновления афиши
async def scheduler():
    while True:
        await fetch_events()
        await asyncio.sleep(60 * 60)  # Обновлять каждый час

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler())
    executor.start_polling(dp, skip_updates=True)
