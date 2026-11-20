import json
import sys
import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import render_quran_review_previews as renderer
from render_quran_review_previews import (render, SURAH_NAMES, fit_translation_lines,
                                            fit_arabic_lines, fit_surah_title_font, font_file,
                                            make_frame, make_intro_frame, probe)


class ReviewPreviewRendererTests(unittest.TestCase):
    def test_photo_background_filter_has_continuous_zoom_and_pan(self):
        photo_filter = renderer.photo_motion_filter()
        self.assertIn("zoompan=", photo_filter)
        self.assertIn("1.15-0.15*cos(2*PI*on/360)", photo_filter)
        self.assertIn("x='iw/2-iw/zoom/2'", photo_filter)
        self.assertIn("y='ih/2-ih/zoom/2'", photo_filter)
        self.assertIn("fps=30", photo_filter)
        self.assertNotIn("min(zoom+", photo_filter)

    def test_scheduled_rotation_uses_the_full_approved_background_count(self):
        from datetime import datetime, timezone
        for count in (4, 11, 16, 27):
            index = renderer.scheduled_background_rotation_index(
                datetime(2026, 11, 8, 18, 0, tzinfo=timezone.utc), count
            )
            self.assertGreaterEqual(index, 0)
            self.assertLess(index, count)
        with self.assertRaisesRegex(ValueError, "At least one approved background"):
            renderer.scheduled_background_rotation_index(
                datetime(2026, 11, 8, tzinfo=timezone.utc), 0
            )

    def test_arabic_layout_keeps_every_word_and_fits_compact_block(self):
        image = Image.new("RGB", (1080, 1920))
        draw = ImageDraw.Draw(image)
        original = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ وَالْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ"
        font, lines, line_height = fit_arabic_lines(draw, original, font_file())
        self.assertLessEqual(len(lines), 4)
        self.assertEqual(" ".join(lines), original)
        self.assertGreaterEqual(font.size, 48)
        self.assertGreater(line_height, font.size)

    def test_long_quran_ayah_uses_readable_fallback_without_dropping_words(self):
        image = Image.new("RGB", (1080, 1920))
        draw = ImageDraw.Draw(image)
        # A long, complete Uthmani ayah (An-Nur 24:62) exercises the fallback
        # that the scheduled render previously lacked.
        original = (
            "إِنَّمَا الْمُؤْمِنُونَ الَّذِينَ آمَنُوا بِاللَّهِ وَرَسُولِهِ "
            "وَإِذَا كَانُوا مَعَهُ عَلَىٰ أَمْرٍ جَامِعٍ لَمْ يَذْهَبُوا "
            "حَتَّىٰ يَسْتَأْذِنُوهُ ۚ إِنَّ الَّذِينَ يَسْتَأْذِنُونَكَ "
            "أُولَٰئِكَ الَّذِينَ يُؤْمِنُونَ بِاللَّهِ وَرَسُولِهِ ۚ "
            "فَإِذَا اسْتَأْذَنُوكَ لِبَعْضِ شَأْنِهِمْ فَأْذَنْ لِمَنْ "
            "شِئْتَ مِنْهُمْ وَاسْتَغْفِرْ لَهُمُ اللَّهَ ۚ إِنَّ اللَّهَ "
            "غَفُورٌ رَحِيمٌ"
        )
        font, lines, line_height = fit_arabic_lines(draw, original, font_file())
        self.assertLessEqual(len(lines), 7)
        self.assertEqual(" ".join(lines), original)
        self.assertGreaterEqual(font.size, 28)
        self.assertGreater(line_height, font.size)

    def test_short_arabic_ayah_uses_larger_amiri_type(self):
        image = Image.new("RGB", (1080, 1920))
        draw = ImageDraw.Draw(image)
        font, lines, _ = fit_arabic_lines(draw, "حم", font_file())
        self.assertEqual(lines, ["حم"])
        self.assertGreaterEqual(font.size, 80)

    def test_long_arabic_ayah_shrinks_to_stay_below_surah_title(self):
        image = Image.new("RGB", (1080, 1920))
        draw = ImageDraw.Draw(image)
        long_ayah = (
            "إِنَّمَا الْمُؤْمِنُونَ الَّذِينَ آمَنُوا بِاللَّهِ وَرَسُولِهِ "
            "وَإِذَا كَانُوا مَعَهُ عَلَىٰ أَمْرٍ جَامِعٍ لَمْ يَذْهَبُوا "
            "حَتَّىٰ يَسْتَأْذِنُوهُ ۚ إِنَّ الَّذِينَ يَسْتَأْذِنُونَكَ "
            "أُولَٰئِكَ الَّذِينَ يُؤْمِنُونَ بِاللَّهِ وَرَسُولِهِ ۚ "
            "فَإِذَا اسْتَأْذَنُوكَ لِبَعْضِ شَأْنِهِمْ فَأْذَنْ لِمَنْ "
            "شِئْتَ مِنْهُمْ وَاسْتَغْفِرْ لَهُمُ اللَّهَ ۚ إِنَّ اللَّهَ "
            "غَفُورٌ رَحِيمٌ"
        )
        short_font, _, _ = fit_arabic_lines(draw, "حم", font_file())
        long_font, lines, line_height = fit_arabic_lines(draw, long_ayah, font_file())
        self.assertEqual(" ".join(lines), long_ayah)
        self.assertLess(long_font.size, short_font.size)
        self.assertLessEqual((len(lines) - 1) * line_height, 390)

    def test_reference_translation_wraps_into_four_centered_lines(self):
        image = Image.new("RGB", (1080, 1920))
        draw = ImageDraw.Draw(image)
        original = (
            "Indeed, We have made whatever is on the earth adornment for it, "
            "that We may test them as to which of them is best in deeds."
        )
        _, lines, _ = fit_translation_lines(
            draw, original, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            max_width=680, max_lines=8
        )
        self.assertEqual(len(lines), 4)
        self.assertEqual(" ".join(lines), original)

    def test_long_translation_is_fitted_without_dropping_words(self):
        image = Image.new("RGB", (1080, 1920))
        draw = ImageDraw.Draw(image)
        original = " ".join(["translation"] * 30)
        font, lines, line_height = fit_translation_lines(
            draw, original, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        )
        self.assertLessEqual(len(lines), 8)
        self.assertEqual(" ".join(lines), original)
        self.assertLessEqual(font.size, 32)
        self.assertGreaterEqual(line_height, 42)

    def test_long_translation_can_use_eight_readable_lines_without_dropping_words(self):
        image = Image.new("RGB", (1080, 1920))
        draw = ImageDraw.Draw(image)
        original = " ".join([f"word{i}" for i in range(72)])
        font, lines, line_height = fit_translation_lines(
            draw, original, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            max_width=820, max_lines=8
        )
        self.assertLessEqual(len(lines), 8)
        self.assertEqual(" ".join(lines), original)
        self.assertGreaterEqual(font.size, 16)
        self.assertGreaterEqual(line_height, 30)
        self.assertLessEqual((len(lines) - 1) * line_height, 300)

    def test_every_surah_title_fits_between_open_reference_brackets(self):
        image = Image.new("RGBA", (1080, 1920))
        draw = ImageDraw.Draw(image)
        path = font_file()
        for surah_name in SURAH_NAMES:
            title = f"سورة {surah_name}"
            font = renderer.fit_surah_title_font(draw, title, path)
            bounds = draw.textbbox((540, 540), title, font=font, anchor="mm",
                                   direction="rtl", language="ar")
            self.assertLessEqual(bounds[2] - bounds[0], 620, title)
            self.assertLessEqual(bounds[3] - bounds[1], 112, title)
            self.assertGreaterEqual(font.size, 48, title)

    def test_make_frame_matches_open_reference_without_panels(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "frame.png"
            make_frame(
                {"number": 5, "arabic": "وَالضُّحَىٰ وَاللَّيْلِ إِذَا سَجَىٰ",
                 "english": "By the morning brightness and by the night when it covers with darkness,"},
                93, 0, output, font_file(), SURAH_NAMES[92]
            )
            with Image.open(output) as frame:
                self.assertEqual(frame.size, (1080, 1920))
                self.assertEqual(frame.mode, "RGBA")
                # Outside text and ornament strokes, the overlay stays transparent:
                # no full-screen tint, rounded panel, or dark text backing is allowed.
                self.assertEqual(frame.getpixel((50, 350))[3], 0)
                self.assertEqual(frame.getpixel((500, 800))[3], 0)
                # The exact gold ornaments are extracted from the checked-in reference.
                alpha = frame.getchannel("A")
                self.assertIsNotNone(alpha.crop((138, 448, 270, 665)).getbbox())
                self.assertIsNotNone(alpha.crop((810, 448, 942, 665)).getbbox())
                self.assertIsNotNone(alpha.crop((298, 650, 784, 730)).getbbox())
                self.assertIsNotNone(alpha.crop((103, 846, 207, 954)).getbbox())
                self.assertEqual(renderer.APPROVED_DESIGN_REFERENCE,
                                 Path("references/approved_quran_design.png"))
                self.assertIsNotNone(alpha.getbbox())

    def test_intro_frame_uses_same_open_reference_without_old_closed_cover(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            background = root / "first_scene.jpg"
            Image.new("RGB", (1080, 1920), (20, 45, 95)).save(background)
            output = root / "opening_cover.png"
            selected = make_intro_frame(
                93, 5, 8, output, font_file(), SURAH_NAMES[92],
                background_frame=background,
                cover_rotation_index=2,
            )
            self.assertEqual(selected, "open_gold_brackets")
            with Image.open(output) as frame:
                self.assertEqual(frame.size, (1080, 1920))
                self.assertEqual(frame.mode, "RGBA")
                self.assertLessEqual(max(abs(actual - expected) for actual, expected in zip(frame.getpixel((540, 780))[:3], (20, 45, 95))), 2)
                alpha = frame.getchannel("A")
                self.assertIsNotNone(alpha.crop((138, 448, 270, 665)).getbbox())
                self.assertIsNotNone(alpha.crop((810, 448, 942, 665)).getbbox())
                self.assertIsNotNone(alpha.crop((298, 650, 784, 730)).getbbox())
                self.assertIsNotNone(alpha.getbbox())

    def test_vocalized_surah_catalog_has_all_114_chapters(self):
        self.assertEqual(len(renderer.SURAH_NAMES_TASHKEEL), 114)
        self.assertEqual(renderer.SURAH_NAMES_TASHKEEL[0], "الْفَاتِحَةِ")
        self.assertEqual(renderer.SURAH_NAMES_TASHKEEL[111], "الْإِخْلَاصِ")

    # Covers both scheduled multi-video batches and isolated user requests.
    def fixtures(self, root: Path):
        passages, items = [], []
        for surah, start in ((19, 81), (88, 21)):
            cid = f"quran_s{surah:03d}_{start:03d}_{start+2:03d}"
            audio_dir = root / "audio" / cid
            audio_dir.mkdir(parents=True)
            (audio_dir / "passage.mp3").write_bytes(b"placeholder")
            processed_dir = audio_dir / "processed"
            processed_dir.mkdir()
            processed_audio_files = {}
            for n in range(start, start + 3):
                (audio_dir / f"{surah:03d}_{n:03d}.mp3").write_bytes(b"whole ayah")
                processed = processed_dir / f"{surah:03d}_{n:03d}.mp3"
                processed.write_bytes(b"edge-silence-checked whole ayah")
                processed_audio_files[str(n)] = str(processed)
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
                "duration_seconds": 28.0,
                "requested_verses": list(range(start, start + 3)),
                "selected_verses": list(range(start, start + 3)),
                "audio_file": str(audio_dir / "passage.mp3"),
                "processed_audio_files": processed_audio_files,
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
    @patch("render_quran_review_previews.make_intro_frame")
    @patch("render_quran_review_previews.subprocess.run")
    @patch("render_quran_review_previews.font_file", return_value="/tmp/font.ttf")
    @patch("render_quran_review_previews.load_approved_photo_backgrounds", return_value=[])
    def test_renders_multiple_complete_distinct_review_previews(
        self, _photos, _font, run, make_intro_frame, make_frame, _probe, _check_output, _download
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch, report = self.fixtures(root)
            result = render(batch, report, root / "out", background_rotation_index=2)
            self.assertEqual(result["preview_count"], 2)
            self.assertEqual([x["background"]["id"] for x in result["items"]], [
                "pexels-sunset-sky-35477402", "pexels-mountain-bridge-5903759"
            ])
            first_sequence = [x["id"] for x in result["items"][0]["background_sequence"]]
            self.assertEqual(len(first_sequence), 3)
            self.assertEqual(len(set(first_sequence)), 3)
            self.assertEqual(first_sequence[0], "pexels-sunset-sky-35477402")
            self.assertEqual(
                [x["duration_seconds"] for x in result["items"][0]["background_sequence"]],
                [5.0, 40.725, 24.0],
            )
            self.assertEqual(result["background_rotation_start_index"], 2)
            self.assertEqual([x["cover_template_id"] for x in result["items"]], ["open_gold_brackets", "open_gold_brackets"])
            self.assertEqual({x["surah_number"] for x in result["items"]}, {19, 88})
            self.assertTrue(all(x["review_only"] for x in result["items"]))
            self.assertTrue(all(x["audio_codec"] == "mp3" for x in result["items"]))
            self.assertFalse(result["production_approved"])
            self.assertFalse(result["telegram_delivery"])
            self.assertFalse(result["auto_publish"])
            self.assertEqual(make_frame.call_count, 6)
            self.assertEqual(make_intro_frame.call_count, 2)
            self.assertEqual(make_intro_frame.call_args_list[0].args[:3], (19, 81, 83))
            first_render_command = next(
                call.args[0] for call in run.call_args_list
                if "-loop" in call.args[0]
            )
            filter_text = " ".join(first_render_command)
            self.assertIn("[bg][2:v]overlay=0:0:format=auto[ayah]", filter_text)
            self.assertIn("[3:v]format=rgba,fade=t=out:st=0.4:d=0.8:alpha=1[intro]", filter_text)
            self.assertIn("[ayah][intro]overlay=0:0:format=auto[v]", filter_text)
            self.assertNotIn("enable='lt(t,0.6)'", filter_text)
            self.assertLess(filter_text.index("[bg][2:v]overlay"), filter_text.index("[ayah][intro]overlay"))
            opening = result["opening_cover"]
            self.assertEqual(opening["duration_seconds"], 1.2)
            self.assertEqual(opening["fade_seconds"], 0.8)
            self.assertAlmostEqual(opening["fade_start_seconds"], 0.4)
            self.assertEqual(opening["ayah_visible_from_seconds"], 0)
            self.assertEqual(opening["audio_starts_at_seconds"], 0)
            self.assertEqual(opening["transition"], "alpha_fade_to_first_ayah")
            self.assertIn("-crf 23", " ".join(first_render_command))
            self.assertIn("-maxrate 6M", " ".join(first_render_command))
            self.assertIn("-bufsize 12M", " ".join(first_render_command))
            self.assertEqual(SURAH_NAMES[18], "مريم")
            self.assertEqual(SURAH_NAMES[87], "الغاشية")
            self.assertEqual(SURAH_NAMES[110], "المسد")
            self.assertEqual(make_frame.call_args_list[0].args[-1], "مريم")
            self.assertEqual(make_frame.call_args_list[3].args[-1], "الغاشية")
            self.assertGreaterEqual(run.call_count, 8)
            self.assertTrue(any("-stream_loop" in call.args[0] for call in run.call_args_list))
            self.assertTrue(any("processed" in " ".join(call.args[0]) for call in run.call_args_list))
            report_data = json.loads((root / "out" / "preview_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report_data["background_type"], "mixed_moving_video_and_photo")

    @patch("render_quran_review_previews.download_background", side_effect=lambda url, dest: dest.write_bytes(b"x" * 100001))
    @patch("render_quran_review_previews.subprocess.check_output", return_value='{"streams":[{"codec_name":"h264"}]}')
    @patch("render_quran_review_previews.probe", return_value={
        "duration_seconds": 46.733, "width": 1080, "height": 1920,
        "video_codec": "h264", "audio_codec": "mp3",
    })
    @patch("render_quran_review_previews.make_frame")
    @patch("render_quran_review_previews.make_intro_frame")
    @patch("render_quran_review_previews.subprocess.run")
    @patch("render_quran_review_previews.font_file", return_value="/tmp/font.ttf")
    @patch("render_quran_review_previews.load_approved_photo_backgrounds", return_value=[])
    def test_allows_one_complete_ayah_exception_up_to_60_seconds(
        self, _photos, _font, _run, _intro, _frame, _probe, _check, _download
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch, report = self.fixtures(root)
            batch_data = json.loads(batch.read_text(encoding="utf-8"))
            report_data = json.loads(report.read_text(encoding="utf-8"))
            batch_data["passages"] = batch_data["passages"][:1]
            report_data["items"] = report_data["items"][:1]
            report_data["items"][0]["selected_verses"] = [81]
            report_data["items"][0]["duration_seconds"] = 46.733
            batch.write_text(json.dumps(batch_data), encoding="utf-8")
            report.write_text(json.dumps(report_data), encoding="utf-8")
            result = render(batch, report, root / "out", minimum_previews=1)
            self.assertEqual(result["preview_count"], 1)
            self.assertEqual(result["items"][0]["duration_seconds"], 46.733)
            self.assertFalse(result["production_approved"])
            self.assertFalse(result["telegram_delivery"])
            self.assertFalse(result["auto_publish"])

    @patch("render_quran_review_previews.download_background", side_effect=lambda url, dest: dest.write_bytes(b"x" * 100001))
    @patch("render_quran_review_previews.subprocess.check_output", return_value='{"streams":[{"codec_name":"h264"}]}')
    @patch("render_quran_review_previews.probe", return_value={
        "duration_seconds": 31.9, "width": 1080, "height": 1920,
        "video_codec": "h264", "audio_codec": "mp3",
    })
    @patch("render_quran_review_previews.make_frame")
    @patch("render_quran_review_previews.make_intro_frame")
    @patch("render_quran_review_previews.subprocess.run")
    @patch("render_quran_review_previews.font_file", return_value="/tmp/font.ttf")
    @patch("render_quran_review_previews.load_approved_photo_backgrounds", return_value=[])
    def test_renders_selected_contiguous_prefix_when_later_ayahs_are_deferred(
        self, _photos, _font, _run, make_intro_frame, make_frame, _probe, _check, _download
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch, report = self.fixtures(root)
            data = json.loads(report.read_text(encoding="utf-8"))
            data["items"] = data["items"][:1]
            data["items"][0]["selected_verses"] = [81, 82]
            data["items"][0]["requested_verses"] = [81, 82, 83]
            data["items"][0]["remaining_verses"] = [83]
            report.write_text(json.dumps(data), encoding="utf-8")
            batch_data = json.loads(batch.read_text(encoding="utf-8"))
            batch_data["passages"] = batch_data["passages"][:1]
            batch.write_text(json.dumps(batch_data), encoding="utf-8")
            result = render(batch, report, root / "out", minimum_previews=1)
            self.assertEqual(result["preview_count"], 1)
            self.assertEqual(result["items"][0]["verses"], [81, 82])
            self.assertEqual(make_frame.call_count, 2)
            self.assertEqual(make_intro_frame.call_args.args[:3], (19, 81, 82))

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
            with self.assertRaisesRegex(ValueError, "contiguous requested slice"):
                render(batch, report, root / "out")

    @patch("render_quran_review_previews.subprocess.check_output", return_value=json.dumps({
        "format": {"duration": "45.000"},
        "streams": [
            {"codec_name": "h264", "width": 1080, "height": 1920},
            {"codec_name": "mp3"}
        ],
    }))
    def test_probe_accepts_video_at_45_second_maximum(self, _check):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "preview.mp4"
            path.write_bytes(b"video")
            info = probe(path)
            self.assertEqual(info["duration_seconds"], 45.0)

    @patch("render_quran_review_previews.subprocess.check_output", return_value=json.dumps({
        "format": {"duration": "60.001"},
        "streams": [
            {"codec_name": "h264", "width": 1080, "height": 1920},
            {"codec_name": "mp3"}
        ],
    }))
    def test_probe_rejects_video_over_60_seconds(self, _check):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "preview.mp4"
            path.write_bytes(b"video")
            with self.assertRaisesRegex(RuntimeError, "exceeds the absolute 60-second maximum"):
                probe(path)

    @patch("render_quran_review_previews.subprocess.check_output", return_value=json.dumps({
        "format": {"duration": "46.733"},
        "streams": [
            {"codec_name": "h264", "width": 1080, "height": 1920},
            {"codec_name": "mp3"}
        ],
    }))
    def test_probe_accepts_exceptional_single_ayah_length_below_60_seconds(self, _check):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "preview.mp4"
            path.write_bytes(b"video")
            info = probe(path)
            self.assertEqual(info["duration_seconds"], 46.733)

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


    @patch("render_quran_review_previews.media_duration_seconds", return_value=12.1)
    @patch("render_quran_review_previews.probe", side_effect=[
        {"duration_seconds": 5.0}, {"duration_seconds": 7.0}
    ])
    @patch("render_quran_review_previews.subprocess.run")
    def test_scene_assembly_crossfades_video_but_stream_copies_original_audio(self, run, _probe, _audio_duration):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            segments = [root / "ayah-1.mp4", root / "ayah-2.mp4"]
            audio_files = [root / "ayah-1.mp3", root / "ayah-2.mp3"]
            for path in segments + audio_files:
                path.write_bytes(b"media")
            concat = root / "segments.txt"
            output = root / "review.mp4"
            result = renderer.assemble_review_segments(segments, audio_files, concat, output, root)
            commands = [call.args[0] for call in run.call_args_list]
            audio_command = next(command for command in commands if "-c:a" in command and str(root / "joined_original_audio.mp3") in command)
            video_command = next(command for command in commands if "-filter_complex" in command)
            mux_command = commands[-1]
            self.assertIn(str(root / "audio_segments.txt"), audio_command)
            self.assertIn("copy", audio_command)
            self.assertIn("xfade=transition=fade", video_command[video_command.index("-filter_complex") + 1])
            self.assertIn("-an", video_command)
            self.assertIn("-c:a", mux_command)
            self.assertIn("copy", mux_command)
            self.assertFalse(result["audio_reencoded"])
            self.assertEqual(result["transition"], "video_only_crossfade")
            self.assertEqual(result["duration_target_seconds"], 12.1)
            self.assertEqual(result["video_overlap_padding_seconds"], 0.45)
            self.assertTrue((root / "audio_segments.txt").read_text(encoding="utf-8").endswith("\n"))

    def test_scene_crossfade_filter_preserves_total_video_duration_and_offsets(self):
        filter_text, total = renderer.build_scene_transition_filter([5.0, 7.0, 8.0], 0.35)
        self.assertEqual(total, 20.0)
        self.assertIn("offset=4.650000", filter_text)
        self.assertIn("offset=11.300000", filter_text)
        self.assertIn("stop_duration=0.7", filter_text)
        self.assertIn("trim=duration=20.000000", filter_text)
        self.assertIn("[xfade2]tpad=", filter_text)

    def test_scene_crossfade_rejects_segments_shorter_than_transition(self):
        with self.assertRaisesRegex(ValueError, "longer than the positive transition"):
            renderer.build_scene_transition_filter([0.2, 5.0], 0.35)

    def test_recent_visual_selection_avoids_recent_assets_and_categories(self):
        backgrounds = [
            {"id": "recent", "tags": ["sea"]},
            {"id": "same-category", "tags": ["sea", "nature"]},
            {"id": "fresh", "tags": ["forest"]},
        ]
        chosen = renderer.choose_first_background(backgrounds, 0, {"recent"}, {"sea"})
        self.assertEqual(chosen["id"], "fresh")

    def test_category_aware_ayah_selection_prefers_a_different_scene_family(self):
        backgrounds = [
            {"id": "mosque", "tags": ["mosque"], "duration_seconds": 30.0},
            {"id": "forest", "tags": ["forest"], "duration_seconds": 30.0},
        ]
        chosen = renderer.choose_background_for_ayah(backgrounds, 10.0, set(), {"mosque"})
        self.assertEqual(chosen["id"], "forest")

    def test_background_selection_preserves_rotation_when_clip_is_long_enough(self):
        backgrounds = [
            {"id": "scheduled", "duration_seconds": 12.0},
            {"id": "longer", "duration_seconds": 30.0},
            {"id": "longest", "duration_seconds": 45.0},
        ]
        chosen = renderer.choose_background_for_ayah(backgrounds, 10.0, set())
        self.assertEqual(chosen["id"], "scheduled")

    def test_background_selection_chooses_next_suitable_clip_for_long_ayah(self):
        backgrounds = [
            {"id": "scheduled", "duration_seconds": 8.0},
            {"id": "medium", "duration_seconds": 18.0},
            {"id": "longest", "duration_seconds": 45.0},
        ]
        chosen = renderer.choose_background_for_ayah(backgrounds, 20.0, set())
        self.assertEqual(chosen["id"], "longest")

    def test_background_selection_uses_longest_fallback_when_no_clip_is_long_enough(self):
        backgrounds = [
            {"id": "scheduled", "duration_seconds": 8.0},
            {"id": "medium", "duration_seconds": 18.0},
        ]
        chosen = renderer.choose_background_for_ayah(backgrounds, 60.0, set())
        self.assertEqual(chosen["id"], "medium")

    def test_background_selection_avoids_reuse_until_all_clips_are_used(self):
        backgrounds = [
            {"id": "first", "duration_seconds": 12.0},
            {"id": "second", "duration_seconds": 30.0},
        ]
        chosen = renderer.choose_background_for_ayah(backgrounds, 10.0, {"first"})
        self.assertEqual(chosen["id"], "second")

    def test_photo_background_can_cover_an_ayah_longer_than_every_video_clip(self):
        backgrounds = [
            {"id": "short-video", "duration_seconds": 8.0, "background_type": "moving_video"},
            {"id": "photo", "duration_seconds": None, "background_type": "photo"},
        ]
        chosen = renderer.choose_background_for_ayah(backgrounds, 60.0, set())
        self.assertEqual(chosen["id"], "photo")


    @patch("render_quran_review_previews.subprocess.check_output", return_value="12.500")
    def test_audio_duration_is_measured_with_ffprobe(self, _check):
        self.assertEqual(renderer.audio_duration_seconds(Path("ayah.mp3")), 12.5)

    @patch("render_quran_review_previews.subprocess.check_output", side_effect=renderer.subprocess.CalledProcessError(1, "ffprobe"))
    def test_audio_duration_probe_failure_is_a_safe_zero_fallback(self, _check):
        self.assertEqual(renderer.audio_duration_seconds(Path("ayah.mp3")), 0.0)


if __name__ == "__main__":
    unittest.main()
