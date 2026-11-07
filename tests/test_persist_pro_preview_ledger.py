"""Offline tests for exact-branch preview ledger persistence."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from persist_pro_preview_ledger import persist_preview_ledger, EXPECTED_BRANCH, _git


class PreviewLedgerPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        ledger = self.repo / "data" / "pro_preview_send_ledger.json"
        ledger.parent.mkdir()
        ledger.write_text('{"version":1,"entries":{}}\n', encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def run_git(self, outputs):
        def fake_run(command, **kwargs):
            result = outputs.pop(0)
            return mock.Mock(returncode=result[0], stdout=result[1], stderr=result[2])
        return mock.patch("persist_pro_preview_ledger.subprocess.run", side_effect=fake_run)

    def test_git_failure_diagnostics_do_not_leak_remote_credentials(self):
        failure = mock.Mock(returncode=128, stdout="",
            stderr="fatal: https://user:SECRET-TOKEN@github.com/owner/repo.git denied")
        with mock.patch("persist_pro_preview_ledger.subprocess.run", return_value=failure):
            with self.assertRaisesRegex(RuntimeError, "Git operation failed") as caught:
                _git(self.repo, "fetch", "origin", "refs/heads/feature/quran-video-pro")
        self.assertNotIn("SECRET-TOKEN", str(caught.exception))
        self.assertNotIn("github.com", str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)

    def test_wrong_branch_stops_before_fetch_or_add(self):
        with self.run_git([(0, "main\n", "")]) as patched:
            with self.assertRaisesRegex(RuntimeError, "expected"):
                persist_preview_ledger(self.repo)
        self.assertEqual(patched.call_count, 1)

    def test_stale_local_branch_stops_before_staging(self):
        outputs = [(0, EXPECTED_BRANCH, ""), (0, "", ""), (0, "local", ""), (0, "remote", "")]
        with self.run_git(outputs) as patched:
            with self.assertRaisesRegex(RuntimeError, "not up to date"):
                persist_preview_ledger(self.repo)
        self.assertEqual(patched.call_count, 4)

    def test_commits_only_preview_ledger_and_verifies_remote_head(self):
        outputs = [
            (0, EXPECTED_BRANCH, ""), (0, "", ""), (0, "same", ""), (0, "same", ""),
            (0, "", ""), (0, "", ""), (0, "data/pro_preview_send_ledger.json\n", ""),
            (0, "[commit]", ""), (0, "pushed", ""), (0, "", ""),
            (0, "same-new", ""), (0, "same-new", ""),
        ]
        with self.run_git(outputs) as patched:
            self.assertTrue(persist_preview_ledger(self.repo))
        commands = [call.args[0] for call in patched.call_args_list]
        self.assertIn(["git", "add", "--", "data/pro_preview_send_ledger.json"], commands)
        self.assertEqual(commands[-2], ["git", "rev-parse", "HEAD"])
        self.assertEqual(commands[-1], ["git", "rev-parse", "refs/remotes/origin/feature/quran-video-pro"])

    def test_unchanged_preview_ledger_is_a_clean_noop(self):
        outputs = [
            (0, EXPECTED_BRANCH, ""), (0, "", ""), (0, "same", ""), (0, "same", ""),
            (0, "", ""), (0, "", ""), (0, "", ""),
        ]
        with self.run_git(outputs) as patched:
            self.assertFalse(persist_preview_ledger(self.repo))
        self.assertEqual(patched.call_count, 7)
        commands = [call.args[0] for call in patched.call_args_list]
        self.assertIn(["git", "add", "--", "data/pro_preview_send_ledger.json"], commands)
        self.assertFalse(any(command[1] in {"commit", "push"} for command in commands))

    def test_symlinked_data_directory_is_rejected_before_staging(self):
        data_dir = self.repo / "data"
        real_dir = self.repo / "real-data"
        data_dir.rename(real_dir)
        try:
            data_dir.symlink_to(real_dir, target_is_directory=True)
        except (OSError, NotImplementedError):
            real_dir.rename(data_dir)
            self.skipTest("Symlinks are unavailable on this platform.")
        outputs = [(0, EXPECTED_BRANCH, ""), (0, "", ""), (0, "same", ""),
                   (0, "same", ""), (0, "", "")]
        with self.run_git(outputs) as patched:
            with self.assertRaisesRegex(RuntimeError, "data directory must not be a symlink"):
                persist_preview_ledger(self.repo)
        self.assertEqual(patched.call_count, 5)

    def test_symlinked_lock_file_is_rejected_before_staging(self):
        ledger = self.repo / "data" / "pro_preview_send_ledger.json"
        lock = ledger.with_name(ledger.name + ".lock")
        target = self.repo / "outside.lock"
        target.write_text("unchanged", encoding="utf-8")
        try:
            lock.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks are unavailable on this platform.")
        outputs = [(0, EXPECTED_BRANCH, ""), (0, "", ""), (0, "same", ""),
                   (0, "same", ""), (0, "", "")]
        with self.run_git(outputs) as patched:
            with self.assertRaisesRegex(RuntimeError, "lock file must not be a symlink"):
                persist_preview_ledger(self.repo)
        self.assertEqual(patched.call_count, 5)
        self.assertEqual(target.read_text(encoding="utf-8"), "unchanged")

    def test_unrelated_staged_path_is_rejected(self):
        outputs = [(0, EXPECTED_BRANCH, ""), (0, "", ""), (0, "same", ""), (0, "same", ""),
                   (0, "", ""), (0, "", ""), (0, "data/pro_preview_send_ledger.json\nREADME.md\n", "")]
        with self.run_git(outputs):
            with self.assertRaisesRegex(RuntimeError, "unexpected staged paths"):
                persist_preview_ledger(self.repo)


if __name__ == "__main__":
    unittest.main()
