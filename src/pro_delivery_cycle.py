"""Fail-closed two-phase Pro delivery cycle; no automatic retry."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Callable

from persist_pro_ledger import persist_ledger
from pro_delivery_ledger import reserve
from send_pro_telegram import send_video


def run_delivery_cycle(
    *,
    repo_path: Path,
    ledger_path: Path,
    video_path: Path,
    caption_path: Path,
    token: str,
    chat_id: str,
    run_id: str,
    reserve_fn: Callable = reserve,
    persist_fn: Callable = persist_ledger,
    send_fn: Callable = send_video,
) -> dict:
    """Persist reservation before sending, then persist the sender outcome.

    If the first persistence fails, the sender is never called.
    If sending raises after making an ambiguous request, persist the sender's
    uncertain state before propagating the error. If that persistence fails,
    the already-pushed reserved state remains a duplicate-send block.
    """
    caption_data = json.loads(caption_path.read_text(encoding="utf-8"))
    manifest_id = caption_data.get("manifest_id")
    content_type = caption_data.get("content_type")
    if not isinstance(manifest_id, str) or not manifest_id.strip():
        raise ValueError("Caption must include a stable manifest_id.")
    if content_type not in {"dua", "dhikr"}:
        raise ValueError("Pro delivery cycle accepts dua/dhikr only.")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("A non-empty workflow run_id is required.")

    # Phase 1: reserve locally, then commit/push before any Telegram request.
    reserve_fn(ledger_path, manifest_id, content_type, run_id)
    persist_fn(repo_path)

    # Phase 2: sender requires the exact persisted reservation for this run.
    try:
        result = send_fn(
            video_path,
            caption_path,
            token,
            chat_id,
            run_id,
            ledger_path,
            reservation_persisted=True,
        )
    except Exception as send_error:
        try:
            # Sender records an ambiguous outcome as uncertain. Persist it.
            # If this push fails, the previously pushed reserved entry still blocks duplicates.
            persist_fn(repo_path)
        except Exception as persistence_error:
            raise RuntimeError(
                "Telegram outcome is not confirmed and outcome-ledger persistence failed; "
                "the previously persisted reservation remains blocking. Human reconciliation required."
            ) from persistence_error
        raise send_error

    # A failure here leaves the already-persisted reserved entry blocking duplicates.
    persist_fn(repo_path)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one Pro review-only delivery cycle.")
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--ledger", type=Path, default=Path("data/pro_delivery_ledger.json"))
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--caption", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    run_delivery_cycle(
        repo_path=args.repo,
        ledger_path=args.ledger,
        video_path=args.video,
        caption_path=args.caption,
        token=os.environ.get("TG_BOT_TOKEN", ""),
        chat_id=os.environ.get("TELEGRAM_CHAT_ID", ""),
        run_id=args.run_id,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
