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

    @staticmethod
    def text_to_slug(text: str) -> str:
        """
        Convert text to slug: lowercase, replace spaces with hyphens,
        remove special characters, escape for URL.
        """
        import re
        # Convert to lowercase
        slug = text.lower()
        # Replace spaces and underscores with hyphens
        slug = re.sub(r'[\s_]+', '-', slug)
        # Remove special characters except hyphens
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        # Strip hyphens from start and end
        slug = slug.strip('-')
        return slug

    def get_ingredient_buttons(self) -> dict[str, str | None]:
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
            if not url:
                continue
            name = ingredient.get("name", "Без названия")
            danger = ingredient.get("danger", -1)
            if danger < 0:
                danger = "?"

            emoji = self.DANGER_LEVEL_EMOJI.get(danger, "⚪")
            truncated_name = name if len(name) <= 20 else name[:20] + "..."
            button_text = f"{emoji} {truncated_name} {danger} из 5"

            buttons[button_text] = url  # url can be None

        return buttons
    
    @staticmethod
    def get_adi_image_buffer(scan_entity: "ScanEntity") -> bytes:
        """
        Generate an ADI image similar to the provided sample: thick arc, rounded ends, gradient background, big number, label, rounded square.
        Returns:
            bytes: PNG image data in memory.
        """
        import numpy as np
        from matplotlib.patches import FancyBboxPatch, Arc
        from matplotlib.colors import LinearSegmentedColormap

        adi = scan_entity._data.get("analysis", {}).get("additivesDangerIndex", 0)
        adi = max(0, min(100, adi))

        # Color selection (orange for 52)
        if adi < 40:
            color = "#2ecc71"
        elif adi < 70:
            color = "#f1c40f"
        else:
            color = "#e74c3c"

        # Image size - increased for better quality
        size = 600
        dpi = 120
        fig, ax = plt.subplots(figsize=(size/dpi, size/dpi), dpi=dpi)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        # Draw rounded rectangle background (white)
        rect = FancyBboxPatch((0, 0), 1, 1,
                              boxstyle="round,pad=0.04,rounding_size=0.15",
                              linewidth=0, facecolor="#fcfcfc")
        ax.add_patch(rect)

        # Arc parameters - empty side down, fills from left to right, rotated left by ~45 degrees
        center = (0.5, 0.5)
        radius = 0.38
        width = 0.073  # Reduced thickness (was 0.13)
        rotation = -45  # degrees, rotate the whole scale counter-clockwise (left by 90°)
        total_span = 270  # degrees of the visible arc

        # Background arc angles (rotated)
        theta1_bg = 0 + rotation
        theta2_bg = total_span + rotation

        # Foreground (filled) angles: fill from left to right so foreground spans from
        # the left edge towards the bottom (towards theta2_bg). Compute the left bound
        # based on adi percent.
        theta2_fg = theta2_bg
        theta1_fg = theta2_bg - total_span * (adi / 100)

        # Draw background arc (gray)
        arc_bg = Arc(center, 2 * radius, 2 * radius, angle=0, theta1=theta1_bg, theta2=theta2_bg,
                     lw=size * width, color="#ececec", capstyle='round')
        ax.add_patch(arc_bg)

        # Draw value arc (colored)
        if adi > 0:
            arc_fg = Arc(center, 2 * radius, 2 * radius, angle=0, theta1=theta1_fg, theta2=theta2_fg,
                         lw=size * width, color=color, capstyle='round')
            ax.add_patch(arc_fg)

        # Draw number
        ax.text(0.5, 0.47, str(adi), ha="center", va="center", fontsize=72, weight="700",
                color="#1c1c28")

        # Draw label
        ax.text(0.5, 0.08, "Вредность", ha="center", va="center", fontsize=36, weight="bold",
                color="#1c1c28")

        # Remove axes
        ax.set_xticks([])
        ax.set_yticks([])

        # Save to buffer
        buffer = io.BytesIO()
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        fig.savefig(buffer, format="png", bbox_inches="tight", pad_inches=0, transparent=False)
        plt.close(fig)
        buffer.seek(0)
        return buffer.getvalue()


if __name__ == '__main__':
    from pathlib import Path
    
    # Create test directory if it doesn't exist
    test_dir = Path(__file__).parent.parent / "test"
    test_dir.mkdir(exist_ok=True)
    
    # Create test scan data
    test_scan = {
        "id": "test_1",
        "name": "Test Product",
        "status": "completed",
        "analysis": {
            "additivesDangerIndex": 52
        }
    }
    
    # Create ScanEntity and generate image
    entity = ScanEntity(test_scan)
    image_buffer = ScanEntity.get_adi_image_buffer(entity)
    
    # Save to file
    output_path = test_dir / "adi_test_52.png"
    with open(output_path, "wb") as f:
        f.write(image_buffer)
    
    print(f"Image saved to: {output_path}")
