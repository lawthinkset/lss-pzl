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

class WaterTankRaceGenerator(BaseGenerator):
    def __init__(self, page_name: str = "Logic Lab", theme: str = "vibrant_navy"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        return {
            "options": ["Tank 1", "Tank 2", "Tank 3", "Tank 4"]
        }

    def render_frame(self, t: float, duration: float) -> np.ndarray:
        img = draw_gradient_background(self.width, self.height, theme=self.theme)
        draw = ImageDraw.Draw(img)
        draw_header_banner(draw, self.page_name, "WATER TANK TRAP", "Tap is running! Which tank fills up FIRST?")

        tanks = [(220, 680), (620, 680), (220, 1020), (620, 1020)]
        tw, th = 220, 220
        font_t = get_font(56)

        draw.line([330, 790, 730, 790], fill=(80, 120, 180), width=16)
        draw.line([330, 900, 330, 1020], fill=(80, 120, 180), width=16)
        draw.line([730, 900, 730, 1020], fill=(80, 120, 180), width=16)

        draw.rectangle([510, 782, 530, 798], fill=(255, 69, 0))

        for i, (tx, ty) in enumerate(tanks):
            draw.rounded_rectangle([tx, ty, tx + tw, ty + th], radius=14, fill=(15, 25, 45, 220), outline=(100, 180, 255), width=4)
            lbl = f"#{i+1}"
            bbox = font_t.getbbox(lbl)
            draw.text((tx + (tw - (bbox[2]-bbox[0]))//2, ty + 70), lbl, fill=(255, 255, 255), font=font_t)

        draw.text((490, 540), "🚰 TAP", fill=(100, 220, 255), font=get_font(42))

        draw_multiple_choice_options(draw, self.puzzle_data["options"], center_y=1420)
        draw_timer_bar(draw, t, duration)
        draw_bottom_cta(draw, t, duration, custom_cta="Look Closely At Blocked Pipes! Who Wins? 👇")
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def get_metadata(self) -> Tuple[str, str, str]:
        return (
            "Water Tank Physics Trap: Which Tank Fills Up First? 🚰",
            "Watch the pipe heights and blocked valves carefully! 99% fail on their first look! Which tank fills first? 👇",
            "🚰 Which tank fills first: Tank 1, 2, 3, or 4? Prove your logic below! 👇"
        )
