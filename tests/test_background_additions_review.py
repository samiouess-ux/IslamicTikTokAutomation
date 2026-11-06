"""Safety checks for the eight additional Islamic background leads."""
import json
import unittest
from pathlib import Path


class BackgroundAdditionReviewTests(unittest.TestCase):
    def test_eight_new_candidates_are_separate_and_fail_closed(self):
        catalog = json.loads(Path("data/background_additions_review.json").read_text(encoding="utf-8"))
        self.assertEqual(len(catalog["candidates"]), 8)
        self.assertIn("not production-enabled", catalog["purpose"])
        self.assertIn("No candidate is active", catalog["activation_policy"])
        ids = [item["id"] for item in catalog["candidates"]]
        self.assertEqual(len(ids), len(set(ids)))
        resolved = [item for item in catalog["candidates"] if item["direct_video_url"]]
        unresolved = [item for item in catalog["candidates"] if not item["direct_video_url"]]
        self.assertEqual(len(resolved), 7)
        self.assertEqual(len(unresolved), 1)
        self.assertEqual(unresolved[0]["id"], "pixabay-chain-dome-rock-131292")
        for item in catalog["candidates"]:
            self.assertTrue(item["source_page_url"].startswith(("https://www.pexels.com/", "https://pixabay.com/")))
            self.assertFalse(item["download_verified"])
            self.assertFalse(item["approved"])
            self.assertFalse(item["user_approved"])

    def test_existing_four_candidate_catalog_is_unchanged(self):
        catalog = json.loads(Path("data/background_candidates.json").read_text(encoding="utf-8"))
        self.assertEqual(len(catalog["candidates"]), 4)
        self.assertTrue(all(item["user_approved"] and item["download_verified"] for item in catalog["candidates"]))


if __name__ == "__main__":
    unittest.main()
