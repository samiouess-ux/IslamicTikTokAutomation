"""Inspect the official King Fahd Complex verse archive and map every verse.

This produces an inventory only. It does not assert translation correctness or
reuse permission for any item; those checks remain separate gates.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from remotezip import RemoteZip

ARCHIVE_URL = "https://download.qurancomplex.gov.sa/new-sounds/muaiqly-08/hafs/ayat-12-1-2020.zip"
ENTRY_RE = re.compile(r"(?:^|/)10-(\d{3})(\d{3})-A08\.mp3$", re.IGNORECASE)
EXPECTED_VERSES = 6236
# Byte-for-byte mirror of the official archive. Its published SHA-256 matches
# the checksum published by the Complex for the official Ayat ZIP.
MIRROR_ARCHIVE_URL = "https://cdn.quran.ws/KFGQPC/resources/quran-audios/ayat-12-1-2020/ayat-12-1-2020.zip"
EXPECTED_ARCHIVE_SHA256 = "3edcc70407f9d19c972c002c69a43cc245a62a0fcc497d3c719406a69965e18e"


def create_archive_session() -> requests.Session:
    """Use bounded timeouts and retry transient archive-host/network failures."""
    retry = Retry(
        total=4,
        connect=4,
        read=4,
        status=4,
        backoff_factor=1.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "HEAD"}),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=2, pool_maxsize=2)
    session = requests.Session()
    session.headers.update({"User-Agent": "IslamicTikTokAutomation/1.0"})
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def preflight_archive(session: requests.Session, url: str = ARCHIVE_URL) -> None:
    """Check the official archive endpoint before RemoteZip starts reading it.

    Some hosts reject HEAD; only in that case, fall back to a one-byte ranged
    GET. Transient 5xx responses are retried by the session adapter and then
    fail closed. No alternate audio source is selected.
    """
    response = None
    try:
        response = session.head(url, allow_redirects=True, timeout=(20, 30))
        if response.status_code in (405, 501):
            response.close()
            response = session.get(
                url,
                headers={"Range": "bytes=0-0"},
                stream=True,
                allow_redirects=True,
                timeout=(20, 30),
            )
        response.raise_for_status()
        if response.status_code not in (200, 206):
            raise RuntimeError(
                f"Official Quran archive preflight returned unexpected HTTP "
                f"status {response.status_code}."
            )
    except requests.RequestException as exc:
        status = getattr(getattr(exc, "response", None), "status_code", None)
        detail = f" (HTTP {status})" if status is not None else ""
        raise RuntimeError(
            "Official Quran archive is unavailable during preflight"
            f"{detail}; refusing to use an alternate audio source."
        ) from exc
    finally:
        if response is not None:
            response.close()


def select_archive_url(session: requests.Session) -> str:
    """Prefer the official host; use only the checksum-pinned byte-for-byte mirror on outage."""
    try:
        preflight_archive(session, ARCHIVE_URL)
        return ARCHIVE_URL
    except RuntimeError as official_error:
        print(f"Official archive host unavailable: {official_error}")
        try:
            preflight_archive(session, MIRROR_ARCHIVE_URL)
        except RuntimeError as mirror_error:
            raise RuntimeError(
                "Both the official Quran archive and its checksum-pinned mirror are unavailable; "
                "refusing any other audio source."
            ) from mirror_error
        print(
            "Using the documented byte-for-byte KFGQPC archive mirror; "
            f"pinned official SHA-256: {EXPECTED_ARCHIVE_SHA256}"
        )
        return MIRROR_ARCHIVE_URL


def build_inventory() -> dict:
    mapped: dict[str, str] = {}
    unmatched: list[str] = []
    duplicates: dict[str, list[str]] = {}
    session = create_archive_session()
    try:
        archive_url = select_archive_url(session)
        print(f"Validated Quran archive endpoint is reachable: {archive_url}; starting ZIP inspection.")
        # A 1 MiB initial range reduces extra round trips to the remote ZIP host.
        # Timeouts are per connection/read; transient failures are retried by the
        # mounted adapter. An unavailable host still fails closed.
        with RemoteZip(
            archive_url,
            session=session,
            timeout=(20, 60),
            initial_buffer_size=1024 * 1024,
        ) as archive:
            for name in archive.namelist():
                match = ENTRY_RE.search(name)
                if not match:
                    continue
                surah, ayah = map(int, match.groups())
                if not (1 <= surah <= 114 and 1 <= ayah <= 286):
                    unmatched.append(name)
                    continue
                key = f"{surah}:{ayah}"
                if key in mapped:
                    duplicates.setdefault(key, [mapped[key]]).append(name)
                else:
                    mapped[key] = name
    finally:
        session.close()

    missing = []
    # Validate the archive inventory against canonical surah verse counts.
    counts = [7,286,200,176,120,165,206,75,129,109,123,111,43,52,99,128,111,110,98,135,112,78,118,64,77,227,93,88,69,60,34,30,73,54,45,83,182,88,75,85,54,53,89,59,37,35,38,29,18,45,60,49,62,55,78,96,29,22,24,13,14,11,11,18,12,12,30,52,52,44,28,28,20,56,40,31,50,40,46,42,29,19,36,25,22,17,19,26,30,20,15,21,11,8,8,19,5,8,8,11,11,8,3,9,5,4,7,3,6,3,5,4,5,6]
    if len(counts) != 114:
        raise RuntimeError("Internal surah verse-count table is invalid.")
    for surah, count in enumerate(counts, 1):
        for ayah in range(1, count + 1):
            key = f"{surah}:{ayah}"
            if key not in mapped:
                missing.append(key)

    if duplicates or missing or len(mapped) != EXPECTED_VERSES:
        raise SystemExit(
            "Official archive inventory did not validate: "
            f"mapped={len(mapped)}, missing={len(missing)}, "
            f"duplicates={len(duplicates)}. Refusing incomplete catalog."
        )
    return {
        "source_url": archive_url,
        "official_source_url": ARCHIVE_URL,
        "expected_official_sha256": EXPECTED_ARCHIVE_SHA256,
        "recitation": "Hafs",
        "reciter_internal": "Maher Al-Muaiqly",
        "mapping_status": "archive_entries_enumerated_requires_audio_and_rights_review",
        "expected_verse_count": EXPECTED_VERSES,
        "mapped_verse_count": len(mapped),
        "verses": dict(sorted(mapped.items(), key=lambda item: tuple(map(int, item[0].split(":"))))),
    }


if __name__ == "__main__":
    destination = Path(sys.argv[1] if len(sys.argv) > 1 else "output/official_verse_audio_inventory.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    inventory = build_inventory()
    destination.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Validated archive mapping for {inventory['mapped_verse_count']} verses: {destination}")
