import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from build_quran_review_batch import build_review_batch

class BatchTests(unittest.TestCase):
    def test_builds_distinct_surahs(self):
        verses = {}
        for surah in range(1, 7):
            for ayah in range(1, 5):
                key = f"{surah}:{ayah}"
                verses[key] = {
                    "arabic_uthmani": f"AR {key}",
                    "english_saheeh_international": f"EN {key}",
                    "audio_archive_member": f"{key}.mp3"
                }
        source = {
            "status": "complete_join_candidate_requires_human_review_and_recording_approval",
            "rendering_allowed": False,
            "expected_verse_count": len(verses),
            "verses": verses
        }
        result = build_review_batch(source, count=4, verses_per_passage=2, seed="test")
        self.assertEqual(result["distinct_surah_count"], 4)
        self.assertFalse(result["rendering_allowed"])
        self.assertFalse(result["auto_publish"])
        self.assertFalse(result["telegram_delivery"])
        for passage in result["passages"]:
            nums = passage["verse_numbers"]
            self.assertEqual(nums, list(range(nums[0], nums[0] + 2)))

if __name__ == "__main__":
    unittest.main()
