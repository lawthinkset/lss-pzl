import math
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

class ClockAngleGenerator(BaseGenerator):
    def __init__(self, page_name: str = "Logic Lab", theme: str = "dark_slate"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        times = [
            (3, 15, "7.5°", ["0°", "7.5°", "15°", "22.5°"]),
            (8, 20, "130°", ["120°", "125°", "130°", "135°"]),
            (2, 40, "160°", ["150°", "160°", "170°", "180°"]),
            (7, 10, "155°", ["145°", "150°", "155°", "160°"]),
            (9, 30, "105°", ["90°", "95°", "100°", "105°"]),
        ]
        h, m, correct, options = random.choice(times)
        random.shuffle(options)
        return {
            "h": h,
            "m": m,
            "correct": correct,
            "options": options
        }

    def render_frame(self, t: float, duration: float) -> np.ndarray:
        img = draw_gradient_background(self.width, self.height, theme=self.theme)
        draw = ImageDraw.Draw(img)
        c = self.puzzle_data
        time_str = f"{c['h']:02d}:{c['m']:02d}"
        draw_header_banner(draw, self.page_name, "CLOCK ANGLE IQ TRAP", f"What is the exact acute angle at {time_str}?")

        cx, cy = 540, 880
        radius = 280
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(25, 30, 42), outline=(255, 215, 0), width=6)

        font_c = get_font(34)
        for num in range(1, 13):
            angle = math.radians(num * 30 - 90)
            nx = cx + int((radius - 50) * math.cos(angle))
            ny = cy + int((radius - 50) * math.sin(angle))
            bbox = font_c.getbbox(str(num))
            draw.text((nx - (bbox[2]-bbox[0])//2, ny - (bbox[3]-bbox[1])//2), str(num), fill=(220, 220, 220), font=font_c)

        m_angle = math.radians(c['m'] * 6 - 90)
        h_angle = math.radians((c['h'] % 12) * 30 + c['m'] * 0.5 - 90)

        mx = cx + int((radius - 70) * math.cos(m_angle))
        my = cy + int((radius - 70) * math.sin(m_angle))
        draw.line([cx, cy, mx, my], fill=(0, 255, 255), width=7)

        hx = cx + int((radius - 120) * math.cos(h_angle))
        hy = cy + int((radius - 120) * math.sin(h_angle))
        draw.line([cx, cy, hx, hy], fill=(255, 215, 0), width=10)

        draw.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(255, 255, 255))

        draw_multiple_choice_options(draw, c["options"], center_y=1400)
        draw_timer_bar(draw, t, duration)
        draw_bottom_cta(draw, t, duration, custom_cta="Hour Hand Moves Too! Don't Fall For The Trap! 👇")
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def get_metadata(self) -> Tuple[str, str, str]:
        return (
            "Clock Angle IQ Trap: What Is The Exact Angle Between Hands? ⏰",
            "Warning: The hour hand moves as minutes pass! Only true math lovers calculate this correctly. What is your angle? 👇",
            "⏰ A, B, C, or D? What is the exact angle? Don't fall for the trap! 👇"
        )
