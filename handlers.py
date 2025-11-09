"""
Handlers module

This module contains functions used in the Pomelo bot.

Contains functions for:

- Fetching and showing a scan result for a given scan ID
- Listening to SSE updates for a scan with the given scan ID and retrieving the scan result when the scan is fully completed

By Bolgaro4ka / 2025
"""

import json
import pomelo
import sse_listener
from keyboards import open_link_button_keyboard
from messages import get_scan_msg
from functions import get_scan_links, get_adi_image_path
from maxapi.types import InputMedia, MessageCreated
import asyncio
from maxapi.enums.parse_mode import ParseMode


async def fetch_and_show_scan(event : MessageCreated, scan_id: str, active_scans : list[str]) -> None:
    """
    Asynchronously fetches and shows a scan result for a given scan ID.

    Parameters:
        event (MessageCreated): The event object representing the message creation.
        scan_id (str): The ID of the scan.

    Returns:
        None

    This function starts a scan by sending a message with the text "Скан запущен! Ожидаем..." to the chat.
    It then saves the message ID and defines two nested functions: `get_scan_result` and `on_error`.
    `get_scan_result` retrieves the scan result for the given scan ID and updates the message with the result.
    It checks if the scan is fully completed and if not, it waits for the next SSE event.
    If the scan is completed, it retrieves the links and attachments from the scan response,
    and edits the previous message with the new text, parse mode, and attachments.
    It also sends a message with components.
    `on_error` handles the error that occurred during the scan by editing the previous message with the error text.

    This function also creates a task to listen for SSE updates in the background using the `sse_listener.listen_scan_updates` function.

    Note: The `get_scan_result` and `on_error` functions are defined within this function and are not accessible outside of it.
    """

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
        """
        Asynchronously retrieves the scan result for a given scan ID and updates the message with the result.

        Parameters:
            scan_id (str): The ID of the scan.

        Returns:
            None
        """
        # If scan is completed and aiAnalysis is not null -> edit previous message
        await event.bot.edit_message(message_id=msg_id, text = f"Скан {scan_id} завершён. Загружаю результат...")
        res = await pomelo.get_scan(scan_id)
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
        active_scans.remove(str(event.from_user.user_id))

    async def on_error(error) -> None:
        """
        Handle the error that occurred during the scan.

        Parameters:
            error (Any): The error that occurred.

        Returns:
            None
        """
        await event.bot.edit_message(message_id=msg_id, text = f"Ошибка скана: {error}")

        # Remove from active scans
        active_scans.remove(str(event.from_user.user_id))

    # Start SSE in background
    asyncio.create_task(
        sse_listener.listen_scan_updates(scan_id, get_scan_result, on_error)
    )