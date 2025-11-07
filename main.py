# By Bolgaro4ka / 2025
import asyncio
import logging

from maxapi import Bot, Dispatcher, F
from maxapi.types import BotStarted, MessageCreated
from maxapi.types import InputMedia
from maxapi.filters.command import Command

import os

from dotenv import load_dotenv
load_dotenv()

from keyboards import open_link_button_keyboard
from messages import HELLO_MSG

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
        text=HELLO_MSG
    )

@dp.message_created(Command("start"))
async def start(event: MessageCreated):
    """
    Обработчик команды /start
    """
    await event.message.answer(
        text=HELLO_MSG,
    )

@dp.message_created(Command("link"))
async def link(event: MessageCreated):
    """
    Обработчик команды /link 
    """
    await event.message.answer(
        text="Привет, я бот Pomelo.",
        attachments=[
            open_link_button_keyboard({'sigma': 'https://blgr.space'}).as_markup(),
            InputMedia('./media/hamster.gif')
        ]
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