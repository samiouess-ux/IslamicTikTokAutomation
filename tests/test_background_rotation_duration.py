"""Regression tests for background duration metadata handling."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from background_rotation import select_background_sequence


class BackgroundDurationSelectionTests(unittest.TestCase):
    def _catalog(self, candidates):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "catalog.json"
        path.write_text(json.dumps({"candidates": candidates}), encoding="utf-8")
        return path

    def _candidate(self, item_id, duration):
        return {
            "id": item_id,
            "approved": True,
            "user_approved": True,
            "download_verified": True,
            "direct_video_url": f"https://cdn.example/{item_id}.mp4",
            "source_page_url": f"https://example.com/{item_id}",
            "duration_seconds": duration,
        }

    def test_unknown_catalog_duration_does_not_abort_sequence(self):
        catalog = self._catalog([
            self._candidate("unknown-a", None),
            self._candidate("known", 8),
            self._candidate("unknown-b", None),
        ])

        selected = select_background_sequence(catalog, "duration-test", 8)

        self.assertEqual(sum(item["duration_seconds"] for item in selected), 8)
        self.assertIn("known", [item["id"] for item in selected])

    def test_non_finite_required_duration_is_rejected(self):
        catalog = self._catalog([self._candidate("known", 8)])

        with self.assertRaisesRegex(ValueError, "finite and positive"):
            select_background_sequence(catalog, "duration-test", float("nan"))

    def test_unknown_durations_report_insufficient_verified_total(self):
        catalog = self._catalog([self._candidate("unknown", None)])

        with self.assertRaisesRegex(ValueError, "provide 0.00s"):
            select_background_sequence(catalog, "duration-test", 8)


if __name__ == "__main__":
    unittest.main()
