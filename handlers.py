"""
Handlers module

This module contains functions used in the Pomelo bot.

Contains functions for:

- Fetching and showing a scan result for a given scan ID
- Listening to SSE updates for a scan with the given scan ID and retrieving the scan result when the scan is fully completed

By Bolgaro4ka / 2025
"""

from pomelo_service import PomeloService
import sse_listener
from keyboards import open_link_button_keyboard
from messages import get_scan_msg
from functions import get_scan_links, get_adi_image_path
from maxapi.types import InputMedia, MessageCreated
import asyncio
from maxapi.enums.parse_mode import ParseMode


async def fetch_and_show_scan(event: MessageCreated, scan_id: str, active_scans: list[str], pomelo_service: PomeloService) -> None:
    """Получение и отображение результата скана"""

    # Check if scan is already in progress
    if str(event.from_user.user_id) in active_scans:
        await event.message.answer(
            text="Скан уже идёт. Пожалуйста, подождите."
        )
        return
    
    # Add user to active scans
    active_scans.append(str(event.from_user.user_id))

    # Start scan
    bot_message = await event.bot.send_message(chat_id=event.chat.chat_id, text="Скан запущен! Ожидаем...")

    # Save message id
    msg_id = bot_message.message.body.mid

    async def get_scan_result(scan_id):
        """Получение результата скана и обновление сообщения"""
        # If scan is completed and aiAnalysis is not null -> edit previous message
        await event.bot.edit_message(message_id=msg_id, text = f"Скан {scan_id} завершён. Загружаю результат...")
        res = await pomelo_service.getScanResult(scan_id)
        SCAN_RESPONSE = res["scan"]

        # If scan is not fully completed
        if not sse_listener.is_scan_fully_completed(SCAN_RESPONSE):
            print("Скан почти завершён, осталось только подождать AI анализ...")
            return  # Wait for next sse event

        # Links in response scan object
        links=get_scan_links(SCAN_RESPONSE)

        # Buttons
        attachments = [InputMedia(get_adi_image_path(SCAN_RESPONSE))]

        # If links exists -> add buttons
        if links:
            attachments.append(open_link_button_keyboard(links).as_markup())

        # Edit previous message
        await event.bot.edit_message(
            message_id=msg_id,
            text=get_scan_msg(SCAN_RESPONSE)[0],
            parse_mode=ParseMode.MARKDOWN,
            attachments=attachments
        )

        # Send message with components
        await event.message.answer(
            text=get_scan_msg(SCAN_RESPONSE)[1],
            parse_mode=ParseMode.MARKDOWN,
        )

        # Remove from active scans
        user_id = str(event.from_user.user_id)
        if user_id in active_scans:
            active_scans.remove(user_id)

    async def on_error(error) -> None:
        """Обработка ошибки скана"""
        await event.bot.edit_message(message_id=msg_id, text = f"Ошибка скана: {error}")

        # Remove from active scans
        user_id = str(event.from_user.user_id)
        if user_id in active_scans:
            active_scans.remove(user_id)

    # Start SSE in background
    asyncio.create_task(
        sse_listener.listen_scan_updates(scan_id, get_scan_result, on_error)
    )