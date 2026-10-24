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

class MissingDominoGenerator(BaseGenerator):
    def __init__(self, page_name: str = "Logic Lab", theme: str = "dark_slate"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        rule_top = random.choice([1, 2])
        rule_bot = random.choice([1, 2])
        start_top = random.randint(0, 2)
        start_bot = random.randint(4, 6)

        dominoes = []
        for i in range(4):
            top_val = (start_top + i * rule_top) % 7
            bot_val = (start_bot - i * rule_bot) % 7
            dominoes.append((top_val, bot_val))

        target = dominoes[3]
        target_str = f"{target[0]} | {target[1]}"
        decoy1 = f"{(target[0]+1)%7} | {target[1]}"
        decoy2 = f"{target[0]} | {(target[1]+1)%7}"
        decoy3 = f"{(target[0]+2)%7} | {(target[1]-1)%7}"
        options = [target_str, decoy1, decoy2, decoy3]
        random.shuffle(options)

        return {
            "dominoes": dominoes[:3],
            "target": target,
            "options": options
        }

    def render_frame(self, t: float, duration: float) -> np.ndarray:
        img = draw_gradient_background(self.width, self.height, theme=self.theme)
        draw = ImageDraw.Draw(img)
        draw_header_banner(draw, self.page_name, "DOMINO SEQUENCE TEST", "Which domino completes the pattern?")

        doms = self.puzzle_data["dominoes"]
        dw, dh = 150, 280
        total_w = 4 * dw + 3 * 30
        sx = (self.width - total_w) // 2
        sy = 700

        font_pip = get_font(54)

        for i in range(4):
            dx = sx + i * (dw + 30)
            if i < 3:
                top_v, bot_v = doms[i]
                draw.rounded_rectangle([dx, sy, dx + dw, sy + dh], radius=18, fill=(245, 245, 245), outline=(200, 200, 200), width=2)
                draw.line([dx + 12, sy + dh//2, dx + dw - 12, sy + dh//2], fill=(100, 100, 100), width=3)
                draw.text((dx + dw//2 - 16, sy + 45), str(top_v), fill=(20, 20, 20), font=font_pip)
                draw.text((dx + dw//2 - 16, sy + dh//2 + 45), str(bot_v), fill=(20, 20, 20), font=font_pip)
            else:
                draw.rounded_rectangle([dx, sy, dx + dw, sy + dh], radius=18, fill=(255, 69, 0, 40), outline=(255, 69, 0), width=3)
                draw.line([dx + 12, sy + dh//2, dx + dw - 12, sy + dh//2], fill=(255, 69, 0), width=3)
                draw.text((dx + dw//2 - 14, sy + 45), "?", fill=(255, 255, 255), font=font_pip)
                draw.text((dx + dw//2 - 14, sy + dh//2 + 45), "?", fill=(255, 255, 255), font=font_pip)

        draw_multiple_choice_options(draw, self.puzzle_data["options"], center_y=1400)
        draw_timer_bar(draw, t, duration)
        draw_bottom_cta(draw, t, duration, custom_cta="Spot The Hidden Rule! What Is 4th Domino? 👇")
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def get_metadata(self) -> Tuple[str, str, str]:
        return (
            "Domino Sequence Test: Which Domino Completes The Pattern? 🁓",
            "Look closely at the top and bottom dots! Which domino is next in line? 👇",
            "🁓 A, B, C, or D? What is the missing domino? Let's see who gets it first! 👇"
        )
