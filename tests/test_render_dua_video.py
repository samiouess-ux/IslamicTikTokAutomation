"""Regression checks for the separate dua/dhikr renderer."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import render_dua_video


class DuaRendererTests(unittest.TestCase):
    def test_module_imports(self):
        self.assertTrue(callable(render_dua_video.create_overlay))

    def test_renderer_is_separate_from_quran(self):
        # The public entry point enforces content type before rendering.
        source = (ROOT / "src" / "render_dua_video.py").read_text(encoding="utf-8")
        self.assertIn('not in {"dua", "dhikr"}', source)
        self.assertIn("validate_content_manifest(data)", source)


if __name__ == "__main__":
    unittest.main()
