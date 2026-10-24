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

class GearRotationGenerator(BaseGenerator):
    def __init__(self, page_name: str = "Logic Lab", theme: str = "dark_slate"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        num_gears = 5
        correct = "Clockwise" if num_gears % 2 == 1 else "Counter-Clockwise"
        return {
            "num_gears": num_gears,
            "correct": correct,
            "options": ["Clockwise", "Counter-Clockwise", "Doesn't Turn", "Stuck"]
        }

    def render_frame(self, t: float, duration: float) -> np.ndarray:
        img = draw_gradient_background(self.width, self.height, theme=self.theme)
        draw = ImageDraw.Draw(img)
        draw_header_banner(draw, self.page_name, "GEAR PHYSICS CHALLENGE", "If Gear A turns Clockwise, which way does Gear E turn?")

        centers = [(240, 680), (440, 840), (640, 680), (840, 840), (540, 1080)]
        labels = ["A", "B", "C", "D", "E"]
        colors = [(255, 99, 71), (46, 204, 113), (52, 152, 219), (155, 89, 182), (241, 196, 15)]

        font_gear = get_font(48)
        radius = 90
        for i, (gx, gy) in enumerate(centers):
            col = colors[i]
            draw.ellipse([gx - radius, gy - radius, gx + radius, gy + radius], fill=col, outline=(255, 255, 255), width=3)
            draw.ellipse([gx - 30, gy - 30, gx + 30, gy + 30], fill=(20, 20, 25))
            lbl = labels[i]
            bbox = font_gear.getbbox(lbl)
            draw.text((gx - (bbox[2]-bbox[0])//2, gy - 75), lbl, fill=(255, 255, 255), font=font_gear)

        draw.text((150, 540), "🔄 CLOCKWISE", fill=(46, 204, 113), font=get_font(32))

        draw_multiple_choice_options(draw, self.puzzle_data["options"], center_y=1420)
        draw_timer_bar(draw, t, duration)
        draw_bottom_cta(draw, t, duration, custom_cta="97% Trace It Wrong! Clockwise Or Counter? 👇")
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def get_metadata(self) -> Tuple[str, str, str]:
        return (
            "Gear Physics Debate: Which Way Does Gear E Turn? ⚙️",
            "Most people get dizzy tracing the gear teeth! Will Gear E turn Clockwise or Counter-Clockwise? 👇",
            "⚙️ Clockwise or Counter-Clockwise? Trace the cogs and drop your answer! 👇"
        )
