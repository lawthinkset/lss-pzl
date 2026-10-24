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

class PatternMatrixGenerator(BaseGenerator):
    def __init__(self, page_name: str = "Logic Lab", theme: str = "vibrant_navy"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        base = random.randint(1, 3)
        correct = base + 4
        options = [str(correct - 2), str(correct - 1), str(correct), str(correct + 1)]
        random.shuffle(options)
        return {
            "base": base,
            "correct": correct,
            "options": options
        }

    def render_frame(self, t: float, duration: float) -> np.ndarray:
        img = draw_gradient_background(self.width, self.height, theme=self.theme)
        draw = ImageDraw.Draw(img)
        draw_header_banner(draw, self.page_name, "MENSA PATTERN MATRIX", "Which number completes the 3x3 matrix?")

        grid_w = 660
        cell_w = grid_w // 3
        sx = (self.width - grid_w) // 2
        sy = 540
        b = self.puzzle_data["base"]
        font_num = get_font(52)

        for r in range(3):
            for c in range(3):
                cx0 = sx + c * cell_w
                cy0 = sy + r * cell_w
                val = b + r + c
                if r == 2 and c == 2:
                    draw.rectangle([cx0, cy0, cx0 + cell_w, cy0 + cell_w], fill=(255, 69, 0, 50), outline=(255, 69, 0), width=4)
                    draw.text((cx0 + cell_w//2 - 16, cy0 + cell_w//2 - 32), "?", fill=(255, 255, 255), font=get_font(64))
                else:
                    draw.rectangle([cx0, cy0, cx0 + cell_w, cy0 + cell_w], fill=(30, 45, 80, 180), outline=(255, 255, 255, 90), width=2)
                    bbox = font_num.getbbox(str(val))
                    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
                    draw.text((cx0 + (cell_w - tw)//2, cy0 + (cell_w - th)//2 - 6), str(val), fill=(255, 255, 255), font=font_num)

        draw_multiple_choice_options(draw, self.puzzle_data["options"], center_y=1400)
        draw_timer_bar(draw, t, duration)
        draw_bottom_cta(draw, t, duration, custom_cta="Only 1% With 130+ IQ Solve This In 10s! 👇")
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def get_metadata(self) -> Tuple[str, str, str]:
        return (
            "Mensa IQ Test: Which Number Completes The 3×3 Grid? 🧠",
            "Only 1% of viewers score 130+ on this pattern matrix. Which option is correct? 👇",
            "🧠 A, B, C, or D? Comment your logic and let's debate! 👇"
        )
