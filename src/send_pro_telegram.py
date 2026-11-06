"""Dua & Adhkar Pro Telegram review sender; no TikTok publishing."""
from __future__ import annotations

import argparse
import json
import os
import secrets
import urllib.request
from pathlib import Path

MAX_VIDEO_BYTES = 50 * 1024 * 1024
MAX_CAPTION_CHARS = 1024


def build_caption(data: dict) -> str:
    if data.get("content_type") not in {"dua", "dhikr"}:
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


def send_video(video_path: Path, caption_path: Path, token: str, chat_id: str) -> dict:
    if not token.strip() or not chat_id.strip():
        raise ValueError("TG_BOT_TOKEN and TELEGRAM_CHAT_ID must be configured as GitHub Secrets.")
    if not video_path.is_file() or video_path.stat().st_size == 0:
        raise FileNotFoundError(f"Review MP4 is missing or empty: {video_path}")
    size = video_path.stat().st_size
    if size > MAX_VIDEO_BYTES:
        raise ValueError("Review MP4 exceeds Telegram's 50 MB sendVideo limit.")
    data = json.loads(caption_path.read_text(encoding="utf-8"))
    caption = build_caption(data)

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
    # Do not automatically retry: a lost response can mean Telegram already accepted the video.
    with urllib.request.urlopen(request, timeout=180) as response:
        result = json.loads(response.read().decode("utf-8"))
    if not result.get("ok") or not isinstance(result.get("result"), dict):
        raise RuntimeError("Telegram API did not confirm Pro review delivery.")
    message = result["result"]
    if not isinstance(message.get("message_id"), int) or message["message_id"] <= 0:
        raise RuntimeError("Telegram response lacks a valid message_id; reconcile before retrying.")
    print(f"Telegram confirmed Dua & Adhkar Pro review delivery: message_id={message['message_id']}.")
    return message


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--caption", type=Path, required=True)
    args = parser.parse_args()
    send_video(args.video, args.caption, os.environ.get("TG_BOT_TOKEN", ""),
               os.environ.get("TELEGRAM_CHAT_ID", ""))


if __name__ == "__main__":
    main()
