"""Regression tests for resilient access to the official Quran audio ZIP."""
import sys
import unittest
from unittest.mock import Mock

import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from build_official_audio_inventory import ENTRY_RE, create_archive_session, preflight_archive


class OfficialAudioInventoryTests(unittest.TestCase):
    def test_archive_filename_mapping_pattern(self):
        match = ENTRY_RE.search("10-011001-A08.mp3")
        self.assertIsNotNone(match)
        self.assertEqual(match.groups(), ("011", "001"))

    def test_preflight_accepts_successful_head_request(self):
        session = Mock()
        response = Mock()
        response.status_code = 200
        session.head.return_value = response

        preflight_archive(session)

        session.head.assert_called_once_with(
            "https://download.qurancomplex.gov.sa/new-sounds/muaiqly-08/hafs/ayat-12-1-2020.zip",
            allow_redirects=True,
            timeout=(20, 30),
        )
        response.raise_for_status.assert_called_once()
        response.close.assert_called_once()
        session.get.assert_not_called()

    def test_preflight_falls_back_to_range_get_when_head_is_unsupported(self):
        session = Mock()
        head_response = Mock()
        head_response.status_code = 405
        range_response = Mock()
        range_response.status_code = 206
        session.head.return_value = head_response
        session.get.return_value = range_response

        preflight_archive(session)

        head_response.close.assert_called_once()
        session.get.assert_called_once_with(
            "https://download.qurancomplex.gov.sa/new-sounds/muaiqly-08/hafs/ayat-12-1-2020.zip",
            headers={"Range": "bytes=0-0"},
            stream=True,
            allow_redirects=True,
            timeout=(20, 30),
        )
        range_response.raise_for_status.assert_called_once()
        range_response.close.assert_called_once()

    def test_preflight_fails_closed_on_http_503(self):
        session = Mock()
        response = requests.Response()
        response.status_code = 503
        response.url = "https://download.qurancomplex.gov.sa/archive.zip"
        session.head.return_value = response

        with self.assertRaisesRegex(RuntimeError, "HTTP 503"):
            preflight_archive(session)

        session.get.assert_not_called()

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
