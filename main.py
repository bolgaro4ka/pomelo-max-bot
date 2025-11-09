"""
Main module

This module contains the main entry point of the Pomelo bot.

Contains functions for:

- Initializing the bot and starting the polling process

By Bolgaro4ka / 2025

"""

# Build-in modules
import asyncio
import logging
import os

# External modules
from dotenv import load_dotenv

# Max API
from maxapi import Bot, Dispatcher, F
from maxapi.types import BotStarted, MessageCreated, InputMedia
from maxapi.filters.command import Command
from maxapi.enums.parse_mode import ParseMode

# Internal modules
import messages
from services.pomelo_service import PomeloService
from services.scan_tracker import ScanTracker
from keyboards import open_link_button_keyboard
from utils import get_adi_image_path

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create bot and dispatcher
bot : Bot = Bot(str(os.getenv('API_KEY')))
dp : Dispatcher = Dispatcher()

# Create Pomelo service
pomelo_service = PomeloService()
scan_tracker = ScanTracker(pomelo_service)

@dp.bot_started()
async def bot_started(event: BotStarted) -> None:
    """If user clicks start button"""
    await event.bot.send_message(
        chat_id=event.chat.chat_id, 
        text=messages.HELLO_MSG,
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message_created(Command("start"))
async def start(event: MessageCreated) -> None:
    """Handles /start command"""
    await event.message.answer(
        text=messages.HELLO_MSG,
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message_created(Command("about"))
async def about(event: MessageCreated) -> None:
    """Handles /about command"""
    await event.message.answer(
        text=messages.ABOUT_MSG,
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message_created(Command("help"))
async def help_cmd(event: MessageCreated) -> None:
    """Handles /help command"""
    await event.message.answer(
        text=messages.HELP_MSG,
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message_created(Command("disclaimer"))
async def disclaimer(event: MessageCreated) -> None:
    """Handles /disclaimer command"""
    await event.message.answer(
        text=messages.DISCLAIMER_MSG,
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message_created(Command("scanner"))
async def scanner(event: MessageCreated) -> None:
    """Handles /scanner command"""
    await event.message.answer(
        text=messages.SCANNER_MSG,
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message_created(F.message.body.attachments)
async def createPhotoScan(event: MessageCreated) -> None:
    """Image handler"""
    # Get image from user message (if image > 1, take the first one)
    image = event.message.body.attachments[0].payload.url

    # Send image scan to Pomelo API
    scan_entity = await pomelo_service.createPhotoScan(image)
    scan_id = scan_entity.id

    # Start scan tracking
    await _track_scan(event, scan_id)


@dp.message_created(F.message.body.text)
async def createTextScan(event: MessageCreated) -> None:
    """Text handler"""
    # Get text from user
    text = event.message.body.text

    # Send text scan to Pomelo API
    scan_entity = await pomelo_service.createTextScan(text)
    scan_id = scan_entity.id

    # Start scan tracking
    await _track_scan(event, scan_id)


async def _track_scan(event: MessageCreated, scan_id: str) -> None:
    """Track scan progress and update user with the scan result"""
    user_id = str(event.from_user.user_id)

    # Initial message reference
    bot_message = None
    msg_id = None

    # Callback for status updates
    async def on_status(status: str, scan_entity) -> None:
        """Handle non-terminal status updates"""
        nonlocal bot_message, msg_id

        # Get progress bar for current status
        progress_text = messages.get_progress_bar_msg(status)

        # Send initial message if not sent yet
        if bot_message is None:
            bot_message = await event.bot.send_message(
                chat_id=event.chat.chat_id,
                text=progress_text
            )
            msg_id = bot_message.message.body.mid
        else:
            # Update the existing message with the new progress bar
            await event.bot.edit_message(
                message_id=msg_id,
                text=progress_text
            )

    # Callback for scan completion
    async def on_complete(scan_entity) -> None:
        """Handle scan completion"""
        nonlocal msg_id

        # Ensure we have a message to edit
        if msg_id is None:
            bot_message = await event.bot.send_message(
                chat_id=event.chat.chat_id,
                text="Pomelo сканирует состав!"
            )
            msg_id = bot_message.message.body.mid

        # Update message with loading status
        await event.bot.edit_message(
            message_id=msg_id,
            text=f"Сканирование завершено. Загружаю результат..."
        )

        # Prepare response
        buttons = scan_entity.get_ingredient_buttons()
        attachments = [InputMedia(get_adi_image_path(scan_entity))]

        # Add buttons if links exist
        if buttons:
            attachments.append(open_link_button_keyboard(buttons).as_markup())

        # Edit message with scan results
        await event.bot.edit_message(
            message_id=msg_id,
            text=messages.get_scan_msg(scan_entity)[0],
            parse_mode=ParseMode.MARKDOWN,
            attachments=attachments
        )

        # Send additional message with components
        await event.message.answer(
            text=messages.get_scan_msg(scan_entity)[1],
            parse_mode=ParseMode.MARKDOWN,
        )

    # Callback for errors
    async def on_error(error_msg: str) -> None:
        """Handle scan errors"""
        nonlocal msg_id

        # Ensure we have a message to edit
        if msg_id is None:
            bot_message = await event.bot.send_message(
                chat_id=event.chat.chat_id,
                text=f"Ошибка: {error_msg}"
            )
        else:
            await event.bot.edit_message(
                message_id=msg_id,
                text=f"Ошибка: {error_msg}"
            )

    # Check if user already has active scan
    if not await scan_tracker.track_scan(
        user_id=user_id,
        scan_id=scan_id,
        on_status=on_status,
        on_complete=on_complete,
        on_error=on_error
    ):
        await event.message.answer(text="Сканирование уже идёт. Пожалуйста, подождите.")


async def main() -> None:
    """Start bot polling"""
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())