"""Regression tests for resilient access to the official Quran audio ZIP."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from build_official_audio_inventory import ENTRY_RE, create_archive_session


class OfficialAudioInventoryTests(unittest.TestCase):
    def test_archive_filename_mapping_pattern(self):
        match = ENTRY_RE.search("10-011001-A08.mp3")
        self.assertIsNotNone(match)
        self.assertEqual(match.groups(), ("011", "001"))

    def test_archive_session_retries_transient_http_failures(self):
        session = create_archive_session()
        try:
            adapter = session.get_adapter("https://")
            retry = adapter.max_retries
            self.assertEqual(retry.total, 4)
            self.assertEqual(retry.connect, 4)
            self.assertEqual(retry.read, 4)
            self.assertIn(503, retry.status_forcelist)
            self.assertIn("GET", retry.allowed_methods)
            self.assertIn("HEAD", retry.allowed_methods)
            self.assertIn("IslamicTikTokAutomation", session.headers["User-Agent"])
        finally:
            session.close()


if __name__ == "__main__":
    unittest.main()
