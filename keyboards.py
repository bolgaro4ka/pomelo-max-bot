from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import OpenAppButton, LinkButton

# Keyboard with 1 btn to open mini-app
def open_link_button_keyboard(links: dict[str, str]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for name, link in links.items():
        builder.row(
            LinkButton(
                text=name,
                url=link
            )
        )
        
    return builder