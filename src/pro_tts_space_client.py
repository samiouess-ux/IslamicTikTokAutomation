"""Fail-closed contract helpers for the hosted Pro spoken-dua TTS Space.

This module performs schema validation and payload construction only. It does not
submit inference requests and must never be used for Quran recitation.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

SPACE_ID = "sherif1313/3arab-TTS-VoiceDesign-v2"
API_NAME = "/gradio_inference"
EXPECTED_INPUTS = (
    "text",
    "caption",
    "num_steps",
    "num_candidates",
    "seed_raw",
    "seconds_raw",
    "duration_scale",
    "t_schedule_mode",
    "sway_coeff",
    "cfg_guidance_mode",
    "cfg_scale_text",
    "cfg_scale_caption",
    "cfg_scale_raw",
    "cfg_min_t",
    "cfg_max_t",
    "context_kv_cache",
    "max_text_len_raw",
    "max_caption_len_raw",
    "truncation_factor_raw",
    "rescale_k_raw",
    "rescale_sigma_raw",
)
EXPECTED_OUTPUTS = 33
AUDIO_OUTPUT_SLOTS = 32


class ProTtsSchemaError(ValueError):
    """Raised when the live Space API or review record violates the contract."""


def validate_human_review(text: str, review_record: Mapping[str, Any] | None) -> None:
    """Bind an explicit human text/pronunciation decision to the exact UTF-8 input."""
    if not isinstance(text, str) or not text.strip():
        raise ProTtsSchemaError("Reviewed spoken-dua text must be non-empty.")
    if not isinstance(review_record, Mapping):
        raise ProTtsSchemaError("A human review record is required before TTS inference.")
    digest = sha256(text.encode("utf-8")).hexdigest()
    if review_record.get("text_sha256") != digest:
        raise ProTtsSchemaError("Human review record does not match the exact Arabic text.")
    if review_record.get("decision") != "approved":
        raise ProTtsSchemaError("Human review decision must be approved before TTS inference.")
    if review_record.get("exact_text_checked") is not True:
        raise ProTtsSchemaError("Human reviewer must confirm exact source-text comparison.")
    if review_record.get("pronunciation_checked") is not True:
        raise ProTtsSchemaError("Human reviewer must confirm Arabic diacritics and pronunciation.")
    reviewer = review_record.get("reviewer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise ProTtsSchemaError("Human review record must identify its reviewer.")
    source_url = review_record.get("source_url")
    try:
        parsed = urlsplit(source_url) if isinstance(source_url, str) else None
        valid_url = parsed is not None and parsed.scheme == "https" and bool(parsed.hostname)
    except ValueError:
        valid_url = False
    if not valid_url:
        raise ProTtsSchemaError("Human review record must include the exact HTTPS religious source URL.")
    reference = review_record.get("source_reference")
    if not isinstance(reference, str) or not reference.strip():
        raise ProTtsSchemaError("Human review record must include the exact source reference.")
    reviewed_at = review_record.get("reviewed_at")
    if not isinstance(reviewed_at, str) or not reviewed_at.strip():
        raise ProTtsSchemaError("Human review record must include an ISO-8601 review timestamp.")
    try:
        datetime.fromisoformat(reviewed_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProTtsSchemaError("Human review timestamp must be valid ISO-8601.") from exc


def _endpoint_info(api_info: Mapping[str, Any]) -> Mapping[str, Any]:
    endpoints = api_info.get("named_endpoints")
    if not isinstance(endpoints, Mapping):
        raise ProTtsSchemaError("Gradio API metadata has no named_endpoints mapping.")
    endpoint = endpoints.get(API_NAME)
    if not isinstance(endpoint, Mapping):
        raise ProTtsSchemaError(f"Live Space is missing expected endpoint {API_NAME}.")
    return endpoint


def validate_live_schema(api_info: Mapping[str, Any]) -> Mapping[str, Any]:
    """Require the exact ordered input contract and 32 audio slots + log output."""
    endpoint = _endpoint_info(api_info)
    parameters = endpoint.get("parameters")
    returns = endpoint.get("returns")
    if not isinstance(parameters, list) or len(parameters) != len(EXPECTED_INPUTS):
        raise ProTtsSchemaError("Live TTS endpoint must expose exactly 21 input parameters.")
    names = tuple(
        item.get("parameter_name") if isinstance(item, Mapping) else None
        for item in parameters
    )
    if names != EXPECTED_INPUTS:
        raise ProTtsSchemaError("Live TTS parameter names/order differ from the reviewed contract.")
    if parameters[0].get("parameter_has_default") is not False:
        raise ProTtsSchemaError("The first text parameter must remain required.")
    if not isinstance(returns, list) or len(returns) != EXPECTED_OUTPUTS:
        raise ProTtsSchemaError("Live TTS endpoint must expose exactly 33 outputs.")
    return endpoint


def build_payload(
    api_info: Mapping[str, Any],
    *,
    text: str,
    caption: str,
) -> dict[str, Any]:
    """Build named inputs from live defaults; override only text and voice description."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Spoken dua text must be a non-empty string.")
    if not isinstance(caption, str) or not caption.strip():
        raise ValueError("A reviewed, neutral voice description is required.")
    endpoint = validate_live_schema(api_info)
    payload: dict[str, Any] = {}
    for parameter in endpoint["parameters"]:
        name = parameter["parameter_name"]
        if parameter["parameter_has_default"]:
            payload[name] = parameter.get("parameter_default")
        elif name == "text":
            payload[name] = text
        else:
            raise ProTtsSchemaError(f"Unexpected additional required parameter: {name}")
    payload["text"] = text
    payload["caption"] = caption
    if payload.get("num_candidates") != 1:
        raise ProTtsSchemaError("Pro preview must request exactly one audio candidate.")
    return payload


