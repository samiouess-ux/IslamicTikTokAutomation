import unittest

from build_quran_translation_catalog import find_translation_metadata


class TranslationMetadataTests(unittest.TestCase):
    def test_accepts_saheeh_translation_with_version(self):
        item = {
            "key": "english_saheeh",
            "title": "English Translation - Saheeh International",
            "version": "1.0",
        }
        self.assertEqual(find_translation_metadata([item]), item)

    def test_rejects_missing_translation(self):
        with self.assertRaisesRegex(ValueError, "found 0"):
            find_translation_metadata([])

    def test_rejects_ambiguous_duplicate_entries(self):
        item = {
            "key": "english_saheeh",
            "title": "Sahih International",
            "version": "1",
        }
        with self.assertRaisesRegex(ValueError, "found 2"):
            find_translation_metadata([item, item])

    def test_rejects_unidentified_translation_title(self):
        item = {"key": "english_saheeh", "title": "English Translation", "version": "1"}
        with self.assertRaisesRegex(ValueError, "does not identify"):
            find_translation_metadata([item])

    def test_rejects_unversioned_translation(self):
        item = {"key": "english_saheeh", "title": "Saheeh International"}
        with self.assertRaisesRegex(ValueError, "version"):
            find_translation_metadata([item])


if __name__ == "__main__":
    unittest.main()
