"""Resolve a direct Mixkit MP4 URL from an exact Mixkit item page.

The page URL is supplied by the user/researcher; no guessed asset URL is used.
Only assets.mixkit.co HTTPS MP4 URLs are accepted.
"""
from __future__ import annotations

import argparse
import re
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path
import subprocess
import sys

HOST = "assets.mixkit.co"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-page", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--output-dir", default="background_inspection")
    args = parser.parse_args()

    page = urllib.parse.urlparse(args.source_page)
    if page.scheme != "https" or page.hostname != "mixkit.co" or "/free-stock-video/" not in page.path:
        raise SystemExit("Provide an exact HTTPS Mixkit stock-video item page.")

    req = urllib.request.Request(args.source_page, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        html = response.read(5_000_000).decode("utf-8", errors="replace")

    candidates = set()
    for raw in re.findall(r"""https?:\\?/\\?/[^"'\\s<>]+?\\.mp4(?:\\?[^"'\\s<>]*)?""", html):
        url = unescape(raw).replace("\\/", "/")
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme == "https" and parsed.hostname == HOST and parsed.path.lower().endswith(".mp4"):
            candidates.add(url)

    if not candidates:
        # Extract JSON-escaped URL variants, then validate host and extension.
        for raw in re.findall(r"""https[^"\\s<>]+""", html):
            url = unescape(raw).replace("\\/", "/").replace("\\u0026", "&")
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme == "https" and parsed.hostname == HOST and parsed.path.lower().endswith(".mp4"):
                candidates.add(url)

    if not candidates:
        raise SystemExit("No direct Mixkit MP4 URL found in the item page HTML; refusing to guess.")

    # Prefer full-resolution 1080 variants when the page exposes more than one.
    ordered = sorted(candidates, key=lambda u: ("1080" not in u and "1920" not in u, len(u)))
    url = ordered[0]
    print(f"Resolved official asset URL: {url}")

    cmd = [
        sys.executable, "src/inspect_background.py",
        "--title", args.title,
        "--source-page", args.source_page,
        "--url", url,
        "--output-dir", args.output_dir,
    ]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
