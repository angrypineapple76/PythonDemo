import asyncio
import logging
from aiogram import Bot, Dispatcher
from handlers import register_handlers
from database import create_tables

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен бота
API_TOKEN = '7657077295:AAEF83UsQ7BFqBNO25ty4kQgEp0gmtZDQMk'

async def main():
    # Создаем объекты бота и диспетчера
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    # Регистрируем обработчики
    register_handlers(dp)

    # Создаем таблицы в БД
    await create_tables()

    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())