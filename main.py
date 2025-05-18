from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import logging
import os

API_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(
    KeyboardButton("Афиша"),
    KeyboardButton("Справка"),
    KeyboardButton("Бизнес-каталог"),
    KeyboardButton("Полезное")
)

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.answer(
        "Добро пожаловать в Цифровой Актобе!",
        reply_markup=main_menu
    )

@dp.message_handler(lambda message: message.text == "Афиша")
async def afisha(message: types.Message):
    text = "Афиша событий в Актобе:
- Концерт в Tleu 20 мая
- Выставка в музей 22 мая"
    await message.answer(text)

@dp.message_handler(lambda message: message.text == "Справка")
async def spravka(message: types.Message):
    text = "Справка:
- ЦОН №1: ул. 101 стрелковой бригады 87
- Аптека 24ч: пр. Абулхаир хана, 45"
    await message.answer(text)

@dp.message_handler(lambda message: message.text == "Бизнес-каталог")
async def catalog(message: types.Message):
    text = "Бизнес-каталог:
- Кофейня 'Ла Крема'
- Автомойка 'ЧистоDrive'
- Магазин 'Электроника+’"
    await message.answer(text)

@dp.message_handler(lambda message: message.text == "Полезное")
async def useful(message: types.Message):
    text = "Полезное:
- Погода: +22°C, ясно
- Курс доллара: 450₸
- Телефон экстренных служб: 112"
    await message.answer(text)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    executor.start_polling(dp, skip_updates=True)
