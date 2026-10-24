"""
Procedural Puzzle Generation & Publishing Engine.
"""
import os
import sys
import time
import random
import argparse
from pathlib import Path
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

from generators import ALL_GENERATORS
from upload.facebook_uploader import upload_reel_to_facebook

DEFAULT_PAGE_ID = "1313658835168646"
DEFAULT_PAGE_NAME = "LogicSteps Lens"
DEFAULT_THEME = "vibrant_navy"
PAGE_INDEX = 2
DEFAULT_PINNED_COMMENT = '🔍 Did you spot the number in time or did you need to replay? Comment your answer and how many seconds it took! 👇'

ORDERED_MODES = [
    "grid_hunter",
    "logic_lock",
    "optical_swirl",
    "pemdas_math",
    "rebus_puzzle",
    "word_guess",
    "tangled_wires",
    "matchstick_puzzle",
    "shape_counter",
    "shadow_glitch",
    "pause_silhouette",
    "color_shade_clash",
    "balance_scale",
    "pyramid_math",
    "missing_domino",
    "pattern_matrix",
    "gear_rotation",
    "water_tank",
    "clock_angle",
    "triangle_trap"
]

def determine_slot(explicit_slot: int = None) -> int:
    if explicit_slot is not None and 1 <= explicit_slot <= 5:
        return explicit_slot
    utc_hour = datetime.utcnow().hour
    if 6 <= utc_hour < 10:
        return 1
    elif 10 <= utc_hour < 14:
        return 2
    elif 14 <= utc_hour < 18:
        return 3
    elif 18 <= utc_hour < 22:
        return 4
    else:
        return 5

def pick_mode_for_slot(slot: int) -> str:
    day_of_year = datetime.utcnow().timetuple().tm_yday
    mode_idx = (day_of_year * 3 + (slot - 1) * 2 + PAGE_INDEX * 7) % len(ORDERED_MODES)
    return ORDERED_MODES[mode_idx]

def run(slot: int = None, forced_mode: str = None, should_publish: bool = False):
    page_id = os.getenv("FB_PAGE_ID", DEFAULT_PAGE_ID).strip()
    page_name = os.getenv("FB_PAGE_NAME", DEFAULT_PAGE_NAME).strip()
    theme = os.getenv("FB_THEME", DEFAULT_THEME).strip()
    pinned_comment = os.getenv("FB_PINNED_COMMENT", DEFAULT_PINNED_COMMENT).strip()
    page_token = os.getenv("FB_PAGE_TOKEN")

    active_slot = determine_slot(slot)
    chosen_mode = forced_mode if (forced_mode and forced_mode in ALL_GENERATORS) else pick_mode_for_slot(active_slot)

    print("=" * 60)
    print(f"🎬 ENGINE RUN: Slot #{active_slot} | Mode: [{chosen_mode.upper()}] | Theme: [{theme}]")
    print(f"Target: {page_name} ({page_id})")
    print("=" * 60)

    generator_cls = ALL_GENERATORS[chosen_mode]
    generator = generator_cls(page_name=page_name, theme=theme)

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_video = OUTPUT_DIR / f"reel_{chosen_mode}_{ts}.mp4"

    # Render exactly 14s @ 30fps (420 frames)
    generator.render_video(
        output_mp4=str(out_video),
        duration=14.0,
        fps=30
    )

    title, description, _gen_pinned = generator.get_metadata()
    comment_to_post = pinned_comment if pinned_comment else _gen_pinned

    print(f"[engine] Video rendered: {out_video.name}")
    print(f"[engine] Title: {title}")

    if should_publish:
        print("[engine] Uploading to Facebook Reels...")
        upload_res = upload_reel_to_facebook(
            video_path=str(out_video),
            title=title,
            description=description,
            page_id=page_id,
            access_token=page_token,
            pinned_comment=comment_to_post
        )
        if upload_res and upload_res.get("status") == "success":
            print(f"[engine] ✅ Published successfully! Video ID: {upload_res.get('video_id')}")
        else:
            print(f"[engine] ❌ Upload failed: {upload_res}")
            sys.exit(1)
    else:
        print("[engine] Mode is render only (not publishing).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", type=int, default=None, help="Daily slot 1-5")
    parser.add_argument("--mode", type=str, default=None, help="Force puzzle mode")
    parser.add_argument("--publish", action="store_true", help="Publish to Facebook Reels")
    args = parser.parse_args()

    run(slot=args.slot, forced_mode=args.mode, should_publish=args.publish)
