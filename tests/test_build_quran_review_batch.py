import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from build_quran_review_batch import build_review_batch, most_recent_delivered_surah

class BatchTests(unittest.TestCase):
    def test_never_reuses_previously_delivered_ayahs(self):
        verses = {}
        for surah in range(1, 7):
            for ayah in range(1, 7):
                key = f"{surah}:{ayah}"
                verses[key] = {"arabic_uthmani": f"AR {key}", "english_saheeh_international": f"EN {key}", "audio_archive_member": f"{key}.mp3"}
        source = {"status": "complete_join_candidate_requires_human_review_and_recording_approval", "rendering_allowed": False, "expected_verse_count": len(verses), "verses": verses}
        used = [f"{surah}:{ayah}" for surah in range(1, 7) for ayah in (1, 2)]
        result = build_review_batch(source, count=4, verses_per_passage=2, seed="history-test", excluded_surahs=[2], used_ayah_references=used)
        selected = [verse["reference"] for passage in result["passages"] for verse in passage["verses"]]
        self.assertTrue(set(selected).isdisjoint(used))

    def test_friday_mode_keeps_al_kahf_and_starts_at_first_unused_ayah(self):
        verses = {}
        for ayah in range(1, 7):
            key = f"18:{ayah}"
            verses[key] = {"arabic_uthmani": f"AR {key}", "english_saheeh_international": f"EN {key}", "audio_archive_member": f"{key}.mp3"}
        source = {
            "status": "complete_join_candidate_requires_human_review_and_recording_approval",
            "rendering_allowed": False,
            "expected_verse_count": len(verses),
            "verses": verses,
        }
        result = build_review_batch(
            source, count=1, seed="friday-1", used_ayah_references=["18:1", "18:2"],
            only_surahs=[18], sequential_unused=True,
        )
        self.assertEqual(result["candidate_count"], 1)
        self.assertEqual(result["passages"][0]["surah_number"], 18)
        self.assertEqual(result["passages"][0]["verse_numbers"], [3, 4, 5, 6])
        self.assertEqual(result["passage_selection"], "first_unused_contiguous_suffix_then_65_second_duration_limit")
        self.assertFalse(result["rendering_allowed"])
        self.assertFalse(result["telegram_delivery"])
        self.assertFalse(result["auto_publish"])
    def test_default_starts_at_first_unused_ayah(self):
        verses = {}
        for ayah in range(1, 7):
            key = f"18:{ayah}"
            verses[key] = {"arabic_uthmani": f"AR {key}", "english_saheeh_international": f"EN {key}", "audio_archive_member": f"{key}.mp3"}
        source = {
            "status": "complete_join_candidate_requires_human_review_and_recording_approval",
            "rendering_allowed": False,
            "expected_verse_count": len(verses),
            "verses": verses,
        }
        result = build_review_batch(
            source, count=1, seed="random-seed-must-not-skip-opening",
            used_ayah_references=["18:1", "18:2"], only_surahs=[18],
        )
        self.assertEqual(result["passages"][0]["verse_numbers"], [3, 4, 5, 6])
        self.assertEqual(
            result["passage_selection"],
            "first_unused_contiguous_suffix_then_65_second_duration_limit",
        )

    def test_excludes_most_recently_delivered_surah(self):
        history = {"deliveries": [
            {"candidate_id": "old", "surah_number": 18},
            {"candidate_id": "latest", "surah_number": 86},
        ]}
        self.assertEqual(most_recent_delivered_surah(history), 86)
        self.assertIsNone(most_recent_delivered_surah({"deliveries": []}))

    def test_rejects_invalid_latest_surah_in_history(self):
        with self.assertRaisesRegex(ValueError, "between 1 and 114"):
            most_recent_delivered_surah({"deliveries": [{"surah_number": 115}]})

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
        result = build_review_batch(source, count=4, verses_per_passage=2, seed="test", excluded_surahs=[2])
        self.assertEqual(result["distinct_surah_count"], 4)
        self.assertNotIn(2, [item["surah_number"] for item in result["passages"]])
        self.assertFalse(result["rendering_allowed"])
        self.assertFalse(result["auto_publish"])
        self.assertFalse(result["telegram_delivery"])
        for passage in result["passages"]:
            nums = passage["verse_numbers"]
            self.assertEqual(nums, list(range(nums[0], nums[0] + 2)))

if __name__ == "__main__":
    unittest.main()
