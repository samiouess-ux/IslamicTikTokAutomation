"""Shared fail-closed validation for Quran and dua/dhikr content manifests.

This module validates metadata and safety gates only. It does not authenticate
religious wording or grant audio/background rights; those require trusted
sources and explicit human review recorded in the manifest.
"""
from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit


CONTENT_TYPES = {"quran", "dua", "dhikr"}
AUDIO_KINDS = {"quran_recitation", "spoken_dua", "ambient_nature", "silent"}

def _is_valid_https_url(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = urlsplit(value)
        return (parsed.scheme == "https" and bool(parsed.hostname)
                and parsed.username is None and parsed.password is None)
    except ValueError:
        return False


def validate_content_manifest(data: dict[str, Any], *, allow_candidate_preview: bool = False) -> None:
    if not isinstance(data, dict):
        raise SystemExit("Manifest must be a JSON object.")

    content_type = data.get("content_type", "quran")
    if not isinstance(content_type, str) or content_type not in CONTENT_TYPES:
        raise SystemExit("content_type must be quran, dua, or dhikr.")

    source = data.get("source")
    visual = data.get("visual")
    audio = data.get("audio")
    publishing = data.get("publishing", {})
    if not all(isinstance(x, dict) for x in (source, visual, audio, publishing)):
        raise SystemExit("source, visual, audio and publishing must be objects.")

    if publishing.get("auto_publish", False):
        raise SystemExit("Auto-publishing must remain disabled.")
    if publishing.get("approval_required") is not True:
        raise SystemExit("Every video must require explicit user review.")

    template = visual.get("template", "ornate_gold_classic")
    supported_templates = {"ornate_gold_classic", "nature_clean", "minimal_mushaf", "cinematic_landscape"}
    if not isinstance(template, str) or template not in supported_templates:
        raise SystemExit(f"Unsupported visual template: {template}.")
    if template != "ornate_gold_classic" and visual.get("template_approved") is not True:
        raise SystemExit("A new visual template must be explicitly approved before production rendering.")
    background = visual.get("background_candidate", {})
    if not isinstance(background, dict):
        raise SystemExit("visual.background_candidate must be an object.")
    if not background.get("direct_video_url") or not background.get("source_url"):
        raise SystemExit("Background source and direct video URLs are required.")
    if background.get("approved") is not True or background.get("user_approved") is not True:
        raise SystemExit("Background must be approved and user-reviewed.")

    kind = audio.get("kind", "quran_recitation" if content_type == "quran" else None)
    if not isinstance(kind, str) or kind not in AUDIO_KINDS:
        raise SystemExit("audio.kind must explicitly identify the audio type.")
    if audio.get("music_allowed", False):
        raise SystemExit("Music is not allowed.")

    if content_type == "quran":
        if kind != "quran_recitation":
            raise SystemExit("Quran content requires authentic Quran recitation.")
        preview_only = audio.get("preview_only") is True
        approved = audio.get("approved", audio.get("approved_for_first_test_video", False)) is True
        if not approved and not preview_only:
            raise SystemExit("Quran recitation is not approved; only an explicit preview_only candidate may be rendered for review.")
        if preview_only and approved:
            raise SystemExit("A preview_only Quran recording cannot also be marked production-approved.")
        candidates = audio.get("license_research_candidates", [])
        if not isinstance(candidates, list):
            raise SystemExit("Quran license_research_candidates must be a list.")
        reviewed = audio.get("exact_recording_user_reviewed") is True or any(
            item.get("exact_recording_user_reviewed") is True
            for item in candidates if isinstance(item, dict)
        )
        if not reviewed and not preview_only:
            raise SystemExit("Exact Quran recording has not been user-reviewed.")
        rights_verified = audio.get("rights_verified") is True or any(
            isinstance(item.get("status"), str)
            and item["status"].startswith("approved_")
            for item in candidates if isinstance(item, dict)
        )
        if not rights_verified:
            raise SystemExit("Reuse permission for the exact Quran recording is not documented.")
        if not source.get("surah_number") or not source.get("verses"):
            raise SystemExit("Quran source must identify a surah and requested verses.")
        verses = data.get("verses")
        if not isinstance(verses, list) or not verses:
            raise SystemExit("Quran manifest must contain verified verses.")
        numbers = [v.get("number") for v in verses if isinstance(v, dict)]
        if len(numbers) != len(verses) or numbers != source["verses"]:
            raise SystemExit("Quran verse entries must exactly match source.verses in order.")
        for verse in verses:
            if not isinstance(verse.get("arabic"), str) or not verse["arabic"].strip():
                raise SystemExit("Every Quran verse needs exact Arabic text.")
            if not isinstance(verse.get("english"), str) or not verse["english"].strip():
                raise SystemExit("Every Quran verse needs its verified translation.")
    else:
        preview_candidate = (
            allow_candidate_preview is True
            and data.get("lifecycle_status") == "candidate_preview"
            and data.get("preview_only") is True
        )
        if data.get("lifecycle_status") == "candidate_preview" and not preview_candidate:
            raise SystemExit("Candidate preview is accepted only by the explicit preview-only validator path.")
        if data.get("lifecycle_status") == "production_approved" and data.get("preview_only") is True:
            raise SystemExit("A preview-only candidate cannot be marked production-approved.")
        if not preview_candidate and data.get("lifecycle_status", "production_approved") != "production_approved":
            raise SystemExit("Dua/dhikr lifecycle_status must be candidate_preview or production_approved.")
        if not data.get("items") or not isinstance(data["items"], list):
            raise SystemExit("Dua/dhikr manifest must contain sourced items.")
        seen_item_ids: set[str] = set()
        for item in data["items"]:
            if not isinstance(item, dict) or not isinstance(item.get("arabic"), str) or not item["arabic"].strip():
                raise SystemExit("Every dua/dhikr item needs its exact Arabic wording.")
            item_id = item.get("id")
            if not isinstance(item_id, str) or not item_id.strip() or item_id in seen_item_ids:
                raise SystemExit("Every dua/dhikr item needs a unique, stable id.")
            seen_item_ids.add(item_id)
            if (not isinstance(item.get("source_name"), str) or not item["source_name"].strip()
                    or not _is_valid_https_url(item.get("source_url"))):
                raise SystemExit("Every dua/dhikr item needs a named HTTPS religious source with a valid host.")
            if not isinstance(item.get("source_reference"), str) or not item["source_reference"].strip():
                raise SystemExit("Every dua/dhikr item needs an exact source reference (book/chapter/hadith or Quran reference).")
            if item.get("verification_status") != "verified":
                raise SystemExit("Dua/dhikr item is not marked as source-verified.")
            if item.get("human_reviewed") is not True:
                if not (preview_candidate and item.get("human_reviewed") is False):
                    raise SystemExit("Dua/dhikr item requires explicit human review before production.")
            item_kind = item.get("kind")
            if not isinstance(item_kind, str) or item_kind not in {"quranic_dua", "prophetic_dua", "dhikr", "general_supplication"}:
                raise SystemExit("Dua/dhikr item kind must be explicitly classified.")
            repeat_count = item.get("repeat_count")
            if repeat_count is not None and (type(repeat_count) is not int or repeat_count < 1):
                raise SystemExit("repeat_count must be a positive integer when provided.")
            grading = item.get("hadith_grading")
            if item_kind == "prophetic_dua" and (not isinstance(grading, str) or not grading.strip()):
                raise SystemExit("Prophetic dua requires its hadith grading/authenticity reference.")
        if kind == "quran_recitation":
            raise SystemExit("Dua/dhikr audio must not be mislabeled as Quran recitation.")
        if kind in {"spoken_dua", "ambient_nature"}:
            if audio.get("approved") is not True or audio.get("rights_verified") is not True:
                raise SystemExit("Dua/dhikr audio needs explicit approval and documented reuse permission.")
            if kind == "spoken_dua" and audio.get("exact_recording_user_reviewed") is not True:
                raise SystemExit("Exact spoken-dua recording must be user-reviewed.")
            if kind == "ambient_nature" and audio.get("user_approved") is not True:
                raise SystemExit("Ambient audio must be explicitly user-approved.")
        if kind == "silent" and audio.get("file"):
            raise SystemExit("Silent content must not declare an audio file.")
