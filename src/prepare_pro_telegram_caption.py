"""Prepare a Pro-only Telegram caption from a validated manifest."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_content_manifest import validate_content_manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    validate_content_manifest(data)
    content_type = data.get("content_type")
    if content_type not in {"dua", "dhikr"}:
        raise SystemExit("Pro caption accepts dua/dhikr only.")
    if data.get("publishing", {}).get("auto_publish", False):
        raise SystemExit("TikTok auto-publishing is disabled.")
    manifest_id = data.get("id")
    if not isinstance(manifest_id, str) or not manifest_id.strip():
        raise SystemExit("Pro manifest must include a stable id for delivery-ledger protection.")
    items = data["items"]
    arabic = "\n".join(item["arabic"] for item in items)
    english = "\n".join(
        str(item["english"]).strip() for item in items
        if isinstance(item.get("english"), str) and item["english"].strip()
    )
    payload = {
        "manifest_id": manifest_id,
        "content_type": content_type,
        "review_only": True,
        "auto_publish": False,
        "title_ar": data.get("title_ar", "دعاء" if content_type == "dua" else "ذكر"),
        "arabic_caption": arabic,
        "english_caption": english,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")


if __name__ == "__main__":
    main()
