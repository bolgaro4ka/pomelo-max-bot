"""
About command handler

This module contains handler for /about command.

By Bolgaro4ka / 2025
"""

from maxapi.types import MessageCreated
from maxapi.filters.command import Command
from maxapi.enums.parse_mode import ParseMode

import messages


def register_about_handlers(dp):
    """Register about-related handlers"""

    @dp.message_created(Command("about"))
    async def about(event: MessageCreated) -> None:
        """Handles /about command"""
        await event.message.answer(
            text=messages.ABOUT_MSG,
            parse_mode=ParseMode.MARKDOWN
        )

