import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from render_quran_review_previews import (render, SURAH_NAMES, fit_translation_lines,
                                            fit_arabic_lines, font_file, probe)


class ReviewPreviewRendererTests(unittest.TestCase):
    def test_arabic_layout_keeps_every_word_and_fits_compact_block(self):
        image = Image.new("RGB", (1080, 1920))
        draw = ImageDraw.Draw(image)
        original = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ وَالْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ"
        font, lines, line_height = fit_arabic_lines(draw, original, font_file())
        self.assertLessEqual(len(lines), 4)
        self.assertEqual(" ".join(lines), original)
        self.assertGreaterEqual(font.size, 48)
        self.assertGreater(line_height, font.size)

    def test_long_translation_is_fitted_without_dropping_words(self):
        image = Image.new("RGB", (1080, 1920))
        draw = ImageDraw.Draw(image)
        original = " ".join(["translation"] * 30)
        font, lines, line_height = fit_translation_lines(
            draw, original, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        )
        self.assertLessEqual(len(lines), 5)
        self.assertEqual(" ".join(lines), original)
        self.assertLessEqual(font.size, 30)
        self.assertGreaterEqual(line_height, 42)

    # Covers both scheduled multi-video batches and isolated user requests.
    def fixtures(self, root: Path):
        passages, items = [], []
        for surah, start in ((19, 81), (88, 21)):
            cid = f"quran_s{surah:03d}_{start:03d}_{start+2:03d}"
            audio_dir = root / "audio" / cid
            audio_dir.mkdir(parents=True)
            (audio_dir / "passage.mp3").write_bytes(b"placeholder")
            for n in range(start, start + 3):
                (audio_dir / f"{surah:03d}_{n:03d}.mp3").write_bytes(b"whole ayah")
            passages.append({
                "candidate_id": cid, "surah_number": surah,
                "verses": [
                    {"ayah": n, "arabic_uthmani": f"نص الآية {n}",
                     "english_saheeh_international": f"Verse {n}"}
                    for n in range(start, start + 3)
                ],
            })
            items.append({
                "candidate_id": cid, "status": "audio_prepared_requires_review",
                "requested_verses": list(range(start, start + 3)),
                "selected_verses": list(range(start, start + 3)),
                "audio_file": str(audio_dir / "passage.mp3"),
            })
        batch = {"batch_status": "review_candidates_only", "passages": passages}
        report = {"rendering_allowed": False, "telegram_delivery": False,
                  "auto_publish": False, "items": items}
        batch_path, report_path = root / "batch.json", root / "report.json"
        batch_path.write_text(json.dumps(batch), encoding="utf-8")
        report_path.write_text(json.dumps(report), encoding="utf-8")
        return batch_path, report_path

    @patch("render_quran_review_previews.download_background", side_effect=lambda url, dest: dest.write_bytes(b"x" * 100001))
    @patch("render_quran_review_previews.subprocess.check_output", return_value='{"streams":[{"codec_name":"h264"}]}')
    @patch("render_quran_review_previews.probe", return_value={
        "duration_seconds": 28.0, "width": 1080, "height": 1920,
        "video_codec": "h264", "audio_codec": "mp3",
    })
    @patch("render_quran_review_previews.make_frame")
    @patch("render_quran_review_previews.subprocess.run")
    @patch("render_quran_review_previews.font_file", return_value="/tmp/font.ttf")
    def test_renders_multiple_complete_distinct_review_previews(
        self, _font, run, make_frame, _probe, _check_output, _download
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch, report = self.fixtures(root)
            result = render(batch, report, root / "out")
            self.assertEqual(result["preview_count"], 2)
            self.assertEqual({x["surah_number"] for x in result["items"]}, {19, 88})
            self.assertTrue(all(x["review_only"] for x in result["items"]))
            self.assertTrue(all(x["audio_codec"] == "mp3" for x in result["items"]))
            self.assertFalse(result["production_approved"])
            self.assertFalse(result["telegram_delivery"])
            self.assertFalse(result["auto_publish"])
            self.assertEqual(make_frame.call_count, 6)
            self.assertEqual(SURAH_NAMES[18], "مريم")
            self.assertEqual(SURAH_NAMES[87], "الغاشية")
            self.assertEqual(SURAH_NAMES[110], "المسد")
            self.assertEqual(make_frame.call_args_list[0].args[-1], "مريم")
            self.assertEqual(make_frame.call_args_list[3].args[-1], "الغاشية")
            self.assertGreaterEqual(run.call_count, 8)
            self.assertTrue(any("-stream_loop" in call.args[0] for call in run.call_args_list))
            report_data = json.loads((root / "out" / "preview_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report_data["background_type"], "moving_video")

    @patch("render_quran_review_previews.download_background", side_effect=lambda url, dest: dest.write_bytes(b"x" * 100001))
    @patch("render_quran_review_previews.subprocess.check_output", return_value='{"streams":[{"codec_name":"h264"}]}')
    @patch("render_quran_review_previews.probe", return_value={
        "duration_seconds": 28.0, "width": 1080, "height": 1920,
        "video_codec": "h264", "audio_codec": "mp3",
    })
    @patch("render_quran_review_previews.make_frame")
    @patch("render_quran_review_previews.subprocess.run")
    @patch("render_quran_review_previews.font_file", return_value="/tmp/font.ttf")
    def test_allows_one_requested_passage_when_explicitly_configured(
        self, _font, _run, _frame, _probe, _check, _download
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch, report = self.fixtures(root)
            batch_data = json.loads(batch.read_text(encoding="utf-8"))
            report_data = json.loads(report.read_text(encoding="utf-8"))
            batch_data["passages"] = batch_data["passages"][:1]
            report_data["items"] = report_data["items"][:1]
            batch.write_text(json.dumps(batch_data), encoding="utf-8")
            report.write_text(json.dumps(report_data), encoding="utf-8")
            result = render(batch, report, root / "out", minimum_previews=1)
            self.assertEqual(result["preview_count"], 1)
            self.assertFalse(result["production_approved"])
            self.assertFalse(result["telegram_delivery"])
            self.assertFalse(result["auto_publish"])

    @patch("render_quran_review_previews.font_file", return_value="/tmp/font.ttf")
    @patch("render_quran_review_previews.download_background", side_effect=lambda url, dest: dest.write_bytes(b"x" * 100001))
    @patch("render_quran_review_previews.subprocess.check_output", return_value='{"streams":[{"codec_name":"h264"}]}')
    def test_rejects_non_prefix_audio_verse_selection_before_rendering(self, _check, _download, _font):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch, report = self.fixtures(root)
            data = json.loads(report.read_text(encoding="utf-8"))
            data["items"][0]["selected_verses"] = [81, 83]
            report.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "requested prefix"):
                render(batch, report, root / "out")

    @patch("render_quran_review_previews.subprocess.check_output", return_value=json.dumps({
        "format": {"duration": "65.000"},
        "streams": [
            {"codec_name": "h264", "width": 1080, "height": 1920},
            {"codec_name": "mp3"}
        ],
    }))
    def test_probe_accepts_exactly_65_seconds(self, _check):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "preview.mp4"
            path.write_bytes(b"video")
            info = probe(path)
            self.assertEqual(info["duration_seconds"], 65.0)

    @patch("render_quran_review_previews.subprocess.check_output", return_value=json.dumps({
        "format": {"duration": "65.001"},
        "streams": [
            {"codec_name": "h264", "width": 1080, "height": 1920},
            {"codec_name": "mp3"}
        ],
    }))
    def test_probe_rejects_video_longer_than_65_seconds(self, _check):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "preview.mp4"
            path.write_bytes(b"video")
            with self.assertRaisesRegex(RuntimeError, "outside allowed range"):
                probe(path)

    @patch("render_quran_review_previews.subprocess.check_output", return_value=json.dumps({
        "format": {"duration": "24.5"},
        "streams": [
            {"codec_name": "h264", "width": 720, "height": 1280},
            {"codec_name": "mp3"}
        ],
    }))
    def test_probe_rejects_non_vertical_video(self, _check):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "preview.mp4"
            path.write_bytes(b"video")
            with self.assertRaisesRegex(RuntimeError, "not 1080x1920"):
                probe(path)


if __name__ == "__main__":
    unittest.main()
