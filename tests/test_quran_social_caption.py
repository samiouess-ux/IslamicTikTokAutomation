import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from quran_social_caption import AR_HASHTAGS, EN_HASHTAGS, build_social_caption, detect_theme
from quran_social_history import EMPTY, record_post


class QuranSocialCaptionTests(unittest.TestCase):
    def manifest(self, english):
        return {
            "source": {"surah_name_ar": "الشرح", "surah_name_en": "Ash-Sharh", "verses": [5, 6]},
            "verses": [{"english": english}],
        }

    def test_exactly_five_hashtags_and_thematic_caption(self):
        result = build_social_caption(self.manifest("For indeed, with hardship will be ease."), "video-a")
        tags = result["hashtags_ar"] + result["hashtags_en"]
        self.assertEqual(len(tags), 5)
        self.assertEqual(len(set(tags)), 5)
        self.assertEqual(result["theme"], "patience")
        self.assertIn("الصبر والثبات", result["arabic_caption"])
        self.assertIn("Verses 5-6", result["english_caption"])

    def test_rotation_changes_sets_between_video_ids(self):
        first = build_social_caption(self.manifest("Allah is One, the Eternal Refuge."), "video-a")
        second = build_social_caption(self.manifest("Allah is One, the Eternal Refuge."), "video-b")
        first_tags = first["hashtags_ar"] + first["hashtags_en"]
        second_tags = second["hashtags_ar"] + second["hashtags_en"]
        self.assertEqual(len(first_tags), 5)
        self.assertEqual(len(second_tags), 5)
        self.assertNotEqual(first_tags, second_tags)

    def test_unknown_topic_uses_honest_general_description(self):
        result = build_social_caption(self.manifest("A verse with uncommon wording."), "video-c")
        self.assertEqual(result["theme"], "general")
        self.assertIn("تدعونا الآيات", result["arabic_caption"])


    def test_large_bilingual_pools_still_emit_exactly_five_tags_and_varied_copy(self):
        self.assertGreaterEqual(len(AR_HASHTAGS), 15)
        self.assertGreaterEqual(len(EN_HASHTAGS), 15)
        first = build_social_caption(self.manifest("For indeed, with hardship will be ease."), "video-first")
        second = build_social_caption(self.manifest("For indeed, with hardship will be ease."), "video-second")
        for result in (first, second):
            tags = result["hashtags_ar"] + result["hashtags_en"]
            self.assertEqual(len(tags), 5)
            self.assertEqual(len(result["hashtags_ar"]), 3)
            self.assertEqual(len(result["hashtags_en"]), 2)
            self.assertIn("hook_id", result)
            self.assertIn("cta_id", result)
        self.assertTrue(
            first["hook_id"] != second["hook_id"] or first["cta_id"] != second["cta_id"]
            or first["hashtags_ar"] != second["hashtags_ar"] or first["hashtags_en"] != second["hashtags_en"]
        )

    def test_confirmed_social_history_balances_tag_hook_and_cta_reuse(self):
        history = {"schema_version": 1, "posts": []}
        first = build_social_caption(self.manifest("A verse with uncommon wording."), "video-one", history)
        record_post(history, "video-one", first)
        second = build_social_caption(self.manifest("A verse with uncommon wording."), "video-two", history)
        self.assertNotEqual(first["hook_id"], second["hook_id"])
        self.assertNotEqual(first["cta_id"], second["cta_id"])
        self.assertFalse(set(first["hashtags_ar"][:2]).intersection(second["hashtags_ar"][:2]))
        self.assertFalse(set(first["hashtags_en"][:1]).intersection(second["hashtags_en"][:1]))

    def test_social_history_record_is_idempotent_for_same_confirmed_candidate(self):
        history = {"schema_version": 1, "posts": []}
        caption = build_social_caption(self.manifest("A verse with uncommon wording."), "video-id", history)
        record_post(history, "candidate-id", caption)
        record_post(history, "candidate-id", caption)
        self.assertEqual(len(history["posts"]), 1)

    def test_arabic_and_english_hashtags_are_classified_correctly(self):
        result = build_social_caption(self.manifest("A verse with uncommon wording."), "video-c")
        self.assertIn("#القرآن_الكريم", result["hashtags_ar"])
        self.assertTrue(all(any(0x0600 <= ord(ch) <= 0x06FF for ch in tag)
                            for tag in result["hashtags_ar"]))
        self.assertTrue(all(not any(0x0600 <= ord(ch) <= 0x06FF for ch in tag)
                            for tag in result["hashtags_en"]))

if __name__ == "__main__":
    unittest.main()
