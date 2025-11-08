# By Bolgaro4ka / 2025
import asyncio
import logging

from maxapi import Bot, Dispatcher, F
from maxapi.types import BotStarted, MessageCreated
from maxapi.types import InputMedia
from maxapi.filters.command import Command
from maxapi.enums.parse_mode import ParseMode

import os

from dotenv import load_dotenv
load_dotenv()

from keyboards import open_link_button_keyboard
from messages import HELLO_MSG, get_scan_msg
from functions import get_scan_links, get_adi_image_path
import pomelo
import sse_listener

import asyncio
import json


logging.basicConfig(level=logging.INFO)

bot : Bot = Bot(str(os.getenv('API_KEY')))
dp : Dispatcher = Dispatcher()


@dp.bot_started()
async def bot_started(event: BotStarted):
    """
    При нажатии на кнопку старт
    """
    await event.message.answer(
        text=HELLO_MSG,
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message_created(Command("start"))
async def start(event: MessageCreated):
    """
    Обработчик команды /start
    """
    await event.message.answer(
        text=HELLO_MSG,
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message_created(F.message.body.attachments)
async def image(event: MessageCreated):
    """
    Обработчик изображений
    """
    image = event.message.body.attachments[0].payload.url

    scan_id=json.loads(pomelo.send_scan(image).content)["scan"]["id"]
    bot_message = await event.bot.send_message(chat_id=event.chat.chat_id, text="Скан запущен! Ожидаем...")
    msg_id = bot_message.message.body.mid
    
    async def get_scan_result(scan_id):
        await event.bot.edit_message(message_id=msg_id, text = f"Скан {scan_id} завершён. Загружаю результат...")
        SCAN_RESPONSE=json.loads(pomelo.get_scan(scan_id).content)["scan"]
        links=get_scan_links(SCAN_RESPONSE)

        attachments = [InputMedia(get_adi_image_path(SCAN_RESPONSE))]
        if links:
            attachments.append(open_link_button_keyboard(links).as_markup())

        await event.bot.edit_message(
            message_id=msg_id,
            text=get_scan_msg(SCAN_RESPONSE)[0],
            parse_mode=ParseMode.MARKDOWN,
            attachments=attachments
        )

        await event.message.answer(
            text=get_scan_msg(SCAN_RESPONSE)[1],
            parse_mode=ParseMode.MARKDOWN,
        )

    async def on_error(error):
        await event.bot.edit_message(message_id=msg_id, text = f"Ошибка скана: {error}")

    # Запускаем SSE в фоне
    asyncio.create_task(
        sse_listener.listen_scan_updates(scan_id, get_scan_result, on_error)
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