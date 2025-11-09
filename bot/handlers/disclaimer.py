from maxapi.types import MessageCreated
from maxapi.filters.command import Command
from maxapi.enums.parse_mode import ParseMode

from bot import messages


def register_disclaimer_handlers(dp):
    """Register disclaimer-related handlers"""

    @dp.message_created(Command("disclaimer"))
    async def disclaimer(event: MessageCreated) -> None:
        """Handles /disclaimer command"""
        await event.message.answer(
            text=messages.DISCLAIMER_MSG,
            parse_mode=ParseMode.MARKDOWN
        )

