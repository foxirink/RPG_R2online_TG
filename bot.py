import logging
import random
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from dotenv import load_dotenv

# Загружаем токен из .env файла
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Логирование
logging.basicConfig(level=logging.INFO)

# База данных пользователей и кланов
users = {}
clans = {}
boss_alive = True
last_boss_kill = 0

# Классы персонажей и характеристики
CLASSES = {
    "Рыцарь": {"Сила": 5, "Ловкость": 2, "Интеллект": 1},
    "Рейнджер": {"Сила": 2, "Ловкость": 5, "Интеллект": 2},
    "Ассасин": {"Сила": 5, "Ловкость": 4, "Интеллект": 1},
    "Маг": {"Сила": 1, "Ловкость": 2, "Интеллект": 5},
}

# Монстры и лут
MONSTERS = {
    "Гремлин": {"hp": 30, "loot": ["Зуб гремлина", "Кусок кожи"]},
    "Хобгремлин": {"hp": 50, "loot": ["Коготь хобгремлина", "Малый зелёный камень"]},
    "Чабон (босс)": {"hp": 200, "loot": ["Меч Чабона", "Большой магический камень"]}
}

# Магазин
SHOP = {
    "Зелье здоровья": 10,
    "Меч новичка": 20,
    "Щит охотника": 15
}

# Клавиатуры
start_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Начать игру"))
class_kb = ReplyKeyboardMarkup(resize_keyboard=True)
for c in CLASSES:
    class_kb.add(KeyboardButton(c))

main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(KeyboardButton("Профиль"), KeyboardButton("Лес гремлинов"))
main_kb.add(KeyboardButton("Вступить в клан"), KeyboardButton("Рейтинг кланов"))
main_kb.add(KeyboardButton("Магазин"), KeyboardButton("Скупщик"))

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_id in users:
        await message.answer("Вы уже зарегистрированы!", reply_markup=main_kb)
    else:
        await message.answer("Привет! Выбери свой класс:", reply_markup=class_kb)

@dp.message_handler(lambda message: message.text in CLASSES)
async def choose_class(message: types.Message):
    user_id = message.from_user.id
    users[user_id] = {
        "имя": message.from_user.first_name,
        "класс": message.text,
        "уровень": 1,
        "опыт": 0,
        "хп": 100,
        "статы": CLASSES[message.text].copy(),
        "клан": None,
        "инвентарь": [],
        "золото": 50
    }
    await message.answer(f"Ты выбрал класс {message.text}!", reply_markup=main_kb)

@dp.message_handler(lambda message: message.text == "Магазин")
async def shop(message: types.Message):
    shop_items = "\n".join([f"{item} - {price} золота" for item, price in SHOP.items()])
    await message.answer(f"🛒 **Магазин:**\n{shop_items}\nНапишите название предмета, чтобы купить его.")

@dp.message_handler(lambda message: message.text in SHOP)
async def buy_item(message: types.Message):
    user_id = message.from_user.id
    item = message.text
    price = SHOP[item]
    if users[user_id]["золото"] >= price:
        users[user_id]["золото"] -= price
        users[user_id]["инвентарь"].append(item)
        await message.answer(f"Вы купили {item}! 🏆")
    else:
        await message.answer("Недостаточно золота! ❌")

@dp.message_handler(lambda message: message.text == "Скупщик")
async def sell_items(message: types.Message):
    user_id = message.from_user.id
    inventory = users[user_id]["инвентарь"]
    if not inventory:
        await message.answer("У вас нет предметов для продажи! ❌")
        return
    
    inventory_items = "\n".join([f"{item}" for item in inventory])
    await message.answer(f"🛒 **Ваш инвентарь:**\n{inventory_items}\nНапишите название предмета, чтобы продать его.")

@dp.message_handler()
async def sell_specific_item(message: types.Message):
    user_id = message.from_user.id
    item = message.text
    if item in users[user_id]["инвентарь"]:
        sell_price = random.randint(5, 15)
        users[user_id]["инвентарь"].remove(item)
        users[user_id]["золото"] += sell_price
await message.answer(f"Вы продали {item} за {sell_price} золота! 💰")
    else:
        await message.answer("Такого предмета нет в вашем инвентаре! ❌")

if name == '__main__':
    executor.start_polling(dp, skip_updates=True)
