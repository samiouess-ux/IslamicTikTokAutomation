"""Offline tests for the Pro Telegram caption preparation."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from prepare_pro_telegram_caption import main


class PrepareProCaptionTests(unittest.TestCase):
    def test_caption_builder_rejects_non_pro_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "manifest.json"
            output = root / "caption.json"
            manifest.write_text(json.dumps({"content_type": "quran"}), encoding="utf-8")
            old_argv = sys.argv
            try:
                sys.argv = ["prepare_pro_telegram_caption.py", "--manifest", str(manifest),
                            "--output", str(output)]
                with self.assertRaisesRegex(SystemExit, "source, visual, audio"):
                    main()
            finally:
                sys.argv = old_argv


if __name__ == "__main__":
    unittest.main()