def extract_single_audio_result(result: Any) -> tuple[str, str]:
    """Accept exactly one returned local audio path and the final textual log."""
    if not isinstance(result, (tuple, list)) or len(result) != EXPECTED_OUTPUTS:
        raise ProTtsSchemaError("Inference result must contain exactly 33 ordered outputs.")
    audio_values = result[:AUDIO_OUTPUT_SLOTS]
    log = result[-1]
    if not isinstance(log, str):
        raise ProTtsSchemaError("The final TTS output must be a text log.")
    paths = [
        value for value in audio_values
        if isinstance(value, (str, Path)) and str(value).strip()
    ]
    if len(paths) != 1:
        raise ProTtsSchemaError("Expected exactly one non-empty audio file among 32 output slots.")
    return str(paths[0]), log

def generate_spoken_dua_once(
    *,
    text: str,
    caption: str,
    review_record: Mapping[str, Any] | None,
    output_dir: Path,
    timeout_seconds: float = 150.0,
    client_factory: Any = None,
) -> tuple[Path, str]:
    """Submit one text-review-bound spoken-dua job; never retry or call Quran text."""
    validate_human_review(text, review_record)
    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
        raise ValueError("A finite positive inference timeout is required.")
    if timeout_seconds > 180:
        raise ValueError("Inference timeout cannot exceed 180 seconds.")
    if client_factory is None:
        try:
            from gradio_client import Client
        except ImportError as exc:
            raise RuntimeError("Install the pinned hf-gradio dependency before TTS use.") from exc
        client_factory = Client

    destination = output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    client = client_factory(
        src=SPACE_ID,
        max_workers=1,
        verbose=False,
        download_files=str(destination),
        analytics_enabled=False,
    )
    api_info = client.view_api(return_format="dict", print_info=False)
    payload = build_payload(api_info, text=text, caption=caption)

    # Exactly one submission. No automatic retry, including after an ambiguous timeout.
    job = client.submit(**payload, api_name=API_NAME)
    try:
        result = job.result(timeout=float(timeout_seconds))
    except TimeoutError:
        try:
            job.cancel()
        except Exception:
            pass
        raise TimeoutError(
            "TTS job exceeded its one-attempt timeout; outcome may be uncertain. Do not retry automatically."
        )

    audio_path_text, generation_log = extract_single_audio_result(result)
    audio_path = Path(audio_path_text).resolve()
    try:
        audio_path.relative_to(destination)
    except ValueError as exc:
        raise ProTtsSchemaError("Returned audio file is outside the isolated output directory.") from exc
    if not audio_path.is_file() or audio_path.stat().st_size < 44:
        raise ProTtsSchemaError("Returned audio file is missing or too small to be a WAV file.")
    try:
        import wave
        with wave.open(str(audio_path), "rb") as wav:
            if wav.getnchannels() not in (1, 2) or wav.getframerate() <= 0 or wav.getnframes() <= 0:
                raise ProTtsSchemaError("Returned WAV has invalid channels, sample rate, or frame count.")
    except (wave.Error, EOFError) as exc:
        raise ProTtsSchemaError("Returned audio is not a valid readable WAV file.") from exc
    return audio_path, generation_log
