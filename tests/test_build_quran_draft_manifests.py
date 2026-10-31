import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from build_quran_draft_manifests import build_draft_manifests


def candidate(cid, surah):
    return {
        "candidate_id": cid,
        "surah_number": surah,
        "verses": [
            {"ayah": 4, "reference": f"{surah}:4", "arabic_uthmani": "نَصٌّ عَرَبِيٌّ", "english_saheeh_international": "Translation one"},
            {"ayah": 5, "reference": f"{surah}:5", "arabic_uthmani": "نَصٌّ ثَانٍ", "english_saheeh_international": "Translation two"},
        ],
    }


class DraftManifestTests(unittest.TestCase):
    def test_builds_distinct_review_only_manifests(self):
        batch = {"batch_status": "review_candidates_only", "passages": [candidate("a", 19), candidate("b", 88)]}
        report = {
            "rendering_allowed": False,
            "auto_publish": False,
            "items": [
                {"candidate_id": "a", "surah_number": 19, "status": "audio_prepared_requires_exact_recording_listen_and_user_review", "selected_verses": [4, 5], "audio_file": "a.mp3", "duration_seconds": 32.5},
                {"candidate_id": "b", "surah_number": 88, "status": "audio_prepared_requires_exact_recording_listen_and_user_review", "selected_verses": [4, 5], "audio_file": "b.mp3", "duration_seconds": 28.0},
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            result = build_draft_manifests(batch, report, Path(tmp))
            self.assertEqual(len(result), 2)
            for item in result:
                data = json.loads(Path(item["manifest"]).read_text(encoding="utf-8"))
                self.assertFalse(data["audio"]["approved"])
                self.assertFalse(data["audio"]["rights_verified"])
                self.assertFalse(data["rotation_approved"])
                self.assertFalse(data["publishing"]["auto_publish"])
                self.assertFalse(data["preflight"]["rendering_allowed"])
                self.assertEqual([v["number"] for v in data["verses"]], [4, 5])

    def test_rejects_missing_ayah_from_audio(self):
        batch = {"batch_status": "review_candidates_only", "passages": [candidate("a", 19), candidate("b", 88)]}
        report = {"rendering_allowed": False, "auto_publish": False, "items": [
            {"candidate_id": "a", "surah_number": 19, "status": "audio_prepared", "selected_verses": [4], "audio_file": "a.mp3", "duration_seconds": 12},
            {"candidate_id": "b", "surah_number": 88, "status": "audio_prepared", "selected_verses": [4, 5], "audio_file": "b.mp3", "duration_seconds": 12},
        ]}
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "every requested ayah"):
                build_draft_manifests(batch, report, Path(tmp))


if __name__ == "__main__":
    unittest.main()
