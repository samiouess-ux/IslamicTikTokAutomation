import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageChops

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from render_cover_template_previews import TEMPLATES, render_all, render_cover


class OpeningCoverPreviewTests(unittest.TestCase):
    def test_four_requested_preview_designs_render_and_are_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = render_all("سُورَةُ الْفَاتِحَةِ", 1, 7, Path(directory))
            self.assertEqual(len(paths), 4)
            self.assertEqual(
                {p.stem for p in paths},
                {"blue_royal", "emerald_arch", "ivory_classic", "midnight_cinematic"},
            )
            images = [Image.open(p).convert("RGB") for p in paths]
            for image in images:
                self.assertEqual(image.size, (1080, 1920))
            for i in range(len(images)):
                for j in range(i + 1, len(images)):
                    self.assertIsNotNone(
                        ImageChops.difference(images[i], images[j]).getbbox()
                    )

    def test_requires_a_vocalized_title_and_valid_ayah_range(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "invalid.png"
            with self.assertRaisesRegex(ValueError, "title"):
                render_cover("", 1, 7, "blue_royal", target)
            with self.assertRaisesRegex(ValueError, "range"):
                render_cover("سُورَةُ الْفَاتِحَةِ", 7, 1, "blue_royal", target)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
