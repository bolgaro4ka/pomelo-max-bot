"""
Handlers module

This module contains functions used in the Pomelo bot.

Contains functions for:

- Fetching and showing a scan result for a given scan ID
- Listening to SSE updates for a scan with the given scan ID and retrieving the scan result when the scan is fully completed

"""

from services.pomelo_service import PomeloService
from keyboards import open_link_button_keyboard
from messages import get_scan_msg
from utils import get_scan_links, get_adi_image_path
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

    async def on_status_update(status: str):
        """Обработка обновления статуса скана"""
        print(f"Обработка статуса: {status}")

        # If error occurred
        if status in ("failed", "analysis_failed", "recognition_failed"):
            await event.bot.edit_message(message_id=msg_id, text=f"Ошибка скана: {status}")

            # Remove from active scans
            user_id = str(event.from_user.user_id)
            if user_id in active_scans:
                active_scans.remove(user_id)

            # Unsubscribe from updates
            pomelo_service.unsubscribeFromStatusUpdates(scan_id)
            return

        # If status is completed or ai_analysis_completed - refetch scan
        if status in ("completed", "ai_analysis_completed"):
            # Fetch the actual scan result
            scan_entity = await pomelo_service.getScanResult(scan_id)

            # If scan is not fully completed yet, wait for next update
            if not scan_entity.is_fully_completed():
                print("Скан почти завершён, осталось только подождать AI анализ...")
                return

            # Scan is fully completed - update message with results
            await event.bot.edit_message(message_id=msg_id, text=f"Скан {scan_id} завершён. Загружаю результат...")

            # Links in response scan object
            links = get_scan_links(scan_entity)

            # Buttons
            attachments = [InputMedia(get_adi_image_path(scan_entity))]

            # If links exists -> add buttons
            if links:
                attachments.append(open_link_button_keyboard(links).as_markup())

            # Edit previous message
            await event.bot.edit_message(
                message_id=msg_id,
                text=get_scan_msg(scan_entity)[0],
                parse_mode=ParseMode.MARKDOWN,
                attachments=attachments
            )

            # Send message with components
            await event.message.answer(
                text=get_scan_msg(scan_entity)[1],
                parse_mode=ParseMode.MARKDOWN,
            )

            # Remove from active scans
            user_id = str(event.from_user.user_id)
            if user_id in active_scans:
                active_scans.remove(user_id)

            # Unsubscribe from updates
            pomelo_service.unsubscribeFromStatusUpdates(scan_id)

    async def on_error(error: str) -> None:
        """Обработка ошибки подключения SSE"""
        await event.bot.edit_message(message_id=msg_id, text=f"Ошибка подключения: {error}")

        # Remove from active scans
        user_id = str(event.from_user.user_id)
        if user_id in active_scans:
            active_scans.remove(user_id)

        # Unsubscribe from updates
        pomelo_service.unsubscribeFromStatusUpdates(scan_id)

    # Subscribe to scan status updates via PomeloService
    asyncio.create_task(
        pomelo_service.subscribeScanStatusUpdate(scan_id, on_status_update, on_error)
    )