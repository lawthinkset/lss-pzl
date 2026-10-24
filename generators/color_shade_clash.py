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

class ColorShadeClashGenerator(BaseGenerator):
    def __init__(self, page_name: str = "Logic Lab", theme: str = "dark_slate"):
        super().__init__(page_name=page_name, theme=theme)

    def generate_puzzle_state(self) -> Dict[str, Any]:
        palettes = [
            ((30, 144, 255), (60, 160, 255)),
            ((255, 99, 71), (255, 130, 100)),
            ((46, 204, 113), (76, 220, 133)),
            ((155, 89, 182), (180, 115, 205)),
            ((241, 196, 15), (250, 215, 60)),
            ((230, 126, 34), (245, 150, 65)),
            ((26, 188, 156), (56, 208, 180)),
            ((233, 30, 99), (245, 70, 130)),
        ]
        base_col, diff_col = random.choice(palettes)
        grid_size = 6
        total = grid_size * grid_size
        diff_idx = random.randint(0, total - 1)
        others = [i for i in range(total) if i != diff_idx]
        random.shuffle(others)
        choice_indices = [diff_idx, others[0], others[1], others[2]]
        random.shuffle(choice_indices)
        labels = ["A", "B", "C", "D"]
        label_map = {choice_indices[i]: labels[i] for i in range(4)}
        return {
            "grid_size": grid_size,
            "base_col": base_col,
            "diff_col": diff_col,
            "diff_idx": diff_idx,
            "label_map": label_map,
            "options": ["Tile A", "Tile B", "Tile C", "Tile D"]
        }

    def render_frame(self, t: float, duration: float) -> np.ndarray:
        img = draw_gradient_background(self.width, self.height, theme=self.theme)
        draw = ImageDraw.Draw(img)
        draw_header_banner(draw, self.page_name, "ODD COLOR EYE TEST", "Find the tile with a different shade!")
        state = self.puzzle_data
        grid_size = state["grid_size"]
        base_col = state["base_col"]
        diff_col = state["diff_col"]
        diff_idx = state["diff_idx"]
        label_map = state["label_map"]

        board_size = 720
        start_x = (self.width - board_size) // 2
        start_y = 520
        tile_gap = 14
        tile_w = (board_size - (grid_size - 1) * tile_gap) // grid_size
        font_label = get_font(42)

        idx = 0
        for r in range(grid_size):
            for c in range(grid_size):
                x0 = start_x + c * (tile_w + tile_gap)
                y0 = start_y + r * (tile_w + tile_gap)
                x1 = x0 + tile_w
                y1 = y0 + tile_w
                col = diff_col if idx == diff_idx else base_col
                draw.rounded_rectangle([x0, y0, x1, y1], radius=16, fill=col, outline=(255, 255, 255, 60), width=2)
                if idx in label_map:
                    lbl = label_map[idx]
                    bbox = font_label.getbbox(lbl)
                    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    draw.ellipse([x0 + tile_w//2 - 28, y0 + tile_w//2 - 28, x0 + tile_w//2 + 28, y0 + tile_w//2 + 28], fill=(0, 0, 0, 160))
                    draw.text((x0 + (tile_w - tw)//2, y0 + (tile_w - th)//2 - 4), lbl, fill=(255, 255, 255), font=font_label)
                idx += 1

        draw_multiple_choice_options(draw, state["options"], center_y=1420)
        draw_timer_bar(draw, t, duration)
        draw_bottom_cta(draw, t, duration, custom_cta="96% Pick The Wrong Tile! Drop Your Choice 👇")
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def get_metadata(self) -> Tuple[str, str, str]:
        return (
            "Eye Test: Which Color Tile Is The Impostor? (A, B, C, or D?) 👁️",
            "Only 4% of people with 20/20 color perception can spot the odd tile! Drop your answer below and tag a friend to test their eyes! 👇",
            "🎨 Which tile has the different shade: A, B, C, or D? Debate below! 👇"
        )
