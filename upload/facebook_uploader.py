"""
Facebook Reels Direct Uploader via Meta Graph API v21.0 - STRICTLY 1 SINGLE META API CALL
Direct multipart upload to Meta Graph Video API endpoint.
Publishes directly to Facebook Page feed in exactly 1 HTTP request.
Zero chunking sessions, zero status polling loops, zero comment retries.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

for env_candidate in [Path(".env"), Path("../.env"), Path(__file__).resolve().parent / ".env", Path(__file__).resolve().parent.parent / ".env"]:
    if env_candidate.exists():
        load_dotenv(dotenv_path=env_candidate, override=True)
        break
else:
    load_dotenv()


LOCAL_TOKENS_PATHS = [
    Path(r"C:\Users\kreg9\logic_pages_tokens.json"),
    Path(r"C:\Users\kreg9\facebook_pages_tokens.json")
]


def safe_print(msg: str):
    try:
        print(msg)
    except Exception:
        print(msg.encode("ascii", "replace").decode("ascii"))


def load_page_tokens() -> Dict[str, Any]:
    tokens = {}
    env_json = os.getenv("FACEBOOK_PAGES_JSON") or os.getenv("PAGE_TOKENS_JSON")
    if env_json:
        try:
            tokens = json.loads(env_json)
        except Exception:
            pass

    for p in LOCAL_TOKENS_PATHS:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        tokens.update(data)
            except Exception:
                pass
    return tokens


def get_token_for_page(page_id: str, tokens: Dict[str, Any]) -> Optional[str]:
    entry = tokens.get(str(page_id)) or tokens.get(page_id)
    if isinstance(entry, dict):
        return entry.get("access_token")
    elif isinstance(entry, str):
        return entry
    return (
        os.getenv("FACEBOOK_ACCESS_TOKEN") or
        os.getenv("FB_ACCESS_TOKEN") or
        os.getenv("META_ACCESS_TOKEN")
    )


def upload_reel_to_facebook(
    video_path: str,
    title: str,
    description: str,
    page_id: str,
    access_token: Optional[str] = None,
    pinned_comment: Optional[str] = None
) -> Dict[str, Any]:
    """
    Publishes video to Facebook Page in EXACTLY ONE Meta Graph API call.
    Single direct multipart POST to https://graph-video.facebook.com/v21.0/{page_id}/videos
    """
    import requests

    if not access_token:
        tokens = load_page_tokens()
        access_token = get_token_for_page(page_id, tokens)

    if not access_token or not page_id:
        err = f"No access token or page_id found for Page ID {page_id}"
        safe_print(f"[facebook] [ERROR] {err}")
        return {"status": "failed", "error": err}

    vid_path = Path(video_path)
    if not vid_path.exists():
        err = f"Video file not found: {video_path}"
        safe_print(f"[facebook] [ERROR] {err}")
        return {"status": "failed", "error": err}

    file_size_mb = vid_path.stat().st_size / (1024 * 1024)

    safe_print("\n" + "=" * 60)
    safe_print("[FACEBOOK] REEL PUBLISHING (STRICTLY 1 META API CALL)")
    safe_print(f"Target Page ID: {page_id}")
    safe_print(f"Video File: {vid_path.name} ({file_size_mb:.2f} MB)")
    safe_print(f"Title: {str(title)[:70]}")
    safe_print("=" * 60)

    upload_url = f"https://graph-video.facebook.com/v21.0/{page_id}/videos"

    # Merge pinned comment into description if provided
    full_desc = str(description)
    if pinned_comment and pinned_comment.strip():
        full_desc = f"{full_desc}\n\n📌 {pinned_comment.strip()}"

    data = {
        "title": str(title)[:100],
        "description": full_desc[:5000],
        "published": "true",
        "access_token": access_token
    }

    video_fp = None
    try:
        video_fp = open(vid_path, "rb")
        files = {
            "source": (vid_path.name, video_fp, "video/mp4")
        }

        safe_print("[facebook] Sending single multipart POST request (API Call 1 of 1)...")
        res = requests.post(upload_url, data=data, files=files, timeout=600)

        if res.status_code in [200, 201]:
            res_data = res.json()
            video_id = res_data.get("id") or res_data.get("video_id")
            if video_id:
                safe_print(f"[facebook] ✅ SUCCESS! Reel Published (Video ID: {video_id})")
                safe_print(f"[facebook] URL: https://www.facebook.com/{video_id}")
                return {
                    "status": "success",
                    "id": str(video_id),
                    "video_id": str(video_id),
                    "url": f"https://www.facebook.com/{video_id}",
                    "api_calls_made": 1
                }

        safe_print(f"[facebook] [ERROR] Response {res.status_code}: {res.text[:400]}")
        return {"status": "failed", "error": res.text[:400]}

    except Exception as e:
        safe_print(f"[facebook] [ERROR] Single-call upload exception: {e}")
        return {"status": "failed", "error": str(e)}
    finally:
        if video_fp:
            try:
                video_fp.close()
            except Exception:
                pass


def upload_to_facebook(video_path, description, title="Video"):
    """Compatibility wrapper."""
    page_id = os.getenv("FACEBOOK_PAGE_ID") or os.getenv("FB_PAGE_ID")
    access_token = os.getenv("FACEBOOK_ACCESS_TOKEN") or os.getenv("FB_ACCESS_TOKEN")
    return upload_reel_to_facebook(
        video_path=video_path,
        title=title,
        description=description,
        page_id=page_id,
        access_token=access_token
    )
