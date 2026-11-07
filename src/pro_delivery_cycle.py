"""Fail-closed two-phase Pro delivery cycle; no automatic retry."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Callable

from persist_pro_ledger import LEDGER_RELATIVE_PATH, persist_ledger
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
    repo_path = repo_path.resolve()
    supplied_ledger = Path(ledger_path)
    if not supplied_ledger.is_absolute():
        supplied_ledger = repo_path / supplied_ledger
    expected_ledger = repo_path / LEDGER_RELATIVE_PATH

    # Check symlinks before resolve(), because resolve() would erase evidence
    # that the caller supplied a link to an external ledger target.
    if (expected_ledger.parent.is_symlink() or expected_ledger.is_symlink()
            or supplied_ledger.parent.is_symlink() or supplied_ledger.is_symlink()):
        raise ValueError("Pro delivery ledger path must not use symlinks.")

    ledger_path = supplied_ledger.resolve()
    expected_ledger_resolved = expected_ledger.resolve()
    if ledger_path != expected_ledger_resolved:
        raise ValueError(
            f"Ledger path must match the persisted Pro branch file: {expected_ledger_resolved}"
        )

    caption_data = json.loads(caption_path.read_text(encoding="utf-8"))
    if not isinstance(caption_data, dict):
        raise ValueError("Caption JSON must contain an object.")
    manifest_id = caption_data.get("manifest_id")
    content_type = caption_data.get("content_type")
    if not isinstance(manifest_id, str) or not manifest_id.strip():
        raise ValueError("Caption must include a stable manifest_id.")
    if not isinstance(content_type, str) or content_type not in {"dua", "dhikr"}:
        raise ValueError("Pro delivery cycle accepts dua/dhikr only.")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("A non-empty workflow run_id is required.")

    # Phase 1: reserve locally, then commit/push before any Telegram request.
    reserve_fn(ledger_path, manifest_id, content_type, run_id)
    if persist_fn(repo_path) is not True:
        raise RuntimeError(
            "Reservation ledger was not committed and pushed; refusing Telegram request."
        )

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
            if persist_fn(repo_path) is not True:
                raise RuntimeError("Outcome ledger was not committed and pushed.")
        except Exception as persistence_error:
            # Git transport diagnostics may contain credential-bearing remote URLs.
            raise RuntimeError(
                "Telegram outcome is not confirmed and outcome-ledger persistence failed "
                f"({type(persistence_error).__name__}); the previously persisted reservation "
                "remains blocking. Human reconciliation required."
            ) from None
        # Do not surface arbitrary sender exception messages or chained transport details.
        raise RuntimeError(
            f"Telegram send outcome is not confirmed ({type(send_error).__name__}); "
            "the ledger was marked uncertain. Do not retry automatically."
        ) from None

    # Telegram has confirmed acceptance. If receipt finalization cannot be
    # persisted, never expose raw Git/filesystem diagnostics or invite a resend.
    try:
        if persist_fn(repo_path) is not True:
            raise RuntimeError("Delivery outcome persistence was not confirmed.")
    except Exception:
        raise RuntimeError(
            "Telegram accepted the Pro review video, but the delivered receipt "
            "could not be fully persisted. The earlier reservation remains blocking; "
            "do not resend until the ledger is reconciled."
        ) from None
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
