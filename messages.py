"""
This module contains functions used in the Pomelo bot for generating messages.

Consains consts:

- HELLO_MSG - A string representing the initial message sent to the user when the bot is started.
- ABOUT_MSG - A string representing the about message.
- DISCLAIMER_MSG - A string representing the disclaimer message.
- HELP_MSG - A string representing the help message.

Contains functions for:

- Generating a list of two strings representing the scan response information.

By Bolgaro4ka / 2025

"""



HELLO_MSG = """**Привет 👋 Я — бот Pomelo 🍋**

Помогаю разобрать состав продуктов: 
- Нахожу опасные Е-добавки
-️ Оцениваю вредность
- Даю рекомендации по питанию 
- Предупреждаю о наличии аллергенов

_Введите /help, чтобы узнать список команд_

📸 Отправь текст или фото состава, чтобы получить детальный анализ"""

ABOUT_MSG = """**🥭 О Pomelo**
Это чат-бот для анализа состава продуктов

**📸 Сфотографируйте состав — и получите подробный анализ всех ингредиентов!**

Pomelo выявляет опасные Е-добавки, сахар, консерванты, красители и аллергены и помогает понять, насколько продукт безопасен для вашего здоровья

**🎓 Анализ основан на точных алгоритмах и большой научной базе данных добавок**

С помощью OCR (оптическое распознавание символов) мы получаем текст состава и с помощью большой научной базы данных добавок, которая собрана из открытых источников (например, сайт добавкам.нет), считаем индекс вредности - число от 0 до 100, которое показывает суммарную вредность продукта. Благодаря чёткому алгоритму анализа результат сканирования для одинаковых продуктов будет одинаковым

Также для дополнительного контекстного анализа мы используем нейросеть-нутрициолога, которая даёт полезные рекомендации.

**🍏 Сканируйте состав — выбирайте продукты, безопасные для здоровья**

70% продуктов содержат добавки, влияющие на здоровье. Наш сканер помогает осознанно выбирать — без сложных терминов и скрытых ингредиентов
"""

DISCLAIMER_MSG = """**⚠ Дисклеймер**

Анализ основан на данных из открытых источников и сайта Добавкам.нет и не является индивидуальной медицинской рекомендацией.

Всегда проверяйте состав самостоятельно.
"""

HELP_MSG = """**🕹 Список команд**

`/start` - перезапустить бота
`/help` - список команд
`/scanner` - сканер продуктов
`/about` - о Pomelo
`/disclaimer` - дисклеймер
"""

SCANNER_MSG = """**📸 Отправь текст или фото состава, чтобы получить детальный анализ**"""

def get_scan_msg(scan_result: dict) -> list[str]:
    """
    Generate a list of two strings representing the scan response information.

    Args:
        scan_result (dict): The scan response containing the analysis information.

    Returns:
        list[str]: A list of two strings. The first string contains the name, allergens, AI analysis, and additives information. The second string contains the composition and a disclaimer.

    This function takes a scan response dictionary as input and generates two strings representing the scan response information. The first string includes the name, allergens, AI analysis, and additives information. The second string includes the composition and a disclaimer. The function iterates over the ingredients in the scan response and checks if any of them have a reference URL. If a reference URL is found, the flag variable is set to True. The function then constructs the two strings using the information from the scan response dictionary.
    """

    # Check if at least one link exists
    AT_LEAST_ONE_LINK_EXISTS_FLAG = False
    for item in scan_result["analysis"]["ingredients"]:
        if item["referenceUrl"]:
            AT_LEAST_ONE_LINK_EXISTS_FLAG = True

    # Return two strings
    return [
        f"**{scan_result["name"]}**\n\n**Аллергены**\n{'\n'.join(['* ' + l[0].upper() + l[1:] for l in scan_result["analysis"]["allergens"]])}\n\n**AI анализ**\n{scan_result['aiAnalysis']}\n\n{'**Добавки**' if AT_LEAST_ONE_LINK_EXISTS_FLAG else ''}",
        f"**Состав:**\n{scan_result["composition"]}"
    ]