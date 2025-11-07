# By Bolgaro4ka / 2025
import asyncio
import logging

from maxapi import Bot, Dispatcher, F
from maxapi.types import BotStarted, MessageCreated
from maxapi.filters.command import Command

import os

from dotenv import load_dotenv
load_dotenv()

from keyboards import START_APP_KEYBOARD

logging.basicConfig(level=logging.INFO)

bot : Bot = Bot(str(os.getenv('API_KEY')))
dp : Dispatcher = Dispatcher()


@dp.bot_started()
async def bot_started(event: BotStarted):
    """
    При нажатии на кнопку старт
    """
    await event.bot.send_message(
        chat_id=event.chat_id,
        text='Привет! Отправь мне /start'
    )

@dp.message_created(Command("start"))
async def start(event: MessageCreated):
    """
    Обработчик команды /start
    """
    await event.message.answer(
        text="Привет, я бот Pomelo.",
    )

@dp.message_created(F.message.body.text)
async def echo(event: MessageCreated):
    """
    Обработчик текстовых сообщений
    """
    await event.message.answer("я ничего не умею, я бесполезный!\nНо ты написал: " + event.message.body.text)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())