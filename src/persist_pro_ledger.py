"""Persist only the Pro delivery ledger using normal Git checkout/commit/push."""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

EXPECTED_BRANCH = "feature/quran-video-pro"
LEDGER_RELATIVE_PATH = Path("data/pro_delivery_ledger.json")


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True, check=False
    )
    if result.returncode != 0:
        # Git diagnostics and arguments may contain credential-bearing remote URLs.
        raise RuntimeError(f"Git operation failed (exit code {result.returncode}).") from None
    return result.stdout.strip()


def _require_remote_head_match(repo: Path, phase: str) -> None:
    _git(
        repo, "fetch", "origin",
        f"refs/heads/{EXPECTED_BRANCH}:refs/remotes/origin/{EXPECTED_BRANCH}",
    )
    local_head = _git(repo, "rev-parse", "HEAD")
    remote_head = _git(repo, "rev-parse", f"refs/remotes/origin/{EXPECTED_BRANCH}")
    if local_head != remote_head:
        raise RuntimeError(
            f"Local Pro branch is not aligned with origin {phase}; refusing ledger persistence."
        )


def persist_ledger(repo: Path) -> bool:
    """Commit/push the ledger only, refusing stale branches and unverified pushes."""
    repo = repo.resolve()
    branch = _git(repo, "branch", "--show-current")
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(
            f"Refusing ledger persistence on branch {branch!r}; expected {EXPECTED_BRANCH!r}."
        )

    _require_remote_head_match(repo, "before write")

    # Do not accidentally absorb unrelated staged work into the ledger commit.
    staged_before = _git(repo, "diff", "--cached", "--name-only")
    if staged_before:
        raise RuntimeError("Refusing persistence because unrelated staged changes already exist.")

    data_dir = repo / LEDGER_RELATIVE_PATH.parent
    ledger_path = repo / LEDGER_RELATIVE_PATH
    lock_path = ledger_path.with_name(ledger_path.name + ".lock")

    # Reject links in every path component below the resolved repository root.
    # Checking only the leaf misses a symlinked ancestor that redirects writes.
    for path in (data_dir, ledger_path, lock_path):
        current = path
        while current != repo and current != current.parent:
            if current.is_symlink():
                raise RuntimeError("Pro ledger storage paths must not contain symlinks.")
            current = current.parent
    if not ledger_path.is_file():
        raise FileNotFoundError("Pro ledger file is missing.")

    _git(repo, "add", "--", str(LEDGER_RELATIVE_PATH))
    staged = _git(repo, "diff", "--cached", "--name-only").splitlines()
    if not staged:
        return False
    if staged != [str(LEDGER_RELATIVE_PATH)]:
        raise RuntimeError(f"Refusing to commit unexpected staged paths: {staged!r}")

    _git(repo, "commit", "-m", "chore(pro): persist delivery ledger")
    _git(repo, "push", "origin", f"HEAD:refs/heads/{EXPECTED_BRANCH}")
    _require_remote_head_match(repo, "after push")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path("."))
    args = parser.parse_args()
    changed = persist_ledger(args.repo)
    print("Pro ledger committed and verified." if changed else "Pro ledger unchanged; no commit needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
