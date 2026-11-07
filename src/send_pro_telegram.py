"""Dua & Adhkar Pro Telegram review sender with delivery-ledger protection."""
from __future__ import annotations

import argparse
import json
import os
import secrets
import urllib.request
from pathlib import Path

from pro_delivery_ledger import assert_reserved_for_run, reserve, transition

MAX_VIDEO_BYTES = 50 * 1024 * 1024
MAX_CAPTION_CHARS = 1024


def build_caption(data: dict) -> str:
    if not isinstance(data, dict):
        raise ValueError("Caption JSON must contain an object.")
    if not isinstance(data.get("content_type"), str) or data.get("content_type") not in {"dua", "dhikr"}:
        raise ValueError("Pro Telegram sender accepts dua/dhikr only.")
    if data.get("review_only") is not True or data.get("auto_publish") is not False:
        raise ValueError("Telegram delivery requires review_only=true and auto_publish=false.")
    parts = [
        "🌿 DUA & ADHKAR PRO — معاينة للمراجعة",
        str(data.get("title_ar", "")).strip(),
        str(data.get("arabic_caption", "")).strip(),
        str(data.get("english_caption", "")).strip(),
        "للمراجعة فقط — لم يتم النشر على TikTok. النشر يدوي بعد مراجعتك.",
    ]
    caption = "\n\n".join(part for part in parts if part)
    if len(caption) > MAX_CAPTION_CHARS:
        raise ValueError(f"Telegram caption exceeds {MAX_CAPTION_CHARS} characters.")
    return caption


def send_video(video_path: Path, caption_path: Path, token: str, chat_id: str,
               run_id: str, ledger_path: Path = Path("data/pro_delivery_ledger.json"),
               reservation_persisted: bool = False) -> dict:
    if not token.strip() or not chat_id.strip():
        raise ValueError("TG_BOT_TOKEN and TELEGRAM_CHAT_ID must be configured as GitHub Secrets.")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("A non-empty workflow run_id is required.")
    if not video_path.is_file() or video_path.stat().st_size == 0:
        raise FileNotFoundError(f"Review MP4 is missing or empty: {video_path}")
    if video_path.stat().st_size > MAX_VIDEO_BYTES:
        raise ValueError("Review MP4 exceeds Telegram's 50 MB sendVideo limit.")

    data = json.loads(caption_path.read_text(encoding="utf-8"))
    caption = build_caption(data)
    manifest_id = data.get("manifest_id")
    content_type = data.get("content_type")
    if not isinstance(manifest_id, str) or not manifest_id.strip():
        raise ValueError("Caption data must include the stable manifest_id.")
    if not isinstance(content_type, str) or content_type not in {"dua", "dhikr"}:
        raise ValueError("Pro Telegram sender accepts dua/dhikr only.")

    # In cross-run mode, the reservation must already be committed to the Pro branch.
    # Local mode remains available for isolated offline tests.
    if reservation_persisted:
        assert_reserved_for_run(ledger_path, manifest_id, content_type, run_id)
    else:
        reserve(ledger_path, manifest_id, content_type, run_id)

    boundary = "----DuaAdhkarPro" + secrets.token_hex(16)
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

    # Never auto-retry: a lost response can mean Telegram already accepted the video.
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))
        if not isinstance(result, dict) or not result.get("ok") or not isinstance(result.get("result"), dict):
            raise RuntimeError("Telegram API did not confirm Pro review delivery.")
        message = result["result"]
        message_id = message.get("message_id")
        if isinstance(message_id, bool) or not isinstance(message_id, int) or message_id <= 0:
            raise RuntimeError("Telegram response lacks a valid message_id; reconcile before retrying.")
    except Exception as send_error:
        try:
            transition(ledger_path, manifest_id, "uncertain")
        except Exception:
            # Never chain transport exceptions: urllib errors can contain the bot-token URL.
            raise RuntimeError(
                "Telegram outcome is uncertain and the ledger could not be advanced; "
                "the existing reservation must remain blocking."
            ) from None
        # Preserve the exception class for diagnostics, but not its potentially secret-bearing message.
        raise RuntimeError(
            f"Telegram send outcome is uncertain ({type(send_error).__name__}); "
            "do not retry automatically."
        ) from None

    # If this write fails, the earlier reservation still blocks a duplicate send.
    transition(ledger_path, manifest_id, "delivered", message_id)
    print(f"Telegram confirmed Dua & Adhkar Pro review delivery: message_id={message_id}.")
    return message


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--caption", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--ledger", type=Path, default=Path("data/pro_delivery_ledger.json"))
    parser.add_argument("--reservation-persisted", action="store_true",
                        help="Require a previously persisted reservation; never create one here.")
    args = parser.parse_args()
    send_video(args.video, args.caption, os.environ.get("TG_BOT_TOKEN", ""),
               os.environ.get("TELEGRAM_CHAT_ID", ""), args.run_id, args.ledger,
               reservation_persisted=args.reservation_persisted)


if __name__ == "__main__":
    main()
