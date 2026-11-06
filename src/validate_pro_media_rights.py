"""Fail-closed, per-asset media-rights validation for Pro dua/dhikr previews."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ASSET_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}\Z")
HASH = re.compile(r"[0-9a-f]{64}\Z")
MEDIA_ROOT = Path("assets/pro/media")
RIGHTS_ROOT = Path("content/pro/rights")
EVIDENCE_ROOT = RIGHTS_ROOT / "evidence"
USE_FIELDS = {
    "private_review": ("download", "editing", "video_synchronization", "private_review_delivery"),
    "public_social": ("download", "editing", "video_synchronization", "public_social_posting"),
    "monetized_social": ("download", "editing", "video_synchronization", "public_social_posting", "commercial_monetized_use"),
}


def _fail(message: str) -> None:
    raise ValueError("Media rights gate: " + message)


def _safe_file(repo_root: Path, relative: str, allowed_root: Path) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        _fail("asset/evidence file path is required.")
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        _fail("absolute paths and traversal are forbidden.")
    candidate = repo_root / rel
    root = repo_root / allowed_root
    if root.is_symlink():
        _fail("approved media/evidence root must not be a symlink.")
    try:
        resolved_root = root.resolve(strict=True)
        resolved = candidate.resolve(strict=True)
    except OSError:
        _fail("referenced asset/evidence file is missing.")
    current = candidate
    while current != repo_root and current != current.parent:
        if current.is_symlink():
            _fail("symlink path components are forbidden.")
        current = current.parent
    if not resolved.is_file() or not resolved.is_relative_to(resolved_root):
        _fail("file must be a regular file inside its fixed approved directory.")
    return resolved


def _https(value: object, field: str) -> str:
    if not isinstance(value, str):
        _fail(field + " must be an exact HTTPS URL.")
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        _fail(field + " must be an exact HTTPS URL.")
    return value


def _date(value: object, field: str) -> date:
    if not isinstance(value, str) or not value.strip():
        _fail(field + " is required.")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(value)
        except ValueError:
            _fail(field + " must be an ISO-8601 date/time.")
    raise AssertionError("unreachable")


def _validate_record(repo_root: Path, asset_ref: dict, planned_use: str) -> tuple[str, Path]:
    asset_id = asset_ref.get("asset_id")
    if not isinstance(asset_id, str) or not ASSET_ID.fullmatch(asset_id):
        _fail("manifest asset_id is unsafe or missing.")
    media_type = asset_ref.get("media_type")
    if media_type not in {"visual", "audio"}:
        _fail("manifest media_type must be visual or audio.")
    record_path = repo_root / RIGHTS_ROOT / (asset_id + ".json")
    if record_path.is_symlink() or not record_path.is_file():
        _fail("exact per-asset rights JSON record is missing.")
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        _fail("rights record is unreadable or malformed.")
    if not isinstance(record, dict) or type(record.get("schema_version")) is not int or record["schema_version"] != 1:
        _fail("unsupported rights-record schema.")
    if record.get("asset_id") != asset_id or record.get("media_type") != media_type:
        _fail("rights record does not match the manifest asset reference.")
    if record.get("decision") != "approved":
        _fail("asset has not received explicit human rights approval.")
    for field in ("creator_or_performer", "rights_owner", "source_platform", "license_name", "reviewer"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            _fail(field + " is required.")
    source_url = _https(record.get("source_page_url"), "source_page_url")
    downloaded = _date(record.get("downloaded_at"), "downloaded_at")
    reviewed = _date(record.get("reviewed_at"), "reviewed_at")
    if reviewed < downloaded:
        _fail("review date cannot precede download date.")
    if reviewed > datetime.now(timezone.utc).date():
        _fail("review date cannot be in the future.")
    digest = record.get("file_sha256")
    if not isinstance(digest, str) or not HASH.fullmatch(digest):
        _fail("file_sha256 must be lowercase SHA-256 hex.")
    asset_path = _safe_file(repo_root, record.get("file_path"), MEDIA_ROOT)
    actual = hashlib.sha256(asset_path.read_bytes()).hexdigest()
    if actual != digest:
        _fail("asset bytes do not match the approved SHA-256.")
    evidence = record.get("license_evidence")
    if not isinstance(evidence, dict) or evidence.get("kind") not in {"url", "file"}:
        _fail("exact license/permission evidence is required.")
    if evidence["kind"] == "url":
        _https(evidence.get("value"), "license_evidence.value")
    else:
        evidence_path = _safe_file(repo_root, evidence.get("value"), EVIDENCE_ROOT)
        evidence_hash = evidence.get("sha256")
        if not isinstance(evidence_hash, str) or not HASH.fullmatch(evidence_hash):
            _fail("saved license evidence requires a SHA-256 digest.")
        if hashlib.sha256(evidence_path.read_bytes()).hexdigest() != evidence_hash:
            _fail("saved license evidence hash mismatch.")
    uses = record.get("intended_uses")
    if not isinstance(uses, dict):
        _fail("explicit intended_uses permissions are required.")
    for field in USE_FIELDS[planned_use]:
        if uses.get(field) is not True:
            _fail("permission is missing for planned use: " + field + ".")
    territories = record.get("territories")
    if not isinstance(territories, list) or not territories or any(not isinstance(x, str) or not x.strip() for x in territories):
        _fail("permitted territories must be explicit.")
    validity = record.get("validity")
    if not isinstance(validity, dict):
        _fail("license validity scope is required.")
    start = _date(validity.get("start"), "validity.start")
    if start > datetime.now(timezone.utc).date():
        _fail("permission is not yet valid.")
    end_value = validity.get("end")
    if end_value is not None and _date(end_value, "validity.end") < datetime.now(timezone.utc).date():
        _fail("permission has expired.")
    attribution = record.get("attribution")
    if not isinstance(attribution, dict) or type(attribution.get("required")) is not bool:
        _fail("attribution requirement must be explicit.")
    if attribution["required"] and (not isinstance(attribution.get("text"), str) or not attribution["text"].strip()):
        _fail("required attribution wording is missing.")
    third = record.get("third_party_review")
    third_fields = ("people", "logos_trademarks", "artwork", "property_privacy", "endorsement")
    if not isinstance(third, dict):
        _fail("third_party_review is required.")
    for field in third_fields:
        item = third.get(field)
        if not isinstance(item, dict) or item.get("reviewed") is not True:
            _fail("third-party review is incomplete: " + field + ".")
        if item.get("resolved") is not True:
            _fail("third-party rights remain unresolved: " + field + ".")
    if media_type == "audio":
        if not isinstance(record.get("performer"), str) or not record["performer"].strip():
            _fail("audio performer must be identified separately.")
        if not isinstance(record.get("recording_owner"), str) or not record["recording_owner"].strip():
            _fail("audio recording owner must be identified.")
    # Source page is returned so callers can optionally compare it to manifest metadata.
    return source_url, asset_path


def validate_manifest_media_rights(data: dict, *, repo_root: Path,
                                   planned_use: str = "private_review") -> dict[str, Path]:
    """Validate every referenced media asset and return exact approved local paths."""
    if planned_use not in USE_FIELDS:
        _fail("unsupported planned-use profile.")
    if not isinstance(data, dict):
        _fail("manifest must be an object.")
    visual = data.get("visual")
    audio = data.get("audio")
    if not isinstance(visual, dict) or not isinstance(audio, dict):
        _fail("manifest visual/audio sections are required.")
    background = visual.get("background_candidate")
    if not isinstance(background, dict):
        _fail("manifest background candidate is required.")
    refs = [{"asset_id": background.get("asset_id"), "media_type": "visual"}]
    kind = audio.get("kind")
    if kind in {"spoken_dua", "ambient_nature"}:
        refs.append({"asset_id": audio.get("asset_id"), "media_type": "audio"})
    elif kind == "silent":
        if audio.get("asset_id") or audio.get("production_audio_file"):
            _fail("silent media must not declare an audio asset.")
    else:
        _fail("audio.kind must be explicit before rights validation.")
    declared = data.get("media_assets")
    if not isinstance(declared, list) or len(declared) != len(refs):
        _fail("media_assets must list exactly the visual and any required audio asset.")
    normalized = []
    for item in declared:
        if not isinstance(item, dict):
            _fail("each media_assets entry must be an object.")
        aid, media_type = item.get("asset_id"), item.get("media_type")
        if not isinstance(aid, str) or not ASSET_ID.fullmatch(aid) or media_type not in {"visual", "audio"}:
            _fail("each media_assets entry needs a safe asset_id and valid media_type.")
        normalized.append({"asset_id": aid, "media_type": media_type})
    if sorted((x["asset_id"], x["media_type"]) for x in normalized) != sorted((x["asset_id"], x["media_type"]) for x in refs):
        _fail("media_assets references do not exactly match visual/audio asset IDs.")
    root = repo_root.resolve(strict=True)
    result = {}
    for ref in refs:
        source_url, path = _validate_record(root, ref, planned_use)
        if ref["media_type"] == "visual":
            expected = background.get("source_url")
            if expected and expected != source_url:
                _fail("background source URL does not match its rights record.")
        result[ref["media_type"]] = path
    return result
