import random
from typing import Dict, Any, Tuple
import numpy as np
from PIL import ImageDraw
import cv2

from core.ui_renderer import (
    get_font,
    draw_gradient_background,
    draw_header_banner,
    draw_timer_bar,
    draw_bottom_cta,
    draw_multiple_choice_options
)
from generators.base_generator import BaseGenerator

class TriangleTrapGenerator(BaseGenerator):
    def __init__(self, page_name: str = "Logic Lab", theme: str = "deep_purple"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        configs = [
            {"correct": 18, "options": ["12", "15", "18", "24"]},
            {"correct": 30, "options": ["20", "25", "30", "36"]},
            {"correct": 27, "options": ["18", "21", "24", "27"]},
        ]
        cfg = random.choice(configs)
        options = list(cfg["options"])
        random.shuffle(options)
        return {
            "correct": cfg["correct"],
            "options": options
        }

    def render_frame(self, t: float, duration: float) -> np.ndarray:
        img = draw_gradient_background(self.width, self.height, theme=self.theme)
        draw = ImageDraw.Draw(img)
        draw_header_banner(draw, self.page_name, "GEOMETRY TRAP", "How many total triangles can you find?")

        apex = (540, 540)
        left = (200, 1150)
        right = (880, 1150)

        draw.polygon([apex, left, right], outline=(0, 255, 255), width=6)

        b1 = (apex[0] - 110, 1150)
        b2 = (apex[0] + 110, 1150)
        draw.line([apex[0], apex[1], b1[0], b1[1]], fill=(0, 255, 255), width=4)
        draw.line([apex[0], apex[1], b2[0], b2[1]], fill=(0, 255, 255), width=4)

        h1_y = 740
        h2_y = 940
        def x_at_y(y):
            ratio = (y - apex[1]) / (1150 - apex[1])
            lx = apex[0] + (left[0] - apex[0]) * ratio
            rx = apex[0] + (right[0] - apex[0]) * ratio
            return int(lx), int(rx)

        lx1, rx1 = x_at_y(h1_y)
        draw.line([lx1, h1_y, rx1, h1_y], fill=(255, 215, 0), width=4)
        lx2, rx2 = x_at_y(h2_y)
        draw.line([lx2, h2_y, rx2, h2_y], fill=(255, 215, 0), width=4)

        draw_multiple_choice_options(draw, self.puzzle_data["options"], center_y=1400)
        draw_timer_bar(draw, t, duration)
        draw_bottom_cta(draw, t, duration, custom_cta="98% Miss The Overlapping Shapes! How Many? 👇")
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def get_metadata(self) -> Tuple[str, str, str]:
        return (
            "Geometry Trap: How Many Triangles Can You Find? 📐",
            "97% miss the hidden overlapping triangles! How many did you count? 👇",
            "📐 Count carefully! How many total triangles do you see? Drop your count below! 👇"
        )
