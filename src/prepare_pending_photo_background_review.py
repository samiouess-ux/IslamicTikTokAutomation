"""Build a review-only contact sheet for pending Pexels photo backgrounds."""
from __future__ import annotations
import json
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

MAX_BYTES = 25 * 1024 * 1024
USER_AGENT = "IslamicTikTokAutomation/1.0 (photo-review-only)"

def download_image(url: str, destination: Path) -> int:
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Referer": "https://www.pexels.com/",
        "Accept": "image/jpeg,image/*;q=0.9,*/*;q=0.5",
    })
    total = 0
    with urllib.request.urlopen(request, timeout=45) as response, destination.open("wb") as target:
        content_type = response.headers.get("Content-Type", "").lower()
        if "image/" not in content_type:
            raise RuntimeError(f"Unexpected image content type: {content_type}")
        while True:
            chunk = response.read(256 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_BYTES:
                raise RuntimeError("Image exceeds 25 MiB intake limit.")
            target.write(chunk)
    if total < 10_000:
        raise RuntimeError("Downloaded image is empty or unexpectedly small.")
    with Image.open(destination) as image:
        image.verify()
    return total

def make_preview(source: Path, destination: Path, overlay_path: Path) -> tuple[int, int]:
    with Image.open(source) as image:
        width, height = image.size
        if width < 720 or height < 720:
            raise RuntimeError(f"Source dimensions too small: {width}x{height}")
        base = ImageOps.fit(image.convert("RGB"), (540, 960), method=Image.Resampling.LANCZOS)
    with Image.open(overlay_path) as overlay:
        layer = ImageOps.fit(overlay.convert("RGBA"), (540, 960), method=Image.Resampling.LANCZOS)
    if layer.getbbox() is None:
        raise RuntimeError("Quran overlay is empty.")
    base = base.convert("RGBA")
    base.alpha_composite(layer)
    destination.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(destination, "JPEG", quality=84, optimize=True)
    return width, height

def main():
    manifest = json.loads(Path("data/background_photos_pending_review.json").read_text(encoding="utf-8"))
    out = Path("output/pending_photo_background_review")
    out.mkdir(parents=True, exist_ok=True)
    overlay = Path("output/pending_photo_background_review/quran_overlay.png")
    if not overlay.is_file():
        raise FileNotFoundError("Actual Quran overlay frame is missing.")
    items, failures = [], []
    for candidate in manifest["candidates"]:
        raw = out / f'{candidate["id"]}_source.jpg'
        preview = out / f'{candidate["id"]}_quran_overlay.jpg'
        try:
            byte_count = download_image(candidate["image_url"], raw)
            width, height = make_preview(raw, preview, overlay)
            raw.unlink(missing_ok=True)
            items.append({
                "id": candidate["id"],
                "description": candidate["description"],
                "source_page_url": candidate["source_page_url"],
                "source_dimensions": f"{width}x{height}",
                "download_bytes": byte_count,
                "preview_file": preview.name,
                "approval_status": "pending_visual_review",
                "user_approved": False,
                "production_enabled": False,
            })
        except Exception as exc:
            raw.unlink(missing_ok=True)
            preview.unlink(missing_ok=True)
            failures.append({"id": candidate["id"], "error": str(exc)})
    if not items:
        raise RuntimeError(f"No pending photos could be prepared: {failures}")
    cols, cell_w, cell_h, label_h = 3, 540, 960, 52
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell_w, rows * (cell_h + label_h)), (10, 16, 22))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for i, item in enumerate(items):
        x, y = (i % cols) * cell_w, (i // cols) * (cell_h + label_h)
        with Image.open(out / item["preview_file"]) as img:
            sheet.paste(img.convert("RGB"), (x, y))
        draw.rectangle((x, y + cell_h, x + cell_w, y + cell_h + label_h), fill=(10, 16, 22))
        draw.text((x + 10, y + cell_h + 8), item["id"], font=font, fill=(255,255,255))
        draw.text((x + 10, y + cell_h + 28), "PENDING — NOT APPROVED FOR PRODUCTION", font=font, fill=(238,211,153))
    sheet.save(out / "pending_photos_quran_overlay_contact_sheet.jpg", quality=88, optimize=True)
    report = {
        "status": "review_only_pending_user_approval",
        "candidate_count": len(manifest["candidates"]),
        "prepared_count": len(items),
        "failed_count": len(failures),
        "items": items,
        "failures": failures,
        "production_enabled": False,
        "user_approval_required": True,
        "note": "These preview images are temporary workflow artifacts. No source image is committed to the repository or enabled in production.",
    }
    (out / "pending_photo_review_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"prepared": len(items), "failed": len(failures), "production_enabled": False}, indent=2))

if __name__ == "__main__":
    main()
