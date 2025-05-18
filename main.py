import logging
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

API_TOKEN = '8026542920:AAGqYDnySvV3aQKmc4NwrirY3Ywq9YCOdjI'



logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

current_events = "Афиша событий загружается..."

async def fetch_events():
    global current_events
    url = 'https://ticketon.kz/aktobe'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logging.error(f"Ошибка HTTP: статус {resp.status}")
                    current_events = "Не удалось получить афишу (ошибка сервера)."
                    return

                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')

                events = []
                # Найдём все блоки событий — адаптируй селекторы, если потребуется
                for item in soup.select('.event-card, .event-item'):  # пробуем оба варианта
                    date_el = item.select_one('.event-date')
                    title_el = item.select_one('.event-title')
                    if date_el and title_el:
                        date = date_el.text.strip()
                        title = title_el.text.strip()
                        events.append(f"{date}: {title}")

                if events:
                    current_events = "Афиша событий в Актобе:\n" + "\n".join(events)
                else:
                    current_events = "События не найдены."
    except Exception as e:
        logging.exception("Ошибка при парсинге афиши:")
        current_events = "Ошибка при обновлении афиши."

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать! Используйте команду /events для просмотра афиши событий в Актобе.")

@dp.message_handler(commands=['events'])
async def cmd_events(message: types.Message):
    await message.answer(current_events, parse_mode=ParseMode.MARKDOWN)

async def scheduler_start():
    scheduler.add_job(fetch_events, 'interval', hours=24)
    scheduler.start()
    await fetch_events()  # обновляем сразу при старте

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler_start())
    executor.start_polling(dp, skip_updates=True)
