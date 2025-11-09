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
import json

# External modules
from dotenv import load_dotenv

# Max API
from maxapi import Bot, Dispatcher, F
from maxapi.types import BotStarted, MessageCreated
from maxapi.filters.command import Command
from maxapi.enums.parse_mode import ParseMode

# Internal modules
import messages
import pomelo
import handlers

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create bot and dispatcher
bot : Bot = Bot(str(os.getenv('API_KEY')))
dp : Dispatcher = Dispatcher()

active_scans = []  # user_id -> scan in progress

@dp.bot_started()
async def bot_started(event: BotStarted) -> None:
    """
    If user clicks start button
    """
    await event.bot.send_message(
        chat_id=event.chat.chat_id, 
        text=messages.HELLO_MSG,
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message_created(Command("start"))
async def start(event: MessageCreated) -> None:
    """
    Handles /start command
    """
    await event.message.answer(
        text=messages.HELLO_MSG,
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message_created(Command("about"))
async def menu(event: MessageCreated) -> None:
    """
    Handles /about command
    """
    await event.message.answer(
        text=messages.ABOUT_MSG,
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message_created(Command("help"))
async def menu(event: MessageCreated) -> None:
    """
    Handles /help command
    """
    await event.message.answer(
        text=messages.HELP_MSG,
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message_created(Command("disclaimer"))
async def menu(event: MessageCreated) -> None:
    """
    Handles /disclaimer command
    """
    await event.message.answer(
        text=messages.DISCLAIMER_MSG,
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message_created(Command("scanner"))
async def menu(event: MessageCreated) -> None:
    """
    Handles /scanner command
    """
    await event.message.answer(
        text=messages.SCANNER_MSG,
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message_created(F.message.body.attachments)
async def image(event: MessageCreated) -> None:
    """
    Image handler
    """
    # Get image from user message (if image > 1, take the first one)
    image = event.message.body.attachments[0].payload.url

    # Send image scan to Pomelo API
    res = await pomelo.send_scan(image)
    scan_id = res["scan"]["id"]

    # Fetch and show scan
    await handlers.fetch_and_show_scan(event, scan_id, active_scans)


@dp.message_created(F.message.body.text)
async def echo(event: MessageCreated) -> None:
    """
    Text handler
    """
    # Get text from user
    text = event.message.body.text

    # Send text scan to Pomelo API
    res = await pomelo.send_text(text)
    scan_id = res["scan"]["id"]

    # Fetch and show scan
    await handlers.fetch_and_show_scan(event, scan_id, active_scans)


async def main() -> None:
    """
    Asynchronously starts polling the bot for updates.

    This function initializes the dispatcher `dp` and starts polling the bot for updates using the `start_polling` method. This allows the bot to receive and handle incoming messages and events.

    Parameters:
        None

    Returns:
        None
    """
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())