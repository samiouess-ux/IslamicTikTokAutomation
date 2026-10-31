import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from render_quran_review_previews import render


class ReviewPreviewRendererTests(unittest.TestCase):
    def fixtures(self, root: Path):
        audio_dir = root / "audio" / "quran_s019_081_083"
        audio_dir.mkdir(parents=True)
        (audio_dir / "passage.mp3").write_bytes(b"placeholder")
        for n in (81, 82, 83):
            (audio_dir / f"019_{n:03d}.mp3").write_bytes(b"whole ayah")
        batch = {
            "batch_status": "review_candidates_only",
            "passages": [{
                "candidate_id": "quran_s019_081_083",
                "surah_number": 19,
                "verses": [
                    {"ayah": n, "arabic_uthmani": f"نص الآية {n}", "english_saheeh_international": f"Verse {n}"}
                    for n in (81, 82, 83)
                ],
            }],
        }
        report = {
            "rendering_allowed": False, "telegram_delivery": False, "auto_publish": False,
            "items": [{
                "candidate_id": "quran_s019_081_083", "status": "audio_prepared_requires_review",
                "selected_verses": [81, 82, 83], "audio_file": str(audio_dir / "passage.mp3"),
            }],
        }
        batch_path, report_path = root / "batch.json", root / "report.json"
        batch_path.write_text(json.dumps(batch), encoding="utf-8")
        report_path.write_text(json.dumps(report), encoding="utf-8")
        return batch_path, report_path

    @patch("render_quran_review_previews.probe", return_value={
        "duration_seconds": 28.0, "width": 1080, "height": 1920,
        "video_codec": "h264", "audio_codec": "mp3",
    })
    @patch("render_quran_review_previews.make_frame")
    @patch("render_quran_review_previews.subprocess.run")
    @patch("render_quran_review_previews.font_file", return_value="/tmp/font.ttf")
    def test_renders_complete_distinct_review_preview_with_safety_flags_false(
        self, _font, run, make_frame, _probe
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch, report = self.fixtures(root)
            result = render(batch, report, root / "out")
            self.assertEqual(result["preview_count"], 1)
            item = result["items"][0]
            self.assertEqual(item["verses"], [81, 82, 83])
            self.assertEqual((item["width"], item["height"]), (1080, 1920))
            self.assertTrue(item["review_only"])
            self.assertFalse(item["audio_approved"])
            self.assertFalse(item["telegram_delivery"])
            self.assertFalse(result["auto_publish"])
            self.assertEqual(make_frame.call_count, 3)
            self.assertGreaterEqual(run.call_count, 4)

    @patch("render_quran_review_previews.font_file", return_value="/tmp/font.ttf")
    def test_rejects_incomplete_audio_verse_coverage(self, _font):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch, report = self.fixtures(root)
            data = json.loads(report.read_text(encoding="utf-8"))
            data["items"][0]["selected_verses"] = [81, 82]
            report.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "do not match"):
                render(batch, report, root / "out")


if __name__ == "__main__":
    unittest.main()
