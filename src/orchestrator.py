"""Safe daily orchestrator for the three review-only video categories.

Default mode is a read-only preflight. Rendering requires --render.
No Telegram delivery, scheduling, or TikTok publishing is performed here.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

from content_rotation import choose_manifest
from validate_content_manifest import validate_content_manifest

KINDS = ("quran", "dua", "dhikr")


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
    value = read_json(path)
    if not isinstance(value.get("content", []), list):
        raise SystemExit("History field 'content' must be a list.")
    return value


def build_plan(content_dir: Path, history: dict, day_key: str) -> list[dict]:
    recent = list(history.get("content", []))
    plan = []
    for index, kind in enumerate(KINDS):
        manifest_path = choose_manifest(
            content_dir, kind, recent, f"{day_key}:{index}:{kind}"
        )
        manifest = read_json(manifest_path)
        validate_content_manifest(manifest)
        if manifest.get("content_type", "quran") != kind:
            raise SystemExit(f"Manifest type mismatch: {manifest_path}")
        if manifest.get("publishing", {}).get("auto_publish", False):
            raise SystemExit(f"Auto-publish must remain disabled: {manifest_path}")
        plan.append({
            "content_type": kind,
            "manifest": str(manifest_path),
            "content_id": manifest["id"],
        })
        recent.append(manifest["id"])
    return plan


def render_plan(plan: list[dict], output_dir: Path) -> list[dict]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered = []
    for item in plan:
        output = output_dir / f"{item['content_type']}-{item['content_id']}.mp4"
        renderer = "src/render_video_scenes.py" if item["content_type"] == "quran" else "src/render_dua_video.py"
        subprocess.run(
            [sys.executable, renderer, "--manifest", item["manifest"], "--output", str(output)],
            check=True,
        )
        if not output.is_file() or output.stat().st_size == 0:
            raise SystemExit(f"Renderer did not produce a valid MP4: {output}")
        rendered.append({**item, "output": str(output)})
    return rendered


def save_history(path: Path, history: dict, completed: list[dict]) -> None:
    updated = dict(history)
    updated["content"] = [*history.get("content", []), *[x["content_id"] for x in completed]]
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Coordinate a safe Quran/dua/dhikr review batch.")
    parser.add_argument("--content-dir", type=Path, default=Path("content"))
    parser.add_argument("--history", type=Path, default=Path("content/rotation_history.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("output/daily"))
    parser.add_argument("--day", default=date.today().isoformat())
    parser.add_argument("--render", action="store_true", help="Render after the complete batch passes preflight.")
    args = parser.parse_args()

    history = load_history(args.history)
    try:
        plan = build_plan(args.content_dir, history, args.day)
    except (FileNotFoundError, ValueError, LookupError, SystemExit) as exc:
        print(json.dumps({
            "status": "blocked",
            "stage": "preflight",
            "reason": str(exc),
            "required_types": list(KINDS),
            "rendered": [],
            "telegram_sent": False,
            "tiktok_published": False,
        }, ensure_ascii=False, indent=2))
        return 2

    print(json.dumps({"status": "ready_to_render" if args.render else "preflight_passed",
                      "day": args.day, "videos": plan,
                      "telegram_sent": False, "tiktok_published": False},
                     ensure_ascii=False, indent=2))
    if not args.render:
        print("Preflight only. Re-run with --render to create review MP4 files.")
        return 0

    rendered = render_plan(plan, args.output_dir)
    save_history(args.history, history, rendered)
    print(json.dumps({"status": "rendered_for_manual_review", "videos": rendered,
                      "telegram_sent": False, "tiktok_published": False},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
