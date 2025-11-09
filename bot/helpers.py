"""
Helper functions for bot operations
"""


async def send_or_edit_message(bot, chat_id, msg_id_holder: dict, text: str, **kwargs):
    """
    Helper function to send new message or edit existing one.

    Parameters:
        bot: Bot instance to send/edit messages
        chat_id: Chat ID where to send the message
        msg_id_holder: Dictionary with 'msg_id' key to track message ID
        text: Message text
        **kwargs: Additional parameters (parse_mode, attachments, etc.)

    Returns:
        None. Updates msg_id_holder['msg_id'] with the message ID.
    """
    if msg_id_holder.get('msg_id') is None:
        bot_message = await bot.send_message(
            chat_id=chat_id,
            text=text,
            **kwargs
        )
        msg_id_holder['msg_id'] = bot_message.message.body.mid
    else:
        await bot.edit_message(
            message_id=msg_id_holder['msg_id'],
            text=text,
            **kwargs
        )

