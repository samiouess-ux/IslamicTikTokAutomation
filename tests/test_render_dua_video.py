"""Regression tests for separate, duration-controlled dua/dhikr screens."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import render_dua_video


class DuaRendererTests(unittest.TestCase):
    def test_each_item_requires_explicit_positive_duration(self):
        self.assertEqual(render_dua_video.item_duration({"duration_seconds": 4}), 4.0)
        for value in (None, 0, -1, True, "4", float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value), self.assertRaises(SystemExit):
                render_dua_video.item_duration({"duration_seconds": value})

    def test_ffprobe_rejects_non_finite_media_duration(self):
        for raw in ("nan", "inf", "-inf"):
            with self.subTest(raw=raw):
                result = type("Result", (), {"stdout": raw})()
                with patch.object(render_dua_video.subprocess, "run", return_value=result):
                    with self.assertRaisesRegex(SystemExit, "invalid duration"):
                        render_dua_video.probe_duration(Path("sample.mp4"))

    def test_slideshow_creates_one_overlay_per_item(self):
        items = [
            {"arabic": "الأول", "source_name": "المصدر الأول", "duration_seconds": 3},
            {"arabic": "الثاني", "source_name": "المصدر الثاني", "duration_seconds": 5},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            with patch.object(render_dua_video, "create_overlay") as draw:
                duration = render_dua_video.build_slideshow(items, "ذكر", work)
            self.assertEqual(duration, 8.0)
            self.assertEqual(draw.call_count, 2)
            self.assertEqual([call.args[1] for call in draw.call_args_list], items)
            playlist = (work / "overlays.ffconcat").read_text(encoding="utf-8")
            self.assertIn("item_000.png", playlist)
            self.assertIn("item_001.png", playlist)
            self.assertEqual(playlist.count("duration "), 2)

    def test_audio_duration_mismatch_fails_closed(self):
        audio = Path('audio.mp3')
        with patch.object(render_dua_video, 'probe_duration', return_value=9.0):
            self.assertEqual(render_dua_video.validate_audio_duration(audio, 9.5), 9.0)
        with patch.object(render_dua_video, 'probe_duration', return_value=12.0):
            with self.assertRaises(SystemExit):
                render_dua_video.validate_audio_duration(audio, 9.5)

    def test_renderer_does_not_silently_pad_audio(self):
        source = (ROOT / 'src' / 'render_dua_video.py').read_text(encoding='utf-8')
        self.assertIn('validate_audio_duration(audio_file, duration)', source)
        self.assertNotIn('apad', source)

    def test_duration_policy_enforces_the_40_second_cap(self):
        self.assertEqual(render_dua_video.TARGET_MAX_DURATION_SECONDS, 40.0)
        self.assertEqual(render_dua_video.HARD_MAX_DURATION_SECONDS, 40.0)
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(render_dua_video, "create_overlay"):
                accepted = render_dua_video.build_slideshow(
                    [{"arabic": "ذكر", "source_name": "مصدر", "duration_seconds": 40}],
                    "ذكر", Path(tmp),
                )
                self.assertEqual(accepted, 40.0)
            with patch.object(render_dua_video, "create_overlay"):
                with self.assertRaisesRegex(SystemExit, "hard limit of 40 seconds"):
                    render_dua_video.build_slideshow(
                        [{"arabic": "ذكر", "source_name": "مصدر", "duration_seconds": 40.01}],
                        "ذكر", Path(tmp),
                    )

    def test_renderer_keeps_validation_and_separate_content_type_gate(self):
        source = (ROOT / "src" / "render_dua_video.py").read_text(encoding="utf-8")
        self.assertIn("validate_content_manifest(data, allow_candidate_preview=args.preview_only)", source)
        self.assertIn("validate_manifest_media_rights(", source)
        self.assertIn('bg_file = media_paths["visual"]', source)
        self.assertIn('audio_file = media_paths["audio"]', source)
        self.assertNotIn('"curl"', source)
        self.assertIn('not in {"dua", "dhikr"}', source)
        self.assertIn("audio is checked as a whole, not synced per item", source)

    def test_candidate_preview_requires_explicit_renderer_flag(self):
        source = (ROOT / "src" / "render_dua_video.py").read_text(encoding="utf-8")
        self.assertIn('data.get("lifecycle_status") == "candidate_preview" and not args.preview_only', source)
        self.assertIn('data.get("lifecycle_status") == "candidate_preview" and data.get("preview_only") is True', source)
        self.assertIn('parser.add_argument("--preview-only"', source)

    def test_overlay_rejects_missing_source_and_text(self):
        with self.assertRaises(SystemExit):
            render_dua_video.create_overlay("ذكر", {"arabic": "نص"}, Path("unused.png"))


if __name__ == "__main__":
    unittest.main()
