from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import LinkButton
from entities.scan_entity import ScanEntity

def open_link_button_keyboard(links: dict[str, str | None]) -> InlineKeyboardBuilder:
    """
    Generate a keyboard with open link buttons based on the provided dictionary of links.

    Args:
        links (dict[str, str | None]): A dictionary where the keys are the button labels and the values are the corresponding URLs (or None for non-clickable buttons).

    Returns:
        InlineKeyboardBuilder: An instance of the InlineKeyboardBuilder class representing the generated keyboard.
    """
    builder = InlineKeyboardBuilder()
    for name, link in links.items():
        # Get url or generate it (but truncate excess from name first and last 7 chars)
        url = link if link else f"https://proe.info/ru/search?text={ScanEntity.text_to_slug(' '.join(name.split(' ')[1:-3]))}"
        builder.row(
            LinkButton(
                text=name,
                url=url
            )
        )

    return builder