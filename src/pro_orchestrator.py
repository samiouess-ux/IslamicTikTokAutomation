"""Dua/adhkar-only Pro orchestrator; isolated from the Quran production path."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

from content_rotation import choose_manifests
from validate_content_manifest import validate_content_manifest
from render_dua_video import HARD_MAX_DURATION_SECONDS


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot read JSON file {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"Expected a JSON object in {path}.")
    return value


def load_history(path: Path) -> dict:
    if not path.exists():
        return {"content": []}
    history = read_json(path)
    if not isinstance(history.get("content", []), list):
        raise SystemExit("Pro history field 'content' must be a list.")
    return history


def build_plan(content_dir: Path, history: dict, content_type: str,
               day_key: str, video_count: int = 1) -> list[dict]:
    """Preflight a complete distinct batch; never invent or partially select items."""
    if content_type not in {"dua", "dhikr"}:
        raise ValueError("Pro content_type must be dua or dhikr.")
    recent = list(history.get("content", []))
    paths = choose_manifests(content_dir, content_type, video_count, recent, day_key)
    plan: list[dict] = []
    for manifest_path in paths:
        manifest = read_json(manifest_path)
        if manifest.get("content_type") != content_type:
            raise SystemExit(f"{manifest_path} must explicitly declare content_type={content_type}.")
        if manifest.get("rotation_approved") is not True:
            raise SystemExit(f"Manifest is not approved for rotation: {manifest_path}")
        validate_content_manifest(manifest)
        durations = [item.get("duration_seconds") for item in manifest["items"]]
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0 for value in durations):
            raise SystemExit(f"Every Pro item needs an explicit positive duration_seconds: {manifest_path}")
        total_duration = sum(float(value) for value in durations)
        if total_duration > HARD_MAX_DURATION_SECONDS:
            raise SystemExit(f"Pro manifest exceeds the {HARD_MAX_DURATION_SECONDS:.0f}-second hard limit: {manifest_path}")
        publishing = manifest["publishing"]
        if publishing.get("approval_required") is not True or publishing.get("auto_publish", False):
            raise SystemExit(f"Manual review must be required and auto-publish disabled: {manifest_path}")
        manifest_id = manifest.get("id")
        if not isinstance(manifest_id, str) or not manifest_id.strip():
            raise SystemExit(f"Manifest has no stable id: {manifest_path}")
        plan.append({
            "content_type": content_type,
            "manifest": str(manifest_path),
            "content_id": manifest_id,
            "item_ids": [item["id"] for item in manifest["items"]],
        })
        recent.append(manifest_id)
    return plan


def build_preview_plan(manifest_path: Path) -> dict:
    """Validate one explicitly selected candidate without rotation eligibility."""
    manifest = read_json(manifest_path)
    if manifest.get("content_type") not in {"dua", "dhikr"}:
        raise SystemExit("Preview candidate must be dua or dhikr.")
    if manifest.get("lifecycle_status") != "candidate_preview" or manifest.get("preview_only") is not True:
        raise SystemExit("Preview path requires lifecycle_status=candidate_preview and preview_only=true.")
    if manifest.get("rotation_approved") is True:
        raise SystemExit("A candidate preview must never be rotation-approved.")
    validate_content_manifest(manifest, allow_candidate_preview=True)
    durations = [item.get("duration_seconds") for item in manifest["items"]]
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0 for value in durations):
        raise SystemExit("Every preview item needs an explicit positive duration_seconds.")
    total = sum(float(value) for value in durations)
    if total > HARD_MAX_DURATION_SECONDS:
        raise SystemExit(f"Preview exceeds the {HARD_MAX_DURATION_SECONDS:.0f}-second hard limit.")
    manifest_id = manifest.get("id")
    if not isinstance(manifest_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", manifest_id):
        raise SystemExit("Preview candidate id must be a safe filename component (1-80 ASCII letters, digits, dot, underscore or hyphen).")
    return {"content_type": manifest["content_type"], "manifest": str(manifest_path),
            "content_id": manifest_id, "item_ids": [item["id"] for item in manifest["items"]],
            "lifecycle_status": "candidate_preview", "preview_only": True}


def render_preview(plan: dict, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"PREVIEW-ONLY-{plan['content_type']}-{plan['content_id']}.mp4"
    subprocess.run([sys.executable, "src/render_dua_video.py", "--preview-only",
                    "--manifest", plan["manifest"], "--output", str(output)], check=True)
    if not output.is_file() or output.stat().st_size == 0:
        raise SystemExit(f"Preview renderer did not produce a non-empty MP4: {output}")
    return {**plan, "output": str(output), "telegram_sent": False, "tiktok_published": False}


def render_plan(plan: list[dict], output_dir: Path) -> list[dict]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered = []
    for entry in plan:
        output = output_dir / f"{entry['content_type']}-{entry['content_id']}.mp4"
        subprocess.run([
            sys.executable, "src/render_dua_video.py",
            "--manifest", entry["manifest"], "--output", str(output)
        ], check=True)
        if not output.is_file() or output.stat().st_size == 0:
            raise SystemExit(f"Renderer did not produce a non-empty MP4: {output}")
        rendered.append({**entry, "output": str(output)})
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser(description="Dua & Adhkar Pro manual-review batch preflight.")
    parser.add_argument("--content-dir", type=Path, default=Path("content/pro"))
    parser.add_argument("--history", type=Path, default=Path("data/dua_dhikr_rotation_history.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("output/pro_review"))
    parser.add_argument("--content-type", choices=("dua", "dhikr"))
    parser.add_argument("--day", default=date.today().isoformat())
    parser.add_argument("--video-count", type=int, default=1)
    parser.add_argument("--render", action="store_true",
                        help="Render only after the complete Pro preflight passes.")
    parser.add_argument("--preview-manifest", type=Path,
                        help="Explicit candidate manifest for isolated preview-only validation.")
    parser.add_argument("--render-preview", action="store_true",
                        help="Render the selected candidate to the Pro preview folder only.")
    args = parser.parse_args()
    if args.preview_manifest:
        if args.render:
            parser.error("Candidate preview mode cannot be combined with production --render.")
        try:
            preview_plan = build_preview_plan(args.preview_manifest)
            if args.render_preview:
                result = render_preview(preview_plan, Path("output/pro_preview"))
                status = "candidate_preview_rendered_locally"
            else:
                result = preview_plan
                status = "candidate_preview_preflight_passed"
            print(json.dumps({"status": status, "preview_only": True, "videos": [result],
                              "telegram_sent": False, "tiktok_published": False},
                             ensure_ascii=False, indent=2))
            return 0
        except (FileNotFoundError, ValueError, LookupError, SystemExit) as exc:
            print(json.dumps({"status": "blocked", "stage": "candidate_preview",
                              "reason": str(exc), "videos": [], "telegram_sent": False,
                              "tiktok_published": False}, ensure_ascii=False, indent=2))
            return 2
    if args.render_preview:
        parser.error("--render-preview requires --preview-manifest.")
    if not args.content_type:
        parser.error("--content-type is required outside candidate preview mode.")
    try:
        history = load_history(args.history)
        plan = build_plan(args.content_dir, history, args.content_type, args.day, args.video_count)
    except (FileNotFoundError, ValueError, LookupError, SystemExit) as exc:
        print(json.dumps({
            "status": "blocked", "stage": "preflight", "reason": str(exc),
            "content_type": args.content_type, "videos": [],
            "telegram_sent": False, "tiktok_published": False,
        }, ensure_ascii=False, indent=2))
        return 2

    if not args.render:
        print(json.dumps({
            "status": "preflight_passed", "day": args.day,
            "content_type": args.content_type, "videos": plan,
            "rendered": False, "telegram_sent": False, "tiktok_published": False,
        }, ensure_ascii=False, indent=2))
        return 0

    rendered = render_plan(plan, args.output_dir)
    # Do not consume history on render; reserve it for confirmed review delivery.
    print(json.dumps({
        "status": "rendered_for_manual_review", "videos": rendered,
        "history_updated": False, "telegram_sent": False, "tiktok_published": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
