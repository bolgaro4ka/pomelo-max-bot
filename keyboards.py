from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import OpenAppButton

# Keyboard with 1 btn to open mini-app
START_APP_KEYBOARD : InlineKeyboardBuilder = InlineKeyboardBuilder().row(
        OpenAppButton(
            text="Pomelo",
            web_app="pomelo_bot",
            contact_id=77777777
        ),
    )