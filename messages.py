"""
This module contains functions used in the Pomelo bot for generating messages.

Consains consts:

- HELLO_MSG - A string representing the initial message sent to the user when the bot is started.

Contains functions for:

- Generating a list of two strings representing the scan response information.

By Bolgaro4ka / 2025

"""



HELLO_MSG = """**Привет 👋 Я — бот Pomelo 🍋**

Помогаю разобрать состав продуктов: 
- нахожу опасные Е-добавки
- оцениваю вредность
- Дают рекомендации по питанию 
- Предупреждаю о наличии аллергенов

📸 Отправь текст или фото состава, чтобы получить детальный анализ"""

def get_scan_msg(scan_response: dict) -> list[str]:
    """
    Generate a list of two strings representing the scan response information.

    Args:
        scan_response (dict): The scan response containing the analysis information.

    Returns:
        list[str]: A list of two strings. The first string contains the name, allergens, AI analysis, and additives information. The second string contains the composition and a disclaimer.

    This function takes a scan response dictionary as input and generates two strings representing the scan response information. The first string includes the name, allergens, AI analysis, and additives information. The second string includes the composition and a disclaimer. The function iterates over the ingredients in the scan response and checks if any of them have a reference URL. If a reference URL is found, the flag variable is set to True. The function then constructs the two strings using the information from the scan response dictionary.
    """

    # Check if at least one link exists
    AT_LEAST_ONE_LINK_EXISTS_FLAG = False
    for item in scan_response["analysis"]["ingredients"]:
        if item["referenceUrl"]:
            AT_LEAST_ONE_LINK_EXISTS_FLAG = True

    # Return two strings
    return [
        f"**{scan_response["name"]}**\n\n**Аллергены**\n{'\n'.join(['* ' + l[0].upper() + l[1:] for l in scan_response["analysis"]["allergens"]])}\n\n**AI анализ**\n{scan_response['aiAnalysis']}\n\n{'**Добавки**' if AT_LEAST_ONE_LINK_EXISTS_FLAG else ''}",
        f"**Состав:**\n{scan_response["composition"]}\n\n_Анализ основани на данных с сайта Добавкам.нет и не является индивидуальной медицинской рекомендацией_"
    ]