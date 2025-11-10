from maxapi import F
from maxapi.types import MessageCreated, InputMediaBuffer
from maxapi.filters.command import Command
from maxapi.enums.parse_mode import ParseMode

from bot import messages
from bot.keyboards import open_link_button_keyboard
from bot.helpers import send_or_edit_message
from services.pomelo_service import PomeloService
from services.scan_tracker import ScanTracker


# Create Pomelo service
pomelo_service = PomeloService()
scan_tracker = ScanTracker(pomelo_service)


def register_scanner_handlers(dp):
    """Register scanner-related handlers"""

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

    # Message ID holder
    msg_id_holder = {'msg_id': None}

    # Callback for status updates
    async def on_status(status: str, scan_entity) -> None:
        """Handle non-terminal status updates"""
        progress_text = messages.get_progress_bar_msg(status)
        await send_or_edit_message(
            event.bot,
            event.chat.chat_id,
            msg_id_holder,
            progress_text
        )

    # Callback for scan completion
    async def on_complete(scan_entity) -> None:
        """Handle scan completion"""
        # Update message with loading status
        await send_or_edit_message(
            event.bot,
            event.chat.chat_id,
            msg_id_holder,
            "Сканирование завершено. Загружаю результат..."
        )

        # Prepare response
        buttons = scan_entity.get_ingredient_buttons()
        attachments = [InputMediaBuffer(scan_entity.get_adi_image_buffer(scan_entity))]

        # Add buttons if links exist
        if buttons:
            attachments.append(open_link_button_keyboard(buttons).as_markup())

        # Edit message with scan results
        await send_or_edit_message(
            event.bot,
            event.chat.chat_id,
            msg_id_holder,
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
        await send_or_edit_message(
            event.bot,
            event.chat.chat_id,
            msg_id_holder,
            f"Ошибка: {error_msg}"
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

