from maxapi.types import BotStarted, MessageCreated, InputMediaBuffer
from maxapi.filters.command import Command
from maxapi.enums.parse_mode import ParseMode

from bot import messages


def register_start_handlers(dp):
    """Register start-related handlers"""

    @dp.bot_started()
    async def bot_started(event: BotStarted) -> None:
        """If user clicks start button"""
        with open("assets/greeting.png", "rb") as image_file:
            await event.bot.send_message(
                chat_id=event.chat.chat_id,
                text=messages.HELLO_MSG,
                parse_mode=ParseMode.MARKDOWN,
                attachments=[InputMediaBuffer(image_file.read())]
            )

    @dp.message_created(Command("start"))
    async def start(event: MessageCreated) -> None:
        """Handles /start command"""
        with open("assets/greeting.png", "rb") as image_file:
            await event.message.answer(
                text=messages.HELLO_MSG,
                parse_mode=ParseMode.MARKDOWN,
                attachments=[InputMediaBuffer(image_file.read())]
            )
