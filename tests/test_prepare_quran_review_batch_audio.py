import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import prepare_quran_review_batch_audio as module


class FakeArchive:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def open(self, member):
        return io.BytesIO(b"fake-mp3")


class QuranBatchAudioTests(unittest.TestCase):
    def test_prepares_distinct_surahs_without_approving_or_publishing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch = {
                "batch_status": "review_candidates_only",
                "rendering_allowed": False,
                "auto_publish": False,
                "passages": [
                    {"candidate_id": "s1", "surah_number": 1, "verses": [{"ayah": 1}, {"ayah": 2}]},
                    {"candidate_id": "s2", "surah_number": 2, "verses": [{"ayah": 1}, {"ayah": 2}]},
                    {"candidate_id": "s3", "surah_number": 3, "verses": [{"ayah": 1}, {"ayah": 2}, {"ayah": 3}]},
                ],
            }
            inventory = {
                "mapped_verse_count": 6236,
                "verses": {f"{s}:{a}": f"{s}-{a}.mp3" for s in (1, 2, 3) for a in (1, 2, 3)},
            }
            batch_path, inventory_path = root / "batch.json", root / "inventory.json"
            batch_path.write_text(json.dumps(batch), encoding="utf-8")
            inventory_path.write_text(json.dumps(inventory), encoding="utf-8")

            def fake_run(command, **kwargs):
                Path(command[-1]).write_bytes(b"combined")
                return None

            def fake_trim(source, destination, source_duration):
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(b"trimmed")
                return source_duration

            with patch.object(module, "RemoteZip", return_value=FakeArchive()), \
                 patch.object(module, "probe", side_effect=lambda p: ({"s1": 33.0, "s2": 39.0, "s3": 40.0}[Path(p).parents[1].name] if Path(p).name == "passage.mp3" else {"001_001.mp3": 16.0, "001_002.mp3": 17.0, "002_001.mp3": 26.0, "002_002.mp3": 13.0, "003_001.mp3": 20.0, "003_002.mp3": 20.0, "003_003.mp3": 40.0}[Path(p).name])), \
                 patch.object(module, "trim_edge_silence", side_effect=fake_trim), \
                 patch.object(module.subprocess, "run", side_effect=fake_run):
                report = module.prepare_batch(batch_path, inventory_path, root / "out")

            self.assertEqual(report["audio_prepared_count"], 3)
            self.assertEqual(report["preview_part_count"], 3)
            partials = [item for item in report["items"] if item["source_candidate_id"] == "s3"]
            self.assertEqual([item["selected_verses"] for item in partials], [[1, 2]])
            self.assertEqual(partials[0]["requested_verses"], [1, 2, 3])
            self.assertEqual(partials[0]["remaining_verses"], [3])
            self.assertFalse(partials[0]["passage_complete"])
            self.assertEqual(partials[0]["part_count"], 1)
            self.assertEqual(partials[0]["duration_seconds"], 40.0)
            self.assertEqual(partials[0]["processed_verse_durations_seconds"], {1: 20.0, 2: 20.0})
            self.assertIn("only confirmed delivery advances the sequence", report["continuation_policy"])
            self.assertTrue((root / "out" / "s3" / "processed" / "003_003.mp3").is_file())
            self.assertTrue(Path(partials[0]["processed_audio_files"]["1"]).is_file())
            self.assertEqual(report["distinct_surah_count"], 3)
            self.assertFalse(report["rendering_allowed"])
            self.assertFalse(report["telegram_delivery"])
            self.assertFalse(report["auto_publish"])
            self.assertTrue(all(not item.get("audio_approved", True) for item in report["items"]))

    def test_selects_longest_contiguous_processed_ayah_prefix_up_to_40_seconds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch = {
                "batch_status": "review_candidates_only",
                "rendering_allowed": False,
                "auto_publish": False,
                "passages": [{
                    "candidate_id": "variable-length",
                    "surah_number": 41,
                    "verses": [{"ayah": 1}, {"ayah": 2}, {"ayah": 3}],
                }],
            }
            inventory = {
                "mapped_verse_count": 6236,
                "verses": {f"41:{n}": f"41-{n}.mp3" for n in (1, 2, 3)},
            }
            batch_path, inventory_path = root / "batch.json", root / "inventory.json"
            batch_path.write_text(json.dumps(batch), encoding="utf-8")
            inventory_path.write_text(json.dumps(inventory), encoding="utf-8")

            def fake_run(command, **kwargs):
                Path(command[-1]).write_bytes(b"combined")
                return None

            trimmed = iter([18.0, 17.0, 9.0])
            def fake_trim(source, destination, source_duration):
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(b"trimmed")
                return next(trimmed)

            with patch.object(module, "RemoteZip", return_value=FakeArchive()), \
                 patch.object(module, "probe", side_effect=[20.0, 18.0, 10.0, 35.0]), \
                 patch.object(module, "trim_edge_silence", side_effect=fake_trim), \
                 patch.object(module.subprocess, "run", side_effect=fake_run):
                report = module.prepare_batch(batch_path, inventory_path, root / "out", target_count=1)

            item = report["items"][0]
            self.assertEqual(item["selected_verses"], [1, 2])
            self.assertEqual(item["duration_seconds"], 35.0)
            self.assertEqual(item["processed_verse_durations_seconds"], {1: 18.0, 2: 17.0})
            self.assertEqual(set(item["processed_audio_files"]), {"1", "2"})

    def test_accepts_short_complete_surah_without_artificial_30_second_minimum(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch = {
                "batch_status": "review_candidates_only",
                "rendering_allowed": False,
                "auto_publish": False,
                "passages": [{
                    "candidate_id": "short-surah",
                    "surah_number": 112,
                    "verses": [{"ayah": 1}, {"ayah": 2}, {"ayah": 3}, {"ayah": 4}],
                }],
            }
            inventory = {
                "mapped_verse_count": 6236,
                "verses": {f"112:{n}": f"112-{n}.mp3" for n in (1, 2, 3, 4)},
            }
            batch_path, inventory_path = root / "batch.json", root / "inventory.json"
            batch_path.write_text(json.dumps(batch), encoding="utf-8")
            inventory_path.write_text(json.dumps(inventory), encoding="utf-8")

            def fake_run(command, **kwargs):
                Path(command[-1]).write_bytes(b"combined")
                return None

            trimmed = iter([3.0, 3.0, 3.0, 3.0])
            def fake_trim(source, destination, source_duration):
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(b"trimmed")
                return next(trimmed)

            with patch.object(module, "RemoteZip", return_value=FakeArchive()), \
                 patch.object(module, "probe", side_effect=[3.0, 3.0, 3.0, 3.0, 12.0]), \
                 patch.object(module, "trim_edge_silence", side_effect=fake_trim), \
                 patch.object(module.subprocess, "run", side_effect=fake_run):
                report = module.prepare_batch(batch_path, inventory_path, root / "out", target_count=1)

            item = report["items"][0]
            self.assertEqual(item["selected_verses"], [1, 2, 3, 4])
            self.assertEqual(item["duration_seconds"], 12.0)
            self.assertEqual(report["minimum_seconds"], 0.0)
            self.assertEqual(report["maximum_seconds"], 40.0)

    def test_defers_a_single_ayah_that_exceeds_40_seconds_without_truncating(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch = {
                "batch_status": "review_candidates_only",
                "rendering_allowed": False,
                "auto_publish": False,
                "passages": [{"candidate_id": "long-ayah", "surah_number": 2, "verses": [{"ayah": 1}]}],
            }
            inventory = {"mapped_verse_count": 6236, "verses": {"2:1": "2-1.mp3"}}
            batch_path, inventory_path = root / "batch.json", root / "inventory.json"
            batch_path.write_text(json.dumps(batch), encoding="utf-8")
            inventory_path.write_text(json.dumps(inventory), encoding="utf-8")

            def fake_run(command, **kwargs):
                Path(command[-1]).write_bytes(b"combined")
                return None

            def fake_trim(source, destination, source_duration):
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(b"trimmed")
                return 66.0

            with (
                patch.object(module, "RemoteZip", return_value=FakeArchive()),
                patch.object(module, "probe", side_effect=[66.0, 66.0]),
                patch.object(module, "trim_edge_silence", side_effect=fake_trim),
                patch.object(module.subprocess, "run", side_effect=fake_run),
            ):
                report = module.prepare_batch(batch_path, inventory_path, root / "out", target_count=1)

            item = report["items"][0]
            self.assertEqual(item["status"], "deferred_single_ayah_exceeds_40_seconds")
            self.assertEqual(item["selected_verses"], [])
            self.assertEqual(item["remaining_verses"], [1])
            self.assertFalse(item["passage_complete"])
            self.assertEqual(report["audio_prepared_count"], 0)
            self.assertEqual(report["maximum_seconds"], 40.0)

    def test_trim_edge_silence_keeps_mp3_and_preserves_the_recitation_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.mp3"
            destination = root / "trimmed.mp3"
            module.subprocess.run([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono:d=0.8",
                "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100:duration=1.0",
                "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono:d=1.0",
                "-filter_complex", "[0:a][1:a][2:a]concat=n=3:v=0:a=1[out]",
                "-map", "[out]", "-c:a", "libmp3lame", "-q:a", "2", str(source)
            ], check=True)
            original_duration = module.probe(source)
            trimmed_duration = module.trim_edge_silence(source, destination, original_duration)
            codec = module.subprocess.check_output([
                "ffprobe", "-v", "error", "-select_streams", "a:0",
                "-show_entries", "stream=codec_name", "-of", "default=nw=1:nk=1",
                str(destination)
            ], text=True).strip()
            self.assertEqual(codec, "mp3")
            self.assertLess(trimmed_duration, original_duration - 1.0)
            self.assertGreater(trimmed_duration, 1.0)
            check = module.subprocess.run([
                "ffmpeg", "-hide_banner", "-i", str(destination),
                "-af", "silencedetect=noise=-50dB:d=0.25", "-f", "null", "-"
            ], capture_output=True, text=True)
            self.assertEqual(check.returncode, 0)
            self.assertNotIn("silence_start: 0", check.stderr)
            self.assertNotIn("silence_end:", check.stderr)

    def test_rejects_non_review_only_batch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch_path, inventory_path = root / "batch.json", root / "inventory.json"
            batch_path.write_text(json.dumps({"batch_status": "approved", "rendering_allowed": True}))
            inventory_path.write_text(json.dumps({"mapped_verse_count": 6236, "verses": {}}))
            with self.assertRaisesRegex(ValueError, "review-only"):
                module.prepare_batch(batch_path, inventory_path, root / "out")


if __name__ == "__main__":
    unittest.main()
