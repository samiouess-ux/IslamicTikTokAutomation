"""Fail-closed candidate-preview cycle; independent of production delivery state."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Callable

from persist_pro_preview_ledger import persist_preview_ledger
from pro_preview_send_ledger import load_ledger, reserve, transition, validate_candidate_id
from send_pro_preview_telegram import MAX_VIDEO_BYTES, build_preview_caption, send_preview, verify_private_chat, PreSendVerificationError
from validate_pro_media_rights import validate_manifest_media_rights

EXPECTED_BRANCH = "feature/quran-video-pro"
MANIFEST_ROOT = Path("content/pro")
PREVIEW_ROOT = Path("output/pro_preview")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inside_regular_file(path: Path, root: Path, repo_root: Path) -> Path:
    repo_root = repo_root.resolve(strict=True)
    root = root.absolute()
    if root.is_symlink():
        raise ValueError("Fixed Pro input directory must not be a symlink.")
    resolved_root = root.resolve(strict=True)
    if not resolved_root.is_relative_to(repo_root):
        raise ValueError("Fixed Pro input directory resolves outside the repository.")
    candidate = path.absolute()
    current = candidate
    while current != repo_root and current != current.parent:
        if current.is_symlink():
            raise ValueError("Symlink path components are not allowed.")
        current = current.parent
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file() or not resolved.is_relative_to(resolved_root):
        raise ValueError("Preview input must be a regular file beneath its fixed Pro directory.")
    return resolved

def preflight(manifest_path: Path, video_path: Path, *, repo_root: Path,
              token: str, chat_id: str) -> dict:
    repo_root = repo_root.resolve(strict=True)
    manifest = _inside_regular_file(repo_root / manifest_path, repo_root / MANIFEST_ROOT, repo_root)
    video = _inside_regular_file(repo_root / video_path, repo_root / PREVIEW_ROOT, repo_root)
    if not token.strip() or not chat_id.strip() or not chat_id.strip().isdigit() or int(chat_id) <= 0:
        raise ValueError("A bot token and positive numeric private-chat ID are required.")
    if video.suffix.lower() != ".mp4" or video.stat().st_size <= 0 or video.stat().st_size > MAX_VIDEO_BYTES:
        raise ValueError("Preview MP4 must be non-empty and no larger than 50 MiB.")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Preview manifest JSON must contain an object.")
    candidate_id = data.get("id")
    validate_candidate_id(candidate_id)
    content_type = data.get("content_type")
    expected_name = f"PREVIEW-ONLY-{content_type}-{candidate_id}.mp4"
    if not isinstance(content_type, str) or content_type not in {"dua", "dhikr"} or video.name != expected_name:
        raise ValueError("Preview MP4 filename must exactly match candidate ID and content type.")
    caption = build_preview_caption(data)
    validate_manifest_media_rights(data, repo_root=repo_root, planned_use="private_review",
                                   planned_territory=data.get("review_delivery_territory"))
    return {
        "manifest": manifest, "video": video, "data": data,
        "candidate_id": candidate_id, "content_type": content_type,
        "manifest_sha256": _sha256(manifest), "video_sha256": _sha256(video),
        "caption": caption,
    }


def run_preview_cycle(manifest_path: Path, video_path: Path, *, repo_root: Path,
                      workflow_run_id: str, token: str, chat_id: str,
                      branch: str, persist_fn: Callable[[Path], bool] = persist_preview_ledger,
                      send_fn: Callable[..., dict] = send_preview,
                      verify_chat_fn: Callable[..., None] = verify_private_chat) -> dict:
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(f"Preview delivery is restricted to {EXPECTED_BRANCH}.")
    if not isinstance(workflow_run_id, str) or not workflow_run_id.strip():
        raise ValueError("workflow_run_id is required.")
    root = repo_root.resolve(strict=True)
    checked = preflight(manifest_path, video_path, repo_root=root, token=token, chat_id=chat_id)
    # Verify before reserving; the sender repeats getChat immediately before sendVideo.
    verify_chat_fn(token, chat_id)
    data_dir = root / "data"
    if data_dir.is_symlink():
        raise ValueError("Pro data directory must not be a symlink.")
    data_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = data_dir / "pro_preview_send_ledger.json"
    if ledger_path.is_symlink():
        raise ValueError("Pro preview ledger must not be a symlink.")

    # Refuse if a previous reservation exists locally before writing another one.
    current = load_ledger(ledger_path)
    existing = current["entries"].get(checked["candidate_id"])
    if existing is not None:
        if (existing["manifest_sha256"], existing["video_sha256"]) != (
            checked["manifest_sha256"], checked["video_sha256"]
        ):
            raise ValueError("Candidate ID already exists with different hashes; identity conflict.")
        raise ValueError(f"Candidate already has preview ledger state '{existing['state']}'; refusing duplicate send.")

    reserve(ledger_path, checked["candidate_id"], checked["content_type"],
            checked["manifest_sha256"], checked["video_sha256"], workflow_run_id)
    if persist_fn(root) is not True:
        raise RuntimeError("Preview reservation was not confirmed persisted; Telegram send blocked.")
    remote_check = load_ledger(ledger_path)
    committed = remote_check["entries"].get(checked["candidate_id"])
    if (
        not committed
        or committed.get("candidate_id") != checked["candidate_id"]
        or committed.get("content_type") != checked["content_type"]
        or committed.get("workflow_run_id") != workflow_run_id
        or committed.get("state") != "reserved"
        or (committed.get("manifest_sha256"), committed.get("video_sha256"))
            != (checked["manifest_sha256"], checked["video_sha256"])
    ):
        raise RuntimeError(
            "Persisted preview reservation identity/state/hashes could not be verified; Telegram send blocked."
        )

    # Re-hash after the remote reservation is committed to close the local
    # preflight-to-send modification window. A mismatch leaves the reservation blocked.
    if _sha256(checked["manifest"]) != checked["manifest_sha256"] or _sha256(checked["video"]) != checked["video_sha256"]:
        raise RuntimeError("Preview manifest or MP4 changed after reservation; Telegram send blocked.")

    try:
        receipt = send_fn(checked["video"], checked["manifest"], token, chat_id, confirmed=True,
                          expected_video_sha256=checked["video_sha256"],
                          expected_manifest_sha256=checked["manifest_sha256"], repo_root=root)
        message_id = receipt.get("message_id") if isinstance(receipt, dict) else None
        if isinstance(message_id, bool) or not isinstance(message_id, int) or message_id <= 0:
            raise RuntimeError("Telegram response lacks a valid positive message_id; outcome is uncertain.")
    except (PreSendVerificationError, ValueError, FileNotFoundError, PermissionError):
        # These failures are definite local/pre-upload rejections; no sendVideo request was made.
        # Keep the reservation blocking duplicates, but do not mislabel it as an ambiguous upload.
        raise
    except Exception:
        # Once send_fn has been entered, an unexpected failure is conservatively
        # treated as an ambiguous remote outcome. Never expose arbitrary exception
        # text or its chain: transports may embed token-bearing request URLs.
        try:
            transition(ledger_path, checked["candidate_id"], "uncertain")
            if persist_fn(root) is not True:
                raise RuntimeError("uncertain preview state was not confirmed persisted")
        except Exception:
            raise RuntimeError(
                "Telegram preview outcome is uncertain and the ledger state could not be confirmed persisted; do not retry automatically."
            ) from None
        raise RuntimeError(
            "Telegram preview outcome is uncertain; the ledger was marked uncertain; do not retry automatically."
        ) from None

    # Telegram has confirmed delivery. Any local ledger/push failure from this point
    # must be reported as a post-send reconciliation issue, never as a send failure
    # that might encourage an unsafe retry.
    try:
        transition(ledger_path, checked["candidate_id"], "delivered", message_id)
        if persist_fn(root) is not True:
            raise RuntimeError("final ledger persistence was not confirmed")
    except Exception:
        raise RuntimeError(
            "Telegram accepted the preview, but the delivered receipt could not be fully persisted; "
            "the previously persisted reservation remains blocking. Do not resend; reconcile the ledger."
        ) from None
    return {"candidate_id": checked["candidate_id"], "state": "delivered",
            "telegram_message_id": message_id, "preview_only": True,
            "production_ledger_touched": False, "rotation_history_touched": False,
            "tiktok_published": False}
