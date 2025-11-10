from typing import Optional
import io
import matplotlib.pyplot as plt

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
    
    @staticmethod
    def get_adi_image_buffer(scan_entity: "ScanEntity") -> bytes:
        """
        Generate an ADI pie-chart image and return it as a bytes buffer (PNG format).

        Returns:
            bytes: PNG image data in memory.
        """

        # Get adi
        adi = scan_entity._data.get("analysis", {}).get("additivesDangerIndex", 0)
        adi = max(0, min(100, adi))

        # Color
        if adi < 40:
            color = "#2ecc71"
        elif adi < 70:
            color = "#f1c40f"
        else:
            color = "#e74c3c"

        # Generate image
        fig, ax = plt.subplots(figsize=(3, 3), dpi=150)

        # Progress bar (pie)
        ax.pie(
            [adi, 100 - adi],
            colors=[color, "#e0e0e0"],
            startangle=90,
            wedgeprops={"width": 0.25, "edgecolor": "white"}
        )

        # Center number
        ax.text(0, 0, str(adi), ha="center", va="center", fontsize=28, weight="bold")

        # Label
        ax.text(0, -1.25, "ВРЕДНОСТЬ", ha="center", fontsize=14, weight="bold")

        ax.axis("equal")
        plt.tight_layout()

        # Save to buffer
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", bbox_inches="tight")
        plt.close(fig)
        buffer.seek(0)

        return buffer.getvalue()

