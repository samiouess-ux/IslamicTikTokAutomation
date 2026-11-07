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
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def persist_ledger(repo: Path) -> bool:
    """Commit/push the ledger only. Return False when there is nothing to commit."""
    repo = repo.resolve()
    branch = _git(repo, "branch", "--show-current")
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(
            f"Refusing ledger persistence on branch {branch!r}; expected {EXPECTED_BRANCH!r}."
        )

    # Do not accidentally absorb unrelated staged work into the ledger commit.
    staged_before = _git(repo, "diff", "--cached", "--name-only")
    if staged_before:
        raise RuntimeError("Refusing persistence because unrelated staged changes already exist.")

    data_dir = repo / LEDGER_RELATIVE_PATH.parent
    if data_dir.is_symlink():
        raise RuntimeError("Pro ledger data directory must not be a symlink.")
    ledger_path = repo / LEDGER_RELATIVE_PATH
    if ledger_path.is_symlink():
        raise RuntimeError("Pro ledger file must not be a symlink.")
    if not ledger_path.is_file():
        raise FileNotFoundError(f"Pro ledger file is missing: {ledger_path}")

    _git(repo, "add", "--", str(LEDGER_RELATIVE_PATH))
    staged = _git(repo, "diff", "--cached", "--name-only").splitlines()
    if not staged:
        return False
    if staged != [str(LEDGER_RELATIVE_PATH)]:
        raise RuntimeError(f"Refusing to commit unexpected staged paths: {staged!r}")

    _git(repo, "commit", "-m", "chore(pro): persist delivery ledger")
    _git(repo, "push", "origin", f"HEAD:refs/heads/{EXPECTED_BRANCH}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path("."))
    args = parser.parse_args()
    changed = persist_ledger(args.repo)
    print("Pro ledger committed and pushed." if changed else "Pro ledger unchanged; no commit needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
