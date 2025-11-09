"""
Help command handler

This module contains handler for /help command.

By Bolgaro4ka / 2025
"""

from maxapi.types import MessageCreated
from maxapi.filters.command import Command
from maxapi.enums.parse_mode import ParseMode

import messages


def register_help_handlers(dp):
    """Register help-related handlers"""

    @dp.message_created(Command("help"))
    async def help_cmd(event: MessageCreated) -> None:
        """Handles /help command"""
        await event.message.answer(
            text=messages.HELP_MSG,
            parse_mode=ParseMode.MARKDOWN
        )

