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

class PyramidNumberFlowGenerator(BaseGenerator):
    def __init__(self, page_name: str = "Logic Lab", theme: str = "deep_purple"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        row3 = [random.randint(1, 5) for _ in range(4)]
        row2 = [row3[i] + row3[i+1] for i in range(3)]
        row1 = [row2[i] + row2[i+1] for i in range(2)]
        top = row1[0] + row1[1]

        target = top
        step = random.choice([2, 4, 5])
        options = [str(target - step), str(target), str(target + step), str(target + 2*step)]
        random.shuffle(options)

        return {
            "row3": row3,
            "row2": row2,
            "row1": row1,
            "top": top,
            "options": options
        }

    def render_frame(self, t: float, duration: float) -> np.ndarray:
        img = draw_gradient_background(self.width, self.height, theme=self.theme)
        draw = ImageDraw.Draw(img)
        draw_header_banner(draw, self.page_name, "PYRAMID MATH PUZZLE", "Upper brick = sum of the 2 bricks below it!")

        c = self.puzzle_data
        font_num = get_font(42)
        font_q = get_font(56)

        brick_w, brick_h = 130, 90
        pyramid_y = 560

        x_top = (self.width - brick_w) // 2
        draw.rounded_rectangle([x_top, pyramid_y, x_top + brick_w, pyramid_y + brick_h], radius=16, fill=(255, 69, 0, 180), outline=(255, 255, 255), width=3)
        draw.text((x_top + 45, pyramid_y + 12), "?", fill=(255, 255, 255), font=font_q)

        y1 = pyramid_y + brick_h + 16
        for j in range(2):
            xj = self.width // 2 - brick_w - 8 + j * (brick_w + 16)
            draw.rounded_rectangle([xj, y1, xj + brick_w, y1 + brick_h], radius=16, fill=(40, 60, 100, 200), outline=(255, 255, 255, 100), width=2)
            val = str(c["row1"][j])
            bbox = font_num.getbbox(val)
            draw.text((xj + (brick_w - (bbox[2]-bbox[0]))//2, y1 + 22), val, fill=(255, 255, 255), font=font_num)

        y2 = y1 + brick_h + 16
        for j in range(3):
            xj = self.width // 2 - int(1.5 * brick_w) - 16 + j * (brick_w + 16)
            draw.rounded_rectangle([xj, y2, xj + brick_w, y2 + brick_h], radius=16, fill=(40, 60, 100, 200), outline=(255, 255, 255, 100), width=2)
            val = str(c["row2"][j])
            bbox = font_num.getbbox(val)
            draw.text((xj + (brick_w - (bbox[2]-bbox[0]))//2, y2 + 22), val, fill=(255, 255, 255), font=font_num)

        y3 = y2 + brick_h + 16
        for j in range(4):
            xj = self.width // 2 - 2 * brick_w - 24 + j * (brick_w + 16)
            draw.rounded_rectangle([xj, y3, xj + brick_w, y3 + brick_h], radius=16, fill=(40, 60, 100, 200), outline=(255, 255, 255, 100), width=2)
            val = str(c["row3"][j])
            bbox = font_num.getbbox(val)
            draw.text((xj + (brick_w - (bbox[2]-bbox[0]))//2, y3 + 22), val, fill=(255, 255, 255), font=font_num)

        draw_multiple_choice_options(draw, c["options"], center_y=1400)
        draw_timer_bar(draw, t, duration)
        draw_bottom_cta(draw, t, duration, custom_cta="Can You Reach The Top? Solve Below 👇")
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def get_metadata(self) -> Tuple[str, str, str]:
        return (
            "Pyramid Math Challenge: What Number Goes At The Top? 🔺",
            "Every upper brick is the sum of the two bricks below it! Can you crack the top number? 👇",
            "🔺 95% get stuck on this brick pyramid! What is the top number? Drop it below! 👇"
        )
