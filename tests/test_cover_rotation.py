"""Tests for the isolated persistent cover selector."""
import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cover_rotation import choose_cover


class CoverRotationTests(unittest.TestCase):
    def _setup(self, root: Path, cover_ids=("original", "variant-a", "variant-b")):
        assets = root / "assets"
        assets.mkdir()
        covers = []
        for cover_id in cover_ids:
            asset = assets / f"{cover_id}.png"
            asset.write_bytes(b"test-image")
            covers.append({"id": cover_id, "asset_path": str(asset), "approved": True})
        catalog = root / "covers.json"
        catalog.write_text(json.dumps({"covers": covers}), encoding="utf-8")
        return catalog, root / "state.json"

    def test_never_repeats_consecutively(self):
        with tempfile.TemporaryDirectory() as tmp:
            catalog, state = self._setup(Path(tmp))
            a = choose_cover(catalog, state, "video-1")
            b = choose_cover(catalog, state, "video-2")
            c = choose_cover(catalog, state, "video-3")
            self.assertEqual([a["id"], b["id"], c["id"]],
                             ["original", "variant-a", "variant-b"])
            self.assertEqual(len({a["id"], b["id"], c["id"]}), 3)
            d = choose_cover(catalog, state, "video-4")
            self.assertEqual(d["id"], "original")
            self.assertNotEqual(c["id"], d["id"])

    def test_same_video_retry_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            catalog, state = self._setup(Path(tmp))
            first = choose_cover(catalog, state, "video-1")
            retry = choose_cover(catalog, state, "video-1")
            self.assertEqual(first["id"], retry["id"])

    def test_delayed_retry_keeps_original_cover_after_later_videos(self):
        with tempfile.TemporaryDirectory() as tmp:
            catalog, state = self._setup(Path(tmp))
            first = choose_cover(catalog, state, "video-1")
            choose_cover(catalog, state, "video-2")
            choose_cover(catalog, state, "video-3")
            delayed_retry = choose_cover(catalog, state, "video-1")
            self.assertEqual(first["id"], delayed_retry["id"])

    def test_state_survives_a_new_process_instance(self):
        with tempfile.TemporaryDirectory() as tmp:
            catalog, state = self._setup(Path(tmp))
            first = choose_cover(catalog, state, "video-1")
            second = choose_cover(catalog, state, "video-2")
            persisted = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(persisted["last_cover_id"], second["id"])
            self.assertNotEqual(first["id"], second["id"])

    def test_only_original_available_remains_operational(self):
        with tempfile.TemporaryDirectory() as tmp:
            catalog, state = self._setup(Path(tmp), ("original",))
            first = choose_cover(catalog, state, "video-1")
            second = choose_cover(catalog, state, "video-2")
            self.assertEqual(first["id"], "original")
            self.assertEqual(second["id"], "original")

    def test_unapproved_variant_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            catalog, state = self._setup(Path(tmp))
            data = json.loads(catalog.read_text(encoding="utf-8"))
            data["covers"][1]["approved"] = False
            catalog.write_text(json.dumps(data), encoding="utf-8")
            first = choose_cover(catalog, state, "video-1")
            second = choose_cover(catalog, state, "video-2")
            self.assertEqual(first["id"], "original")
            self.assertEqual(second["id"], "variant-b")

    def test_missing_original_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            catalog, state = self._setup(Path(tmp))
            data = json.loads(catalog.read_text(encoding="utf-8"))
            data["covers"][0]["approved"] = False
            catalog.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(LookupError, "original approved cover is missing"):
                choose_cover(catalog, state, "video-1")


if __name__ == "__main__":
    unittest.main()
