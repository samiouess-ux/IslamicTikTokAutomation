import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import build_saad_ghamdi_audio_inventory as inventory_builder
import prepare_quran_review_batch_audio as audio_module


class SaadGhamdiSourceTests(unittest.TestCase):
    def test_builds_complete_6236_ayah_url_map_and_keeps_rights_gates_closed(self):
        inventory = inventory_builder.build_inventory()
        self.assertEqual(inventory["mapped_verse_count"], 6236)
        self.assertEqual(len(inventory["verses"]), 6236)
        self.assertEqual(inventory["verses"]["1:1"], "https://everyayah.com/data/Ghamadi_40kbps/001001.mp3")
        self.assertEqual(inventory["verses"]["2:286"], "https://everyayah.com/data/Ghamadi_40kbps/002286.mp3")
        self.assertEqual(inventory["verses"]["114:6"], "https://everyayah.com/data/Ghamadi_40kbps/114006.mp3")
        self.assertFalse(inventory["rights_verified"])
        self.assertFalse(inventory["commercial_use_allowed"])
        self.assertFalse(inventory["audio_approved"])
        self.assertFalse(inventory["rendering_allowed"])
        self.assertFalse(inventory["telegram_delivery"])
        self.assertFalse(inventory["auto_publish"])
        self.assertEqual(inventory["mapping_status"], "url_pattern_enumerated_not_network_verified")

    def test_per_ayah_downloader_streams_only_from_configured_everyayah_folder(self):
        class Response:
            status_code = 200
            def raise_for_status(self):
                return None
            def iter_content(self, chunk_size):
                self.chunk_size = chunk_size
                return [b"ID3", b"audio-bytes"]
            def close(self):
                self.closed = True

        response = Response()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "ayah.mp3"
            url = "https://everyayah.com/data/Ghamadi_40kbps/001001.mp3"
            with patch.object(audio_module.requests, "get", return_value=response) as get:
                audio_module.download_audio_member("per_ayah_http", None, url, target)
            get.assert_called_once_with(url, stream=True, timeout=(20, 60))
            self.assertEqual(target.read_bytes(), b"ID3audio-bytes")
            self.assertTrue(response.closed)

    def test_per_ayah_downloader_rejects_untrusted_url_before_network_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "ayah.mp3"
            with patch.object(audio_module.requests, "get") as get:
                with self.assertRaisesRegex(ValueError, "outside the configured EveryAyah"):
                    audio_module.download_audio_member(
                        "per_ayah_http", None, "https://example.com/001001.mp3", target
                    )
            get.assert_not_called()

    def test_review_audio_preparation_uses_direct_ayah_urls_without_opening_zip(self):
        class Response:
            def raise_for_status(self):
                return None
            def iter_content(self, chunk_size):
                return [b"fake-mp3"]
            def close(self):
                return None

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch = {
                "batch_status": "review_candidates_only",
                "rendering_allowed": False,
                "auto_publish": False,
                "passages": [{
                    "candidate_id": "saad-test",
                    "surah_number": 1,
                    "verses": [{"ayah": 1}, {"ayah": 2}],
                }],
            }
            inventory = {
                "source_type": "per_ayah_http",
                "source_name": "EveryAyah Ghamadi_40kbps (Saad Al-Ghamdi)",
                "recording_rights_status": "unverified_written_permission_required",
                "rights_verified": False,
                "mapped_verse_count": 6236,
                "verses": {
                    "1:1": "https://everyayah.com/data/Ghamadi_40kbps/001001.mp3",
                    "1:2": "https://everyayah.com/data/Ghamadi_40kbps/001002.mp3",
                },
            }
            batch_path = root / "batch.json"
            inventory_path = root / "inventory.json"
            batch_path.write_text(json.dumps(batch), encoding="utf-8")
            inventory_path.write_text(json.dumps(inventory), encoding="utf-8")

            def fake_run(command, **kwargs):
                Path(command[-1]).write_bytes(b"combined-mp3")
                return None

            def fake_trim(source, destination, source_duration):
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(b"trimmed-mp3")
                return source_duration

            with (
                patch.object(audio_module, "RemoteZip", side_effect=AssertionError("ZIP must not be opened")),
                patch.object(audio_module.requests, "get", return_value=Response()) as get,
                patch.object(audio_module, "probe", side_effect=[3.0, 3.0, 6.0]),
                patch.object(audio_module, "trim_edge_silence", side_effect=fake_trim),
                patch.object(audio_module.subprocess, "run", side_effect=fake_run),
            ):
                report = audio_module.prepare_batch(batch_path, inventory_path, root / "out", target_count=1)

            self.assertEqual(get.call_count, 2)
            self.assertEqual(report["audio_prepared_count"], 1)
            self.assertEqual(report["items"][0]["selected_verses"], [1, 2])
            self.assertEqual(report["recording_source"], "EveryAyah Ghamadi_40kbps (Saad Al-Ghamdi)")
            self.assertEqual(report["recording_rights_status"], "unverified_written_permission_required")
            self.assertFalse(report["rights_verified"])
            self.assertFalse(report["rendering_allowed"])
            self.assertFalse(report["telegram_delivery"])
            self.assertFalse(report["auto_publish"])


if __name__ == "__main__":
    unittest.main()
