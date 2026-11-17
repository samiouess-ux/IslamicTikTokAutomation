import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import render_quran_review_previews as renderer


class CinematicReviewRendererTests(unittest.TestCase):
    def test_background_reel_uses_slow_zoom_and_short_crossfades(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            photo = root / "mosque.jpg"
            video = root / "ocean.mp4"
            photo.touch()
            video.touch()
            output = root / "background_reel.mp4"
            scenes = [
                {"background": str(photo), "background_type": "photo", "duration": 2.5},
                {"background": str(video), "background_type": "moving_video", "duration": 3.0},
            ]
            with patch.object(renderer.subprocess, "run") as run:
                report = renderer.build_cinematic_background_reel(scenes, output)
            command = run.call_args.args[0]
            graph = command[command.index("-filter_complex") + 1]
            self.assertIn("zoompan=", graph)
            self.assertIn("xfade=transition=fade", graph)
            self.assertIn("duration=0.400000:offset=2.500000", graph)
            self.assertEqual(report["scene_count"], 2)
            self.assertEqual(report["transition_seconds"], 0.4)
            self.assertEqual(report["duration_seconds"], 5.5)

    def test_cinematic_composite_keeps_original_audio_stream_and_timed_ayahs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            intro = root / "intro.png"
            intro.touch()
            scenes = []
            for index, duration in enumerate((2.6, 3.0)):
                background = root / f"background_{index}.mp4"
                audio = root / f"ayah_{index}.mp3"
                frame = root / f"ayah_{index}.png"
                for path in (background, audio, frame):
                    path.touch()
                scenes.append({
                    "background": str(background),
                    "background_type": "moving_video",
                    "audio": str(audio),
                    "frame": str(frame),
                    "duration": duration,
                    "ayah": index + 1,
                })
            output = root / "cinematic_review.mp4"
            with patch.object(
                renderer, "build_cinematic_background_reel",
                return_value={"scene_count": 2, "transition_seconds": 0.416},
            ), patch.object(renderer.subprocess, "run") as run:
                report = renderer.render_cinematic_preview(scenes, intro, output, root)
            final_command = run.call_args_list[-1].args[0]
            graph = final_command[final_command.index("-filter_complex") + 1]
            self.assertIn("enable='lt(t,0.6)'", graph)
            self.assertIn("gte(t,0.600000)*lt(t,2.600000)", graph)
            self.assertIn("gte(t,2.600000)*lt(t,5.600000)", graph)
            self.assertEqual(final_command[final_command.index("-map") + 1], "[verse1]")
            self.assertIn("1:a:0", final_command)
            self.assertEqual(final_command[final_command.index("-c:a") + 1], "copy")
            self.assertEqual(report["scene_count"], 2)
            audio_list = (root / "cinematic_audio.txt").read_text(encoding="utf-8")
            self.assertEqual(audio_list.count("file '"), 2)

    def test_cinematic_background_rejects_invalid_scene_duration(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "finite positive duration"):
                renderer.build_cinematic_background_reel(
                    [{"background": "unused.mp4", "background_type": "moving_video", "duration": 0}],
                    Path(directory) / "unused.mp4",
                )


if __name__ == "__main__":
    unittest.main()
