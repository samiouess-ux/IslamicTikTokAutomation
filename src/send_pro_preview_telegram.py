"""Explicit, isolated Telegram sender for candidate-only Pro previews.

This module never touches the production delivery ledger or rotation history.
It requires a separate Pro preview bot/chat configuration and an explicit CLI
confirmation. A transport error is treated as an unknown outcome; it is never
retried automatically.
"""
from __future__ import annotations

import argparse
import json
import hashlib
import os
import secrets
import urllib.request
from pathlib import Path

from validate_content_manifest import validate_content_manifest
from validate_pro_media_rights import validate_manifest_media_rights

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


class PreSendVerificationError(RuntimeError):
    """A definite pre-upload verification failure; no sendVideo request was made."""


def _safe_pro_file(path: Path, repo_root: Path, allowed: Path) -> Path:
    root = repo_root.resolve(strict=True)
    allowed_root = root / allowed
    if allowed_root.is_symlink():
        raise ValueError("Fixed Pro artifact directory must not be a symlink.")
    resolved_root = allowed_root.resolve(strict=True)
    candidate = path if path.is_absolute() else root / path
    current = candidate
    while current != root and current != current.parent:
        if current.is_symlink():
            raise ValueError("Symlink path components are not allowed.")
        current = current.parent
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file() or not resolved.is_relative_to(resolved_root):
        raise ValueError("Sender accepts files only beneath fixed Pro artifact directories.")
    return resolved


def verify_private_chat(token: str, chat_id: str, *, urlopen_fn=None) -> None:
    """Fail closed unless Telegram confirms this exact destination is a private chat."""
    if urlopen_fn is None:
        urlopen_fn = urllib.request.urlopen
    if not token.strip() or not chat_id.strip().isdigit() or int(chat_id) <= 0:
        raise ValueError("A bot token and positive numeric destination are required.")
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token.strip()}/getChat?chat_id={chat_id.strip()}",
        headers={"Accept": "application/json"},
        method="GET",
    )
    try:
        with urlopen_fn(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        # Do not propagate urllib exceptions: they may contain the token-bearing URL.
        raise PreSendVerificationError("Telegram private-chat verification failed; preview upload blocked.") from None
    if not isinstance(payload, dict) or payload.get("ok") is not True:
        raise PreSendVerificationError("Telegram private-chat verification was not confirmed; preview upload blocked.")
    chat = payload.get("result")
    if not isinstance(chat, dict):
        raise PreSendVerificationError("Telegram private-chat verification returned malformed data; preview upload blocked.")
    actual_id = chat.get("id")
    if isinstance(actual_id, bool) or not isinstance(actual_id, int) or actual_id != int(chat_id):
        raise PreSendVerificationError("Telegram returned a different destination; preview upload blocked.")
    if chat.get("type") != "private":
        raise PreSendVerificationError("Telegram destination is not a private chat; preview upload blocked.")


def send_preview(video_path: Path, manifest_path: Path, token: str, chat_id: str,
                 *, confirmed: bool = False, expected_video_sha256: str | None = None,
                 expected_manifest_sha256: str | None = None,
                 repo_root: Path | None = None, urlopen_fn=None) -> dict:
    if not confirmed:
        raise PermissionError("Explicit --confirm-preview-send is required before any Telegram request.")
    if not token.strip() or not chat_id.strip():
        raise ValueError("Separate PRO_PREVIEW_TG_BOT_TOKEN and PRO_PREVIEW_TELEGRAM_CHAT_ID are required.")
    if not chat_id.strip().isdigit() or int(chat_id) <= 0:
        raise ValueError("Preview destination must be a positive numeric private-chat ID.")
    effective_root = repo_root or Path.cwd()
    manifest_path = _safe_pro_file(manifest_path, effective_root, Path("content/pro"))
    video_path = _safe_pro_file(video_path, effective_root, Path("output/pro_preview"))
    if video_path.stat().st_size == 0:
        raise FileNotFoundError("Preview MP4 is empty.")
    if not video_path.name.startswith("PREVIEW-ONLY-") or video_path.suffix.lower() != ".mp4":
        raise ValueError("Only PREVIEW-ONLY-*.mp4 files can be sent by this sender.")
    if video_path.stat().st_size > MAX_VIDEO_BYTES:
        raise ValueError("Preview MP4 exceeds Telegram's 50 MB sendVideo limit.")

    # Read each artifact once, then hash and use those exact bytes in the request.
    # This binds the ledger identity to the bytes actually uploaded, not a prior path check.
    video_bytes = video_path.read_bytes()
    manifest_bytes = manifest_path.read_bytes()
    if expected_video_sha256 is not None and hashlib.sha256(video_bytes).hexdigest() != expected_video_sha256:
        raise ValueError("Preview video bytes do not match the reserved SHA-256 identity.")
    if expected_manifest_sha256 is not None and hashlib.sha256(manifest_bytes).hexdigest() != expected_manifest_sha256:
        raise ValueError("Preview manifest bytes do not match the reserved SHA-256 identity.")
    data = json.loads(manifest_bytes.decode("utf-8"))
    caption = build_preview_caption(data)
    validate_manifest_media_rights(data, repo_root=repo_root or Path.cwd(), planned_use="private_review")
    manifest_id = data.get("id")
    expected_name = "PREVIEW-ONLY-{}-{}.mp4".format(data["content_type"], manifest_id)
    if not isinstance(manifest_id, str) or video_path.name != expected_name:
        raise ValueError("Preview filename must exactly match the selected candidate manifest id and content type.")
    verify_private_chat(token, chat_id, urlopen_fn=urlopen_fn)
    boundary = "----DuaAdhkarProPreview" + secrets.token_hex(16)
    body = b"".join([
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n{chat_id}\r\n".encode(),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"caption\"\r\n\r\n{caption}\r\n".encode("utf-8"),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"supports_streaming\"\r\n\r\ntrue\r\n".encode(),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"video\"; filename=\"{video_path.name}\"\r\nContent-Type: video/mp4\r\n\r\n".encode(),
        video_bytes,
        f"\r\n--{boundary}--\r\n".encode("ascii"),
    ])
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token.strip()}/sendVideo",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )

    # A timeout or lost response may follow successful delivery. Never retry here.
    with (urlopen_fn or urllib.request.urlopen)(request, timeout=180) as response:
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
