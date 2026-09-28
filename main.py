from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from loguru import logger
import sqlite3
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from train import Train 
import os
from dotenv import load_dotenv
load_dotenv()

# 1. Настройка окружения
bot = Bot(token=os.environ["BOT_TOKEN"])
dp = Dispatcher()

# 5. Логирование
logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB")

# 4. FSM (Finite State Machine) для поиска билетов
class TrainSearch(StatesGroup):
    waiting_for_departure = State()
    waiting_for_arrival = State()
    waiting_for_date = State()

# 7. Обработка ошибок
@dp.errors()
async def errors_handler(update, exception):
    logger.error(f"Ошибка: {exception} при обработке {update}")
    return True

# 3. Команды бота
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать в систему расписания поездов!\n"
        "Доступные команды:\n"
        "/search - Поиск поездов\n"
        "/help - Помощь"
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Помощь по боту:\n/search - начать поиск поездов")

# 6. Интеграция с базой данных

def find_trains(departure, arrival):
    try:
        conn = sqlite3.connect("trains.db")
        cursor = conn.cursor()

        route_pattern = f"{departure} -> {arrival}"
        logger.debug(f"Executing SQL Query: SELECT number, route, departure_time, arrival_time FROM trains WHERE route LIKE '{route_pattern}'")

        cursor.execute("SELECT number, route, departure_time, arrival_time FROM trains WHERE route = ?", (route_pattern,))
        trains = cursor.fetchall()
        
        conn.close()

        logger.debug(f"Trains Found: {len(trains)}")
        for train in trains:
            logger.debug(f"Train: {train[0]}, Route: {train[1]}")

        return trains
    except Exception as e:
        logger.error(f"Ошибка в find_trains(): {e}")
        return []



# 3. Обработка поиска
@dp.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext):
    await message.answer("Введите станцию отправления:")
    await state.set_state(TrainSearch.waiting_for_departure)

@dp.message(TrainSearch.waiting_for_departure)
async def process_departure(message: Message, state: FSMContext):
    await state.update_data(departure=message.text)
    logger.debug(f"Пользователь ввел станцию отправления: {message.text}")
    await message.answer("Введите станцию назначения:")
    await state.set_state(TrainSearch.waiting_for_arrival)

@dp.message(TrainSearch.waiting_for_arrival)
async def process_arrival(message: Message, state: FSMContext):
    await state.update_data(arrival=message.text)
    user_data = await state.get_data()
    
    logger.debug(f"Поиск поездов: {user_data['departure']} -> {message.text}")
    
    # Добавляем лог перед вызовом функции
    logger.debug("Вызов find_trains()...")
    trains = find_trains(user_data['departure'], message.text)
    logger.debug("find_trains() завершил выполнение")
    
    if trains:
        response = "\n\n".join([
            f"Поезд №{train.train_number}\n"
            f"Маршрут: {train.route}\n"
            f"Время отправления: {train.departure_time}\n"
            f"Время прибытия: {train.arrival_time}"
            for train in trains
        ])
    else:
        response = "Поездов не найдено"
    
    logger.debug(f"Отправляем ответ: {response}")  # Проверяем, что ответ сгенерирован
    await message.answer(response)
    await state.clear()

# 2. Ответ на текстовые сообщения
@dp.message()
async def text_messages(message: Message):
    await message.answer("Используйте команды для работы с ботом (/help)")

if __name__ == "__main__":
    logger.info("Бот запущен")
    dp.run_polling(bot)