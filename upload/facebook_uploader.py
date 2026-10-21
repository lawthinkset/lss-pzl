"""
Facebook Reels Direct Uploader via Meta Graph API v21.0
Robust dual-strategy publisher:
1. Fast direct multipart upload to Meta Graph Video API (1 single API call).
2. Resumable chunked Reels publishing fallback.
Full support for environment variables, secrets, and optional .env loading.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Optional .env loading without hard dependency on python-dotenv
try:
    from dotenv import load_dotenv
    for env_candidate in [Path(".env"), Path("../.env"), Path(__file__).resolve().parent / ".env", Path(__file__).resolve().parent.parent / ".env"]:
        if env_candidate.exists():
            load_dotenv(dotenv_path=env_candidate, override=True)
            break
    else:
        load_dotenv()
except Exception:
    pass

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
        os.getenv("FB_PAGE_TOKEN") or
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
    Publishes video to Facebook Page with automatic strategy selection:
    Primary: Single multipart POST to https://graph-video.facebook.com/v21.0/{page_id}/videos
    Fallback: 3-step Resumable Video Reels Publishing session
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
    safe_print("[FACEBOOK] REEL PUBLISHING PIPELINE")
    safe_print(f"Target Page ID: {page_id}")
    safe_print(f"Video File: {vid_path.name} ({file_size_mb:.2f} MB)")
    safe_print(f"Title: {str(title)[:70]}")
    safe_print("=" * 60)

    # Prepare description with pinned comment
    full_desc = str(description)
    if pinned_comment and pinned_comment.strip():
        full_desc = f"{full_desc}\n\n📌 {pinned_comment.strip()}"

    # Strategy 1: Direct single-call upload (Fastest, 1 API call)
    upload_url = f"https://graph-video.facebook.com/v21.0/{page_id}/videos"
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
        safe_print("[facebook] Strategy 1: Sending direct multipart upload...")
        res = requests.post(upload_url, data=data, files=files, timeout=600)

        if res.status_code in [200, 201]:
            res_data = res.json()
            video_id = res_data.get("id") or res_data.get("video_id")
            if video_id:
                safe_print(f"[facebook] ✅ SUCCESS! Published (Video ID: {video_id})")
                safe_print(f"[facebook] URL: https://www.facebook.com/{video_id}")
                return {
                    "status": "success",
                    "id": str(video_id),
                    "video_id": str(video_id),
                    "url": f"https://www.facebook.com/{video_id}",
                    "strategy": "direct"
                }

        safe_print(f"[facebook] Strategy 1 returned {res.status_code}: {res.text[:200]}, activating fallback...")
    except Exception as e:
        safe_print(f"[facebook] Strategy 1 exception: {e}, activating fallback...")
    finally:
        if video_fp:
            try:
                video_fp.close()
            except Exception:
                pass

    # Strategy 2: Resumable chunked Reels API fallback
    try:
        safe_print("[facebook] Strategy 2: Initializing resumable video_reels session...")
        base_url = f"https://graph.facebook.com/v21.0/{page_id}/video_reels"
        file_size = vid_path.stat().st_size
        r_start = requests.post(base_url, data={
            "access_token": access_token,
            "upload_phase": "start",
            "file_size": file_size
        }, timeout=30)
        if r_start.status_code != 200:
            return {"status": "failed", "error": f"Reels session start failed: {r_start.text[:300]}"}

        s_json = r_start.json()
        video_id = s_json.get("video_id")
        reels_upload_url = s_json.get("upload_url")

        with open(vid_path, "rb") as f:
            v_bytes = f.read()

        r_trans = requests.post(reels_upload_url, headers={
            "Authorization": f"OAuth {access_token}",
            "offset": "0",
            "file_size": str(file_size)
        }, data=v_bytes, timeout=180)

        if r_trans.status_code not in (200, 201):
            return {"status": "failed", "error": f"Reels transfer failed: {r_trans.text[:300]}"}

        r_finish = requests.post(base_url, data={
            "access_token": access_token,
            "upload_phase": "finish",
            "video_id": video_id,
            "video_state": "PUBLISHED",
            "description": full_desc[:5000],
            "title": str(title)[:100]
        }, timeout=30)

        if r_finish.status_code == 200:
            safe_print(f"[facebook] ✅ SUCCESS via Resumable Reels API! (Video ID: {video_id})")
            return {
                "status": "success",
                "id": str(video_id),
                "video_id": str(video_id),
                "url": f"https://www.facebook.com/{video_id}",
                "strategy": "resumable"
            }
        return {"status": "failed", "error": f"Reels finish failed: {r_finish.text[:300]}"}

    except Exception as e:
        safe_print(f"[facebook] [ERROR] All publishing strategies failed: {e}")
        return {"status": "failed", "error": str(e)}

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
