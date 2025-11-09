"""
Functions module

This module contains functions used in the Pomelo bot.

Contains functions for:

- Generating an image representing the additives danger index (ADI) based on the given scan response
- Generating a dictionary of links based on the analysis ingredients of a given dictionary.

By Bolgaro4ka / 2025

"""

import os
import matplotlib.pyplot as plt


def get_adi_image_path(scan_response: dict, folder: str = "adi_cache") -> str:
    """
    Get the path to an image file representing the additives danger index (ADI) based on the given scan response.

    Parameters:
        scan_response (dict): The scan response containing the analysis information.
        folder (str, optional): The folder where the image file will be saved. Defaults to "adi_cache".

    Returns:
        str: The path to the generated image file.

    This function calculates the ADI value from the scan response and generates an image representing the ADI as a pie chart. The ADI value is used to determine the color of the chart. The image file is saved in the specified folder or the default "adi_cache" folder if not provided. If the file already exists, the path to the existing file is returned.

    The image file is generated using matplotlib library. The pie chart represents the ADI value as a percentage, with the color determined by the ADI value. The ADI value is displayed in the center of the chart, and the label "ВРЕДНОСТЬ" (HARMFULNESS) is displayed below the chart.

    The function returns the path to the generated image file.
    """

    # Get adi
    adi = scan_response.get("analysis", {}).get("additivesDangerIndex", 0)
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


# Danger level to emoji for keyboard
DANGER_LEVEL = {
    -1: "⚪",
    0: "⚪",
    1: "🟢",
    2: "🟡",
    3: "🟡",
    4: "🟠",
    5: "🔴"
}

def get_scan_links(res : dict) -> dict[str, str]:
    """
    Generate a dictionary of links based on the analysis ingredients of a given dictionary.

    Args:
        res (dict): The dictionary containing the analysis ingredients.

    Returns:
        dict[str, str]: A dictionary where the keys are formatted strings representing the danger level, ingredient name, and danger level index, and the values are the corresponding reference URLs.
    """
    d = {}
    for item in res["analysis"]["ingredients"]:
        if not item["referenceUrl"]:
            continue
        # For example: {"⚪️ кальций-найтрий-3гидрокси... 0 из 5": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
        d[f"{DANGER_LEVEL[item['danger']]} {item['name'] if len(item["name"]) < 20 else (item['name'][:20] + '...')} {item['danger']} из 5"] = item["referenceUrl"]

    return d