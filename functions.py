import os
import matplotlib.pyplot as plt


def get_adi_image_path(scan_response: dict, folder: str = "adi_cache") -> str:
    """
    Генерирует PNG для additivesDangerIndex, если файла ещё нет.
    Возвращает путь к изображению (кэширование по adi).
    """

    # --- получаем adi ---
    adi = scan_response.get("analysis", {}).get("additivesDangerIndex", 0)
    adi = max(0, min(100, adi))

    # --- создаём папку ---
    os.makedirs(folder, exist_ok=True)

    # --- путь к файлу ---
    file_path = os.path.join(folder, f"adi_{adi}.png")

    # --- если файл уже есть — возвращаем его ---
    if os.path.exists(file_path):
        return file_path

    # --- подбираем цвет ---
    if adi < 40:
        color = "#2ecc71"
    elif adi < 70:
        color = "#f1c40f"
    else:
        color = "#e74c3c"

    # --- генерируем картинку ---
    fig, ax = plt.subplots(figsize=(3, 3), dpi=150)

    # прогресс-бар
    ax.pie(
        [adi, 100 - adi],
        colors=[color, "#e0e0e0"],
        startangle=90,
        wedgeprops={"width": 0.25, "edgecolor": "white"}
    )

    # число в центре
    ax.text(0, 0, str(adi), ha="center", va="center", fontsize=28, weight="bold")

    # подпись
    ax.text(0, -1.25, "ВРЕДНОСТЬ", ha="center", fontsize=14, weight="bold")

    ax.axis("equal")
    plt.tight_layout()

    # сохраняем файл
    fig.savefig(file_path, format="png", bbox_inches="tight")
    plt.close(fig)

    return file_path



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
    d = {}
    for item in res["analysis"]["ingredients"]:
        if not item["referenceUrl"]:
            continue
        d[f"{DANGER_LEVEL[item['danger']]} {item['name'] if len(item["name"]) < 20 else (item['name'][:20] + '...')} {item['danger']} из 5"] = item["referenceUrl"]

    return d