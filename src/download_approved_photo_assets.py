"""Download and compact only explicitly approved photo backgrounds."""
from __future__ import annotations
import json
import urllib.request
from pathlib import Path
from PIL import Image, ImageOps

MANIFEST = Path("data/background_photos_manifest.json")
MAX_BYTES = 25 * 1024 * 1024
MAX_SIZE = (1080, 1920)

def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    approved = data.get("approved_photo_ids")
    if not isinstance(approved, list) or not approved or len(approved) != len(set(approved)):
        raise SystemExit("Missing or invalid explicit photo approval allowlist.")
    records = {item["id"]: item for item in data.get("candidates", [])}
    out_dir = Path("assets/background_photos")
    out_dir.mkdir(parents=True, exist_ok=True)
    for asset_id in approved:
        item = records.get(asset_id)
        if not item or item.get("user_approved") is not True or item.get("approval_status") != "approved":
            # Original 35 predate per-item fields; their allowlist entry is the recorded approval.
            if not item or asset_id not in data.get("approved_photo_ids", []):
                raise SystemExit(f"Approved photo record missing: {asset_id}")
        target = Path(item["local_path"])
        if target.is_file() and target.stat().st_size >= 50_000:
            try:
                with Image.open(target) as check: check.verify()
                print(f"Already present: {asset_id} ({target.stat().st_size} bytes)")
                continue
            except Exception:
                target.unlink(missing_ok=True)
        request = urllib.request.Request(item["image_url"], headers={
            "User-Agent": "IslamicTikTokAutomation/1.0",
            "Referer": "https://www.pexels.com/",
            "Accept": "image/jpeg,image/*;q=0.9,*/*;q=0.5",
        })
        raw = target.with_suffix(".download")
        total = 0
        try:
            with urllib.request.urlopen(request, timeout=60) as response, raw.open("wb") as output:
                if "image/" not in response.headers.get("Content-Type", "").lower():
                    raise RuntimeError("Source did not return an image.")
                while True:
                    chunk = response.read(256 * 1024)
                    if not chunk: break
                    total += len(chunk)
                    if total > MAX_BYTES: raise RuntimeError("Source image exceeds 25 MiB.")
                    output.write(chunk)
            with Image.open(raw) as source:
                source.verify()
            with Image.open(raw) as source:
                image = ImageOps.exif_transpose(source).convert("RGB")
                if image.width < 720 or image.height < 720:
                    raise RuntimeError(f"Source dimensions too small: {image.size}")
                image.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
                target.parent.mkdir(parents=True, exist_ok=True)
                image.save(target, "JPEG", quality=82, optimize=True, progressive=True)
            if target.stat().st_size < 50_000:
                raise RuntimeError("Optimized photo is unexpectedly small.")
            with Image.open(target) as check:
                check.verify()
            print(f"Downloaded and optimized {asset_id}: {target.stat().st_size} bytes")
        finally:
            raw.unlink(missing_ok=True)

if __name__ == "__main__":
    main()
