"""Source-level safety and Arabic-layout tests for the dedicated Pro renderer."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from render_dua_dhikr import create_item_overlay


class DuaDhikrRendererTests(unittest.TestCase):
    def item(self):
        return {
            "id": "review-only-test",
            "kind": "dhikr",
            "display_title": "أذكار",
            "arabic": "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ",
            "meaning_en": "Glory be to Allah and praise is His.",
            "repeat_count": 100,
        }

    def test_overlay_is_vertical_and_transparent_png(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "overlay.png"
            create_item_overlay(self.item(), output)
            from PIL import Image
            with Image.open(output) as image:
                self.assertEqual(image.size, (1080, 1920))
                self.assertEqual(image.mode, "RGBA")
                self.assertEqual(image.getbbox(), (72, 360, 1008, 1515))

    def test_empty_arabic_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(SystemExit, "exact Arabic"):
                create_item_overlay({"arabic": " "}, Path(directory) / "bad.png")

    def test_long_arabic_is_rejected_instead_of_clipped(self):
        item = self.item()
        item["arabic"] = " ".join(["كلمة"] * 300)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(SystemExit, "too long"):
                create_item_overlay(item, Path(directory) / "long.png")


if __name__ == "__main__":
    unittest.main()
