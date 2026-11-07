"""Offline tests for the live hosted TTS contract; no network or inference."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pro_tts_space_client import (
    API_NAME,
    EXPECTED_INPUTS,
    EXPECTED_OUTPUTS,
    ProTtsSchemaError,
    build_payload,
    extract_single_audio_result,
    validate_live_schema,
)


def fake_api_info():
    parameters = []
    for name in EXPECTED_INPUTS:
        parameters.append({
            "parameter_name": name,
            "parameter_has_default": name != "text",
            "parameter_default": None if name == "text" else (
                1 if name == "num_candidates" else
                40 if name == "num_steps" else
                1.0 if name == "duration_scale" else
                "linear" if name == "t_schedule_mode" else
                -1.0 if name == "sway_coeff" else
                "independent" if name == "cfg_guidance_mode" else
                3.0 if name == "cfg_scale_text" else
                4.0 if name == "cfg_scale_caption" else
                0.5 if name == "cfg_min_t" else
                1.0 if name == "cfg_max_t" else
                True if name == "context_kv_cache" else ""
            ),
        })
    return {"named_endpoints": {
        API_NAME: {
            "parameters": parameters,
            "returns": [{"label": f"output_{i}", "type": {}} for i in range(EXPECTED_OUTPUTS)],
        }
    }}


class ProTtsSpaceClientTests(unittest.TestCase):
    def test_validates_live_endpoint_contract(self):
        endpoint = validate_live_schema(fake_api_info())
        self.assertEqual(len(endpoint["parameters"]), 21)
        self.assertEqual(len(endpoint["returns"]), 33)

    def test_builds_named_payload_from_live_defaults(self):
        payload = build_payload(
            fake_api_info(),
            text="اللَّهُمَّ اغْفِرْ لِي",
            caption="Neutral, calm Modern Standard Arabic spoken supplication; no recitation and no imitation.",
        )
        self.assertEqual(tuple(payload), EXPECTED_INPUTS)
        self.assertEqual(payload["num_candidates"], 1)
        self.assertEqual(payload["num_steps"], 40)
        self.assertEqual(payload["text"], "اللَّهُمَّ اغْفِرْ لِي")

    def test_rejects_changed_parameter_order(self):
        info = fake_api_info()
        info["named_endpoints"][API_NAME]["parameters"].reverse()
        with self.assertRaisesRegex(ProTtsSchemaError, "names/order"):
            validate_live_schema(info)

    def test_rejects_changed_output_count(self):
        info = fake_api_info()
        info["named_endpoints"][API_NAME]["returns"].pop()
        with self.assertRaisesRegex(ProTtsSchemaError, "33 outputs"):
            validate_live_schema(info)

    def test_rejects_missing_required_text(self):
        info = fake_api_info()
        info["named_endpoints"][API_NAME]["parameters"][0]["parameter_has_default"] = True
        with self.assertRaisesRegex(ProTtsSchemaError, "text parameter"):
            validate_live_schema(info)

    def test_rejects_empty_text_or_caption(self):
        with self.assertRaisesRegex(ValueError, "non-empty"):
            build_payload(fake_api_info(), text=" ", caption="neutral")
        with self.assertRaisesRegex(ValueError, "voice description"):
            build_payload(fake_api_info(), text="دعاء", caption=" ")

    def test_extracts_exactly_one_audio_file_and_log(self):
        outputs = [None] * EXPECTED_OUTPUTS
        outputs[0] = "/tmp/pro-dua.wav"
        outputs[-1] = "generation complete"
        self.assertEqual(
            extract_single_audio_result(outputs),
            ("/tmp/pro-dua.wav", "generation complete"),
        )

    def test_rejects_multiple_audio_candidates(self):
        outputs = [None] * EXPECTED_OUTPUTS
        outputs[0] = "/tmp/a.wav"
        outputs[1] = "/tmp/b.wav"
        outputs[-1] = "done"
        with self.assertRaisesRegex(ProTtsSchemaError, "exactly one"):
            extract_single_audio_result(outputs)

    def test_rejects_wrong_result_shape(self):
        with self.assertRaisesRegex(ProTtsSchemaError, "33 ordered outputs"):
            extract_single_audio_result(["/tmp/a.wav", "done"])


if __name__ == "__main__":
    unittest.main()
