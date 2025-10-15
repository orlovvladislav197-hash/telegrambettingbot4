import os, asyncio, logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from bot.handlers import router
from bot.db import init_db_pool

load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
dp.include_router(router)

async def main():
    pool = await init_db_pool(DATABASE_URL)
    dp['db_pool'] = pool
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
