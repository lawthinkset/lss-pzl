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

class BalanceScaleAlgebraGenerator(BaseGenerator):
    def __init__(self, page_name: str = "Logic Lab", theme: str = "vibrant_navy"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        v_circle = random.randint(2, 6)
        v_square = random.randint(4, 9)
        v_triangle = v_circle + v_square
        target = 2 * v_triangle
        step = random.choice([1, 2, 3])
        options = [str(target - step), str(target), str(target + step), str(target + 2*step)]
        random.shuffle(options)
        return {
            "v_circle": v_circle,
            "v_square": v_square,
            "v_triangle": v_triangle,
            "target": target,
            "options": options
        }

    def render_frame(self, t: float, duration: float) -> np.ndarray:
        img = draw_gradient_background(self.width, self.height, theme=self.theme)
        draw = ImageDraw.Draw(img)
        draw_header_banner(draw, self.page_name, "BALANCE SCALE IQ", "Find the value of: ▲ + ▲ = ?")
        c = self.puzzle_data
        font_sym = get_font(52)
        cards = [
            ("SCALE 1", f"● = {c['v_circle']}   |   ■ = {c['v_square']}"),
            ("SCALE 2", f"▲ = ● + ■"),
            ("FINAL SCALE", f"▲ + ▲ = ?")
        ]
        y_start = 540
        for i, (title, eq) in enumerate(cards):
            card_y = y_start + i * 240
            bg_card = (255, 255, 255, 25) if i < 2 else (255, 215, 0, 45)
            draw.rounded_rectangle([140, card_y, self.width - 140, card_y + 190], radius=24, fill=bg_card, outline=(255, 255, 255, 80), width=2)
            draw.text((180, card_y + 25), title, fill=(255, 215, 0) if i==2 else (180, 200, 240), font=get_font(28))
            bbox = font_sym.getbbox(eq)
            ew = bbox[2] - bbox[0]
            draw.text(((self.width - ew)//2, card_y + 85), eq, fill=(255, 255, 255), font=font_sym)

        draw_multiple_choice_options(draw, self.puzzle_data["options"], center_y=1400)
        draw_timer_bar(draw, t, duration)
        draw_bottom_cta(draw, t, duration, custom_cta="98% Get This Wrong On First Try! Solve Below 👇")
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def get_metadata(self) -> Tuple[str, str, str]:
        return (
            "Balance Scale IQ: What Does ▲ + ▲ Equal? ⚖️",
            "Can you solve the weight balance equation? Only 2% can solve this balance algebra equation. What is your answer? 👇",
            "⚖️ What is the exact missing number? Drop your calculation below and debate! 👇"
        )
