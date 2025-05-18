import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import aiohttp
from bs4 import BeautifulSoup

API_TOKEN = "8026542920:AAGqYDnySvV3aQKmc4NwrirY3Ywq9YCOdjI"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Главное меню
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("Афиша событий"))

current_events = "Афиша пока не загружена. Подождите..."

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

                # Пример - ищем блоки событий (пример надо подстроить под структуру сайта)
                for event_div in soup.select(".event-list-item"):
                    title = event_div.select_one(".event-title")
                    date = event_div.select_one(".event-date")
                    if title and date:
                        events_list.append(f"{date.text.strip()} - {title.text.strip()}")

                if events_list:
                    current_events = "Афиша событий в Актобе:\n\n" + "\n".join(events_list)
                else:
                    current_events = "Афиша пока пуста или структура сайта изменилась."

    except Exception as e:
        logging.exception("Ошибка при обновлении афиши:")
        current_events = "Ошибка при обновлении афиши."

@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    await message.answer(
        "Добро пожаловать в Цифровой Актобе!\n"
        "Нажмите кнопку 'Афиша событий', чтобы увидеть актуальные мероприятия.",
        reply_markup=main_menu
    )

@dp.message_handler(lambda message: message.text == "Афиша событий")
async def send_events(message: types.Message):
    await message.answer(current_events)

async def scheduler():
    while True:
        await fetch_events()
        await asyncio.sleep(60 * 60)  # обновлять каждый час

if name == "main":
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler())
    executor.start_polling(dp, skip_updates=True)
