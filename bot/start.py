"""
Start command handlers

This module contains handlers for bot start events and /start command.

By Bolgaro4ka / 2025
"""

from maxapi.types import BotStarted, MessageCreated
from maxapi.filters.command import Command
from maxapi.enums.parse_mode import ParseMode

import messages


def register_start_handlers(dp):
    """Register start-related handlers"""

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

