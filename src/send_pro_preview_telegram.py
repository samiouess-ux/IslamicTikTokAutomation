"""Explicit, isolated Telegram sender for candidate-only Pro previews.

This module never touches the production delivery ledger or rotation history.
It requires a separate Pro preview bot/chat configuration and an explicit CLI
confirmation. A transport error is treated as an unknown outcome; it is never
retried automatically.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import urllib.request
from pathlib import Path

from validate_content_manifest import validate_content_manifest

MAX_VIDEO_BYTES = 50 * 1024 * 1024
MAX_CAPTION_CHARS = 1024
PREVIEW_PREFIX = "PREVIEW — NOT APPROVED FOR POSTING"


def validate_preview_manifest(data: dict) -> None:
    if data.get("content_type") not in {"dua", "dhikr"}:
        raise ValueError("Pro preview sender accepts dua/dhikr only.")
    if data.get("lifecycle_status") != "candidate_preview" or data.get("preview_only") is not True:
        raise ValueError("Only candidate_preview manifests can be sent through this isolated preview sender.")
    if data.get("rotation_approved") is True:
        raise ValueError("A preview candidate must not be approved for production rotation.")
    validate_content_manifest(data, allow_candidate_preview=True)


def build_preview_caption(data: dict) -> str:
    validate_preview_manifest(data)
    title = str(data.get("title_ar", "")).strip()
    arabic_items = [str(item["arabic"]).strip() for item in data["items"]]
    item_text = "\n\n".join(arabic_items)
    caption = "\n\n".join(part for part in (
        PREVIEW_PREFIX,
        "معاينة خاصة للمراجعة فقط",
        title,
        item_text,
        "لا تنشر هذا الفيديو. ينتظر مراجعة النص والموافقة الصريحة.",
    ) if part)
    if len(caption) > MAX_CAPTION_CHARS:
        raise ValueError(f"Preview caption exceeds Telegram's {MAX_CAPTION_CHARS}-character limit.")
    return caption


def send_preview(video_path: Path, manifest_path: Path, token: str, chat_id: str,
                 *, confirmed: bool = False) -> dict:
    if not confirmed:
        raise PermissionError("Explicit --confirm-preview-send is required before any Telegram request.")
    if not token.strip() or not chat_id.strip():
        raise ValueError("Separate PRO_PREVIEW_TG_BOT_TOKEN and PRO_PREVIEW_TELEGRAM_CHAT_ID are required.")
    if not chat_id.strip().isdigit() or int(chat_id) <= 0:
        raise ValueError("Preview destination must be a positive numeric private-chat ID.")
    if not video_path.is_file() or video_path.stat().st_size == 0:
        raise FileNotFoundError(f"Preview MP4 is missing or empty: {video_path}")
    if not video_path.name.startswith("PREVIEW-ONLY-") or video_path.suffix.lower() != ".mp4":
        raise ValueError("Only PREVIEW-ONLY-*.mp4 files can be sent by this sender.")
    if video_path.stat().st_size > MAX_VIDEO_BYTES:
        raise ValueError("Preview MP4 exceeds Telegram's 50 MB sendVideo limit.")

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    caption = build_preview_caption(data)
    boundary = "----DuaAdhkarProPreview" + secrets.token_hex(16)
    body = b"".join([
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n{chat_id}\r\n".encode(),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"caption\"\r\n\r\n{caption}\r\n".encode("utf-8"),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"supports_streaming\"\r\n\r\ntrue\r\n".encode(),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"video\"; filename=\"{video_path.name}\"\r\nContent-Type: video/mp4\r\n\r\n".encode(),
        video_path.read_bytes(),
        f"\r\n--{boundary}--\r\n".encode("ascii"),
    ])
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token.strip()}/sendVideo",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )

    # A timeout or lost response may follow successful delivery. Never retry here.
    with urllib.request.urlopen(request, timeout=180) as response:
        result = json.loads(response.read().decode("utf-8"))
    if not result.get("ok") or not isinstance(result.get("result"), dict):
        raise RuntimeError("Telegram did not confirm the candidate preview. Outcome may be uncertain; do not retry automatically.")
    message_id = result["result"].get("message_id")
    if isinstance(message_id, bool) or not isinstance(message_id, int) or message_id <= 0:
        raise RuntimeError("Telegram response lacks a valid message_id; outcome may be uncertain.")
    return {"message_id": message_id, "preview_only": True, "production_ledger_touched": False,
            "rotation_history_touched": False, "tiktok_published": False}


def main() -> None:
    parser = argparse.ArgumentParser(description="Send one explicitly confirmed Pro candidate preview to a private Telegram chat.")
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--confirm-preview-send", action="store_true",
                        help="Explicitly authorize this one candidate-preview Telegram request.")
    args = parser.parse_args()
    result = send_preview(
        args.video, args.manifest,
        os.environ.get("PRO_PREVIEW_TG_BOT_TOKEN", ""),
        os.environ.get("PRO_PREVIEW_TELEGRAM_CHAT_ID", ""),
        confirmed=args.confirm_preview_send,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
