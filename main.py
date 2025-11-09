import asyncio
import logging
import os

from dotenv import load_dotenv
from maxapi import Bot, Dispatcher

from bot import register_all_handlers

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)


def create_bot() -> Bot:
    """Create and configure bot instance"""
    return Bot(str(os.getenv('API_KEY')))


def create_dispatcher() -> Dispatcher:
    """Create and configure dispatcher instance"""
    dp = Dispatcher()
    register_all_handlers(dp)
    return dp


async def main() -> None:
    """Start bot polling"""
    bot = create_bot()
    dp = create_dispatcher()

    logging.info("Bot is starting...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())