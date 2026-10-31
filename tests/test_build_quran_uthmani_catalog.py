import unittest

from build_quran_uthmani_catalog import validate_surah_payload


class UthmaniCatalogTests(unittest.TestCase):
    def test_accepts_complete_surah_and_preserves_exact_unicode(self):
        text = "بِسْمِ ٱللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
        payload = {"code": 200, "data": {"ayahs": [
            {"numberInSurah": 1, "text": text},
            {"numberInSurah": 2, "text": "الْحَمْدُ لِلَّهِ"},
        ]}}
        self.assertEqual(validate_surah_payload(payload, 1, 2), {"1:1": text, "1:2": "الْحَمْدُ لِلَّهِ"})

    def test_rejects_missing_ayah(self):
        with self.assertRaisesRegex(ValueError, "incomplete Uthmani text"):
            validate_surah_payload({"code": 200, "data": {"ayahs": [{"numberInSurah": 1, "text": "نص"}]}}, 1, 2)

    def test_rejects_duplicate_ayah(self):
        payload = {"code": 200, "data": {"ayahs": [
            {"numberInSurah": 1, "text": "نص"},
            {"numberInSurah": 1, "text": "نص مكرر"},
        ]}}
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_surah_payload(payload, 1, 1)

    def test_rejects_empty_arabic(self):
        with self.assertRaisesRegex(ValueError, "empty Arabic text"):
            validate_surah_payload({"code": 200, "data": {"ayahs": [{"numberInSurah": 1, "text": "  " }]}}, 1, 1)

    def test_rejects_invalid_status(self):
        with self.assertRaisesRegex(ValueError, "HTTP 200"):
            validate_surah_payload({"code": 503}, 1, 1)


if __name__ == "__main__":
    unittest.main()
