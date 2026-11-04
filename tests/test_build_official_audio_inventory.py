"""Regression tests for resilient access to the official Quran audio ZIP."""
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from remotezip import RemoteIOError
from build_official_audio_inventory import (
    ARCHIVE_OPEN_ATTEMPTS,
    ENTRY_RE,
    create_archive_session,
    fetch_archive_names,
)


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

    @patch("build_official_audio_inventory.time.sleep")
    @patch("build_official_audio_inventory.create_archive_session")
    @patch("build_official_audio_inventory.RemoteZip")
    def test_archive_open_retries_after_remote_503_then_succeeds(
        self, remote_zip, create_session, sleep
    ):
        session = MagicMock()
        create_session.return_value = session
        successful_archive = MagicMock()
        successful_archive.__enter__.return_value.namelist.return_value = [
            "10-001001-A08.mp3"
        ]
        remote_zip.side_effect = [RemoteIOError("HTTP 503"), successful_archive]

        self.assertEqual(fetch_archive_names(), ["10-001001-A08.mp3"])
        self.assertEqual(remote_zip.call_count, 2)
        sleep.assert_called_once_with(15)
        self.assertEqual(session.close.call_count, 2)

    @patch("build_official_audio_inventory.time.sleep")
    @patch("build_official_audio_inventory.create_archive_session")
    @patch("build_official_audio_inventory.RemoteZip")
    def test_archive_open_fails_closed_after_all_outer_retries(
        self, remote_zip, create_session, sleep
    ):
        session = MagicMock()
        create_session.return_value = session
        remote_zip.side_effect = RemoteIOError("HTTP 503")

        with self.assertRaisesRegex(RuntimeError, "refusing to build an incomplete"):
            fetch_archive_names()

        self.assertEqual(remote_zip.call_count, ARCHIVE_OPEN_ATTEMPTS)
        self.assertEqual(sleep.call_count, ARCHIVE_OPEN_ATTEMPTS - 1)
        self.assertEqual(session.close.call_count, ARCHIVE_OPEN_ATTEMPTS)


if __name__ == "__main__":
    unittest.main()
