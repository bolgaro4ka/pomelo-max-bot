import os
import matplotlib.pyplot as plt
from entities.scan_entity import ScanEntity


def get_adi_image_path(scan_entity: ScanEntity, folder: str = "adi_cache") -> str:
    """
    Get the path to an image file representing the additives danger index (ADI) based on the given scan entity.

    Parameters:
        scan_entity (ScanEntity): The scan entity containing the analysis information.
        folder (str, optional): The folder where the image file will be saved. Defaults to "adi_cache".

    Returns:
        str: The path to the generated image file.

    This function calculates the ADI value from the scan entity and generates an image representing the ADI as a pie chart. The ADI value is used to determine the color of the chart. The image file is saved in the specified folder or the default "adi_cache" folder if not provided. If the file already exists, the path to the existing file is returned.

    The image file is generated using matplotlib library. The pie chart represents the ADI value as a percentage, with the color determined by the ADI value. The ADI value is displayed in the center of the chart, and the label "ВРЕДНОСТЬ" (HARMFULNESS) is displayed below the chart.

    The function returns the path to the generated image file.
    """

    # Get adi
    adi = scan_entity._data.get("analysis", {}).get("additivesDangerIndex", 0)
    adi = max(0, min(100, adi))

    # Create folder
    os.makedirs(folder, exist_ok=True)

    # Path to file
    file_path = os.path.join(folder, f"adi_{adi}.png")

    # If file exists -> return file path
    if os.path.exists(file_path):
        return file_path

    # Color
    if adi < 40:
        color = "#2ecc71"
    elif adi < 70:
        color = "#f1c40f"
    else:
        color = "#e74c3c"

    # Generate image
    fig, ax = plt.subplots(figsize=(3, 3), dpi=150)

    # Progress bar
    ax.pie(
        [adi, 100 - adi],
        colors=[color, "#e0e0e0"],
        startangle=90,
        wedgeprops={"width": 0.25, "edgecolor": "white"}
    )

    # Number in center
    ax.text(0, 0, str(adi), ha="center", va="center", fontsize=28, weight="bold")

    # Label
    ax.text(0, -1.25, "ВРЕДНОСТЬ", ha="center", fontsize=14, weight="bold")

    ax.axis("equal")
    plt.tight_layout()

    # Save file
    fig.savefig(file_path, format="png", bbox_inches="tight")
    plt.close(fig)

    # Return file path
    return file_path


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
