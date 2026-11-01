"""Tests for the staged background preview workflow."""
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from src.prepare_background_review_previews import build_contact_sheet, prepare


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
