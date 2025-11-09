from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import LinkButton


def open_link_button_keyboard(links: dict[str, str]) -> InlineKeyboardBuilder:
    """
    Generate a keyboard with open link buttons based on the provided dictionary of links.

    Args:
        links (dict[str, str]): A dictionary where the keys are the button labels and the values are the corresponding URLs.

    Returns:
        InlineKeyboardBuilder: An instance of the InlineKeyboardBuilder class representing the generated keyboard.
    """
    builder = InlineKeyboardBuilder()
    for name, link in links.items():
        builder.row(
            LinkButton(
                text=name,
                url=link
            )
        )
        
    return builder