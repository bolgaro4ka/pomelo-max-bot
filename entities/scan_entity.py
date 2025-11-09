from typing import Optional

class ScanEntity:
    """Entity class representing a product scan."""
    def __init__(self, scan: dict):
        self._data = scan

    @property
    def id(self) -> Optional[str]:
        return self._data.get("id")

    @property
    def name(self) -> str:
        name = self._data.get("name", "")
        if len(name) > 0:
            return name
        return "Без названия"

    @property
    def status(self) -> Optional[str]:
        return self._data.get("status")

    @property
    def ai_analysis(self) -> Optional[dict]:
        return self._data.get("aiAnalysis")

    @property
    def ingredients(self) -> list[dict]:
        analysis = self._data.get("analysis", {})
        return analysis.get("ingredients", [])

    def is_fully_completed(self) -> bool:
        return (
            self.status == "completed"
            and self.ai_analysis is not None
        )

    DANGER_LEVEL_EMOJI = {
        -1: "⚪",
        0: "⚪",
        1: "🟢",
        2: "🟡",
        3: "🟡",
        4: "🟠",
        5: "🔴"
    }

    def get_ingredient_buttons(self) -> dict[str, str]:
        """
        Return list of buttons for ingredients with reference URLs.
        {
            "🟡 Кальций 2 из 5": "https://example.com",
            "🔴 Бензоат натрия 5 из 5": "https://..."
        }
        """
        buttons = {}

        for ingredient in self.ingredients:
            url = ingredient.get("referenceUrl")
            # Skip ingredients without URL
            if not url:
                continue

            name = ingredient.get("name", "Без названия")
            danger = ingredient.get("danger", -1)

            emoji = self.DANGER_LEVEL_EMOJI.get(danger, "⚪")
            truncated_name = name if len(name) <= 20 else name[:20] + "..."
            button_text = f"{emoji} {truncated_name} {danger} из 5"

            buttons[button_text] = url

        return buttons
