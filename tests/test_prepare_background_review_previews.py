"""Tests for the staged background preview workflow."""
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from src.prepare_background_review_previews import build_contact_sheet, composite_overlay_preview, prepare


class BackgroundReviewPreviewTests(unittest.TestCase):
    def test_contact_sheet_is_vertical_and_contains_four_tiles(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            items = []
            for index in range(4):
                path = root / f"{index}.jpg"
                Image.new("RGB", (540, 960), (index * 40, 30, 60)).save(path)
                items.append({
                    "preview_path": str(path),
                    "description": f"Candidate {index}",
                    "width": 2160,
                    "height": 3840,
                    "duration_seconds": 5,
                })
            output = root / "sheet.jpg"
            build_contact_sheet(items, output)
            with Image.open(output) as image:
                self.assertEqual(image.size, (1080, 1920))

    def test_actual_quran_overlay_is_composited_over_candidate_crop(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            background = root / "background.jpg"
            overlay = root / "overlay.png"
            output = root / "composite.jpg"
            Image.new("RGB", (540, 960), (20, 80, 120)).save(background)
            layer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
            from PIL import ImageDraw
            ImageDraw.Draw(layer).rectangle((100, 100, 980, 1800), fill=(0, 0, 0, 160))
            layer.save(overlay)
            composite_overlay_preview(background, overlay, output)
            with Image.open(output) as result:
                self.assertEqual(result.size, (540, 960))
                self.assertNotEqual(result.getpixel((270, 480)), (20, 80, 120))


    def test_prepare_refuses_any_candidate_already_marked_approved(self):
        catalog = json.loads(Path("data/background_candidates.json").read_text(encoding="utf-8"))
        catalog["candidates"][0]["approved"] = True
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog_path = root / "catalog.json"
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "disabled, unverified"):
                prepare(catalog_path, root / "output")


if __name__ == "__main__":
    unittest.main()
