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
    generate_spoken_dua_once,
    validate_live_schema,
    validate_human_review,
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


def approved_review(text):
    import hashlib
    return {
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "decision": "approved",
        "exact_text_checked": True,
        "pronunciation_checked": True,
        "reviewer": "Independent Arabic reviewer",
        "source_url": "https://sunnah.com/abudawud/43/302",
        "source_reference": "Sunan Abi Dawud 5074",
        "reviewed_at": "2026-11-08T00:00:00+00:00",
    }


class ProTtsSpaceClientTests(unittest.TestCase):
    def test_review_record_is_bound_to_exact_arabic_text(self):
        text = "اللَّهُمَّ اغْفِرْ لِي"
        validate_human_review(text, approved_review(text))
        with self.assertRaisesRegex(ProTtsSchemaError, "exact Arabic text"):
            validate_human_review(text + " ", approved_review(text))

    def test_review_gate_rejects_missing_or_unapproved_record(self):
        text = "دعاء"
        with self.assertRaisesRegex(ProTtsSchemaError, "required"):
            validate_human_review(text, None)
        record = approved_review(text)
        record["decision"] = "candidate"
        with self.assertRaisesRegex(ProTtsSchemaError, "must be approved"):
            validate_human_review(text, record)

    def test_review_gate_requires_pronunciation_and_source_evidence(self):
        text = "دعاء"
        record = approved_review(text)
        record["pronunciation_checked"] = False
        with self.assertRaisesRegex(ProTtsSchemaError, "diacritics and pronunciation"):
            validate_human_review(text, record)
        record = approved_review(text)
        record["source_url"] = "http://sunnah.com/abudawud/43/302"
        with self.assertRaisesRegex(ProTtsSchemaError, "HTTPS"):
            validate_human_review(text, record)

    def test_review_gate_requires_timezone_aware_timestamp(self):
        text = "دعاء"
        record = approved_review(text)
        record["reviewed_at"] = "2026-11-08T00:00:00"
        with self.assertRaisesRegex(ProTtsSchemaError, "valid ISO-8601"):
            validate_human_review(text, record)

    def test_review_gate_rejects_source_url_with_credentials(self):
        text = "دعاء"
        record = approved_review(text)
        record["source_url"] = "https://user:pass@sunnah.com/abudawud/43/302"
        with self.assertRaisesRegex(ProTtsSchemaError, "HTTPS"):
            validate_human_review(text, record)

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



    def test_generate_submits_once_and_accepts_valid_local_wav(self):
        import wave
        from tempfile import TemporaryDirectory

        class Job:
            def __init__(self, result):
                self._result = result
                self.timeout = None
            def result(self, timeout=None):
                self.timeout = timeout
                return self._result
            def cancel(self):
                return True

        with TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "isolated"
            output_dir.mkdir()
            audio = output_dir / "spoken_dua.wav"
            with wave.open(str(audio), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(48000)
                wav.writeframes(b"\\x00\\x00" * 480)

            outputs = [None] * EXPECTED_OUTPUTS
            outputs[0] = str(audio)
            outputs[-1] = "done"
            job = Job(outputs)

            class FakeClient:
                submit_count = 0
                def __init__(self, **kwargs):
                    self.kwargs = kwargs
                def view_api(self, **kwargs):
                    return fake_api_info()
                def submit(self, **kwargs):
                    self.submit_count += 1
                    self.payload = kwargs
                    return job

            holder = {}
            def factory(**kwargs):
                holder["client"] = FakeClient(**kwargs)
                return holder["client"]

            path, log = generate_spoken_dua_once(
                text="اللَّهُمَّ اغْفِرْ لِي",
                caption="Neutral spoken dua narration; not Quran recitation; no imitation.",
                review_record=approved_review("اللَّهُمَّ اغْفِرْ لِي"),
                output_dir=output_dir,
                timeout_seconds=90,
                client_factory=factory,
            )
            self.assertEqual(path, audio.resolve())
            self.assertEqual(log, "done")
            self.assertEqual(holder["client"].submit_count, 1)
            self.assertEqual(job.timeout, 90)
            self.assertEqual(holder["client"].kwargs["max_workers"], 1)
            self.assertEqual(holder["client"].payload["num_candidates"], 1)

    def test_generate_rejects_non_finite_or_non_positive_timeout_before_client(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            for value in (float("nan"), float("inf"), float("-inf"), 0, -1, True):
                factory_called = False
                def factory(**kwargs):
                    nonlocal factory_called
                    factory_called = True
                    raise AssertionError("client must not be constructed")
                with self.subTest(timeout=value):
                    with self.assertRaisesRegex(ValueError, "finite positive"):
                        generate_spoken_dua_once(
                            text="دعاء",
                            caption="Neutral spoken dua narration.",
                            review_record=approved_review("دعاء"),
                            output_dir=Path(tmp),
                            timeout_seconds=value,
                            client_factory=factory,
                        )
                    self.assertFalse(factory_called)

    def test_generate_timeout_is_not_retried(self):
        from tempfile import TemporaryDirectory

        class Job:
            cancel_called = False
            def result(self, timeout=None):
                raise TimeoutError("late")
            def cancel(self):
                self.cancel_called = True

        job = Job()
        class FakeClient:
            submit_count = 0
            def __init__(self, **kwargs):
                pass
            def view_api(self, **kwargs):
                return fake_api_info()
            def submit(self, **kwargs):
                self.submit_count += 1
                return job

        with TemporaryDirectory() as tmp:
            holder = {}
            def factory(**kwargs):
                holder["client"] = FakeClient(**kwargs)
                return holder["client"]
            with self.assertRaisesRegex(TimeoutError, "Do not retry automatically"):
                generate_spoken_dua_once(
                    text="دعاء",
                    caption="Neutral spoken dua narration.",
                    review_record=approved_review("دعاء"),
                    output_dir=Path(tmp),
                    client_factory=factory,
                )
        self.assertEqual(holder["client"].submit_count, 1)
        self.assertTrue(job.cancel_called)

    def test_generate_rejects_audio_path_outside_isolated_directory(self):
        from tempfile import TemporaryDirectory
        class Job:
            def result(self, timeout=None):
                outputs = [None] * EXPECTED_OUTPUTS
                outputs[0] = "/tmp/untrusted.wav"
                outputs[-1] = "done"
                return outputs
            def cancel(self):
                return True
        class FakeClient:
            def __init__(self, **kwargs):
                pass
            def view_api(self, **kwargs):
                return fake_api_info()
            def submit(self, **kwargs):
                return Job()
        with TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ProTtsSchemaError, "outside"):
                generate_spoken_dua_once(
                    text="دعاء",
                    caption="Neutral spoken dua narration.",
                    review_record=approved_review("دعاء"),
                    output_dir=Path(tmp),
                    client_factory=FakeClient,
                )


if __name__ == "__main__":
    unittest.main()
