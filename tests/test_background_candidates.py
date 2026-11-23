"""Safety checks for staged and approved background candidates."""
import json
import re
import unittest
from pathlib import Path

from src.background_rotation import load_eligible_backgrounds


class BackgroundCandidateTests(unittest.TestCase):
    def test_all_candidates_have_matching_pexels_direct_mp4_sources(self):
        catalog = json.loads(Path("data/background_candidates.json").read_text(encoding="utf-8"))
        self.assertEqual(len(catalog["candidates"]), 17)
        original_ids = {
            "pexels-ocean-shore-35036280",
            "pexels-mountain-lake-37675265",
            "pexels-sunset-sky-35477402",
            "pexels-mountain-bridge-5903759",
        }
        original = [item for item in catalog["candidates"] if item["id"] in original_ids]
        additions = [item for item in catalog["candidates"] if item["id"] not in original_ids]
        self.assertEqual(len(original), 4)
        self.assertEqual(len(additions), 13)
        for item in catalog["candidates"]:
            source_id = item["id"].rsplit("-", 1)[-1]
            url = item["direct_video_url"]
            self.assertTrue(url.startswith("https://videos.pexels.com/video-files/"))
            self.assertRegex(url, rf"/video-files/{re.escape(source_id)}/[^/]+\.mp4$")
            self.assertIn(source_id, item["source_page_url"])

    def test_two_new_candidates_are_approved_and_eligible(self):
        catalog = json.loads(Path("data/background_candidates.json").read_text(encoding="utf-8"))
        approved_ids = {
            "pexels-mosque-architecture-28899957",
            "pexels-ancient-mosque-architecture-36628576",
        }
        entries = {item["id"]: item for item in catalog["candidates"]}
        self.assertTrue(approved_ids.issubset(entries))
        for asset_id in approved_ids:
            item = entries[asset_id]
            self.assertTrue(item["approved"])
            self.assertTrue(item["user_approved"])
            self.assertTrue(item["download_verified"])
            self.assertEqual(item["aspect_ratio"], "9:16")
            self.assertTrue(item["direct_video_url"].startswith("https://"))
        eligible_ids = {
            item["id"] for item in load_eligible_backgrounds(Path("data/background_candidates.json"))
        }
        self.assertTrue(approved_ids.issubset(eligible_ids))

    def test_all_seventeen_candidates_are_download_verified(self):
        catalog = json.loads(Path("data/background_candidates.json").read_text(encoding="utf-8"))
        verified = [item for item in catalog["candidates"] if item["download_verified"]]
        self.assertEqual(len(verified), 17)


if __name__ == "__main__":
    unittest.main()
