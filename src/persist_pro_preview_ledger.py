"""Persist only the isolated Pro preview-send ledger to its exact branch."""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

EXPECTED_BRANCH = "feature/quran-video-pro"
LEDGER_RELATIVE_PATH = Path("data/pro_preview_send_ledger.json")


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def persist_preview_ledger(repo: Path) -> bool:
    repo = repo.resolve()
    branch = _git(repo, "branch", "--show-current")
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(f"Refusing preview ledger persistence: expected {EXPECTED_BRANCH}, got {branch!r}.")
    _git(repo, "fetch", "origin", f"refs/heads/{EXPECTED_BRANCH}:refs/remotes/origin/{EXPECTED_BRANCH}")
    local_head = _git(repo, "rev-parse", "HEAD")
    remote_head = _git(repo, "rev-parse", f"refs/remotes/origin/{EXPECTED_BRANCH}")
    if local_head != remote_head:
        raise RuntimeError("Local Pro branch is not up to date with origin; refusing preview ledger write.")
    staged = _git(repo, "diff", "--cached", "--name-only")
    if staged:
        raise RuntimeError(f"Refusing preview ledger persistence with pre-existing staged changes: {staged}")
    ledger = repo / LEDGER_RELATIVE_PATH
    if not ledger.is_file() or ledger.is_symlink():
        raise RuntimeError("Pro preview ledger must exist as a regular, non-symlink file.")
    _git(repo, "add", "--", LEDGER_RELATIVE_PATH.as_posix())
    staged_after = _git(repo, "diff", "--cached", "--name-only")
    if staged_after.splitlines() != [LEDGER_RELATIVE_PATH.as_posix()]:
        raise RuntimeError(f"Refusing preview ledger commit; unexpected staged paths: {staged_after}")
    changed = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo,
                             text=True, capture_output=True, check=False)
    if changed.returncode == 0:
        _git(repo, "reset", "--", LEDGER_RELATIVE_PATH.as_posix())
        return False
    if changed.returncode != 1:
        raise RuntimeError("Could not determine whether the preview ledger changed.")
    _git(repo, "commit", "-m", "chore(pro): persist preview-send ledger")
    _git(repo, "push", "origin", f"HEAD:refs/heads/{EXPECTED_BRANCH}")
    _git(repo, "fetch", "origin", f"refs/heads/{EXPECTED_BRANCH}:refs/remotes/origin/{EXPECTED_BRANCH}")
    committed_head = _git(repo, "rev-parse", "HEAD")
    verified_remote = _git(repo, "rev-parse", f"refs/remotes/origin/{EXPECTED_BRANCH}")
    if committed_head != verified_remote:
        raise RuntimeError("Remote Pro branch does not match the preview-ledger commit after push.")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Persist only the Pro preview-send ledger.")
    parser.add_argument("--repo", type=Path, default=Path("."))
    args = parser.parse_args()
    changed = persist_preview_ledger(args.repo)
    print("Pro preview ledger committed and verified." if changed else "Pro preview ledger unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
