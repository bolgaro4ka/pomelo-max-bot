# By Bolgaro4ka / 2025
import asyncio
import logging

from maxapi import Bot, Dispatcher, F
from maxapi.types import MessageCreated
from maxapi.filters.command import Command

from keyboards import START_APP_KEYBOARD

logging.basicConfig(level=logging.INFO)

bot : Bot = Bot('f9LHodD0cOKy1loHcHd-t8b_QUvhAVqbwS1M58II6OeOktmwQslmFyyZIUW_J0R_MhzJbRTL_9fJkG1gOUQj')
dp : Dispatcher = Dispatcher()

@dp.message_created(Command("start"))
async def start(event: MessageCreated):
    """
    Обработчик команды /start
    """
    await event.message.answer(
        text="Привет, я бот Pomelo.\nЖми кнопку начать, чтобы запустить приложение!",
    )

@dp.message_created(F.message.body.text)
async def echo(event: MessageCreated):
    """
    Обработчик текстовых сообщений
    """
    await event.message.answer("Я пока не умею разговаривать, но умею запускать мини-приложение!")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())