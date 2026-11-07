"""Offline tests for the Pro ledger-only Git persistence helper."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from persist_pro_ledger import persist_ledger, EXPECTED_BRANCH


class ProLedgerPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        ledger = self.repo / "data" / "pro_delivery_ledger.json"
        ledger.parent.mkdir()
        ledger.write_text('{"version":1,"entries":{}}\n', encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def run_git(self, outputs):
        def fake_run(command, **kwargs):
            result = outputs.pop(0)
            return mock.Mock(returncode=result[0], stdout=result[1], stderr=result[2])
        return mock.patch("persist_pro_ledger.subprocess.run", side_effect=fake_run)

    def aligned_prefix(self):
        return [
            (0, EXPECTED_BRANCH, ""),  # branch
            (0, "", ""),               # fetch origin
            (0, "same-head", ""),      # local HEAD
            (0, "same-head", ""),      # origin tracking HEAD
        ]

    def test_refuses_wrong_branch_before_fetch_or_staging(self):
        with self.run_git([(0, "main\n", "")]):
            with self.assertRaisesRegex(RuntimeError, "expected"):
                persist_ledger(self.repo)

    def test_refuses_stale_local_branch_before_staging(self):
        outputs = [
            (0, EXPECTED_BRANCH, ""), (0, "", ""),
            (0, "local-old", ""), (0, "remote-new", ""),
        ]
        with self.run_git(outputs) as patched:
            with self.assertRaisesRegex(RuntimeError, "not aligned"):
                persist_ledger(self.repo)
        self.assertEqual(len(patched.call_args_list), 4)

    def test_refuses_preexisting_staged_changes(self):
        outputs = self.aligned_prefix() + [(0, "README.md\n", "")]
        with self.run_git(outputs):
            with self.assertRaisesRegex(RuntimeError, "staged changes"):
                persist_ledger(self.repo)

    def test_unchanged_production_ledger_is_a_clean_noop(self):
        outputs = self.aligned_prefix() + [
            (0, "", ""),  # pre-existing staged paths
            (0, "", ""),  # git add
            (0, "", ""),  # no staged paths: unchanged ledger
        ]
        with self.run_git(outputs) as patched:
            self.assertFalse(persist_ledger(self.repo))
        self.assertEqual(len(patched.call_args_list), 7)
        commands = [call.args[0] for call in patched.call_args_list]
        self.assertIn(["git", "add", "--", "data/pro_delivery_ledger.json"], commands)
        self.assertFalse(any(command[1] in {"commit", "push"} for command in commands))

    def test_commits_only_ledger_and_verifies_exact_remote_head(self):
        outputs = self.aligned_prefix() + [
            (0, "", ""),  # pre-existing staged paths
            (0, "", ""),  # git add
            (0, "data/pro_delivery_ledger.json\n", ""),  # staged paths
            (0, "[commit] saved", ""),  # commit
            (0, "pushed", ""),  # push
            (0, "", ""),  # post-push fetch
            (0, "new-head", ""),  # local HEAD
            (0, "new-head", ""),  # origin tracking HEAD
        ]
        with self.run_git(outputs) as patched:
            self.assertTrue(persist_ledger(self.repo))
        commands = [call.args[0] for call in patched.call_args_list]
        self.assertEqual(commands[-4], [
            "git", "push", "origin", f"HEAD:refs/heads/{EXPECTED_BRANCH}"
        ])
        self.assertIn(["git", "add", "--", "data/pro_delivery_ledger.json"], commands)
        self.assertEqual(len(commands), 12)

    def test_post_push_remote_mismatch_is_not_reported_as_success(self):
        outputs = self.aligned_prefix() + [
            (0, "", ""), (0, "", ""),
            (0, "data/pro_delivery_ledger.json\n", ""),
            (0, "[commit] saved", ""), (0, "pushed", ""),
            (0, "", ""), (0, "local-new", ""), (0, "remote-other", ""),
        ]
        with self.run_git(outputs):
            with self.assertRaisesRegex(RuntimeError, "not aligned with origin after push"):
                persist_ledger(self.repo)

    def test_push_failure_raises_and_never_reports_persistence_success(self):
        outputs = self.aligned_prefix() + [
            (0, "", ""), (0, "", ""),
            (0, "data/pro_delivery_ledger.json\n", ""),
            (0, "[commit] saved", ""),
            (1, "", "remote rejected push"),
        ]
        with self.run_git(outputs) as patched:
            with self.assertRaisesRegex(RuntimeError, "Git operation failed") as caught:
                persist_ledger(self.repo)
        self.assertNotIn("remote rejected push", str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)
        commands = [call.args[0] for call in patched.call_args_list]
        self.assertEqual(commands[-1], [
            "git", "push", "origin", f"HEAD:refs/heads/{EXPECTED_BRANCH}"
        ])

    def test_git_failure_redacts_credential_bearing_remote_diagnostics(self):
        secret = "GITHUB_REMOTE_TOKEN_SECRET"
        outputs = self.aligned_prefix() + [
            (0, "", ""), (0, "", ""),
            (0, "data/pro_delivery_ledger.json\n", ""),
            (0, "[commit] saved", ""),
            (1, "", f"remote rejected https://{secret}@github.com/owner/repo"),
        ]
        with self.run_git(outputs):
            with self.assertRaisesRegex(RuntimeError, "Git operation failed") as caught:
                persist_ledger(self.repo)
        self.assertNotIn(secret, str(caught.exception))
        self.assertNotIn("github.com", str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)

    def test_refuses_symlinked_ledger_file(self):
        ledger = self.repo / "data" / "pro_delivery_ledger.json"
        target = self.repo / "outside.json"
        target.write_text('{"version":1,"entries":{}}', encoding="utf-8")
        ledger.unlink()
        ledger.symlink_to(target)
        outputs = self.aligned_prefix() + [(0, "", "")]
        with self.run_git(outputs):
            with self.assertRaisesRegex(RuntimeError, "storage paths must not contain symlinks"):
                persist_ledger(self.repo)

    def test_refuses_symlinked_ledger_lock_file(self):
        ledger = self.repo / "data" / "pro_delivery_ledger.json"
        lock = ledger.with_name(ledger.name + ".lock")
        target = self.repo / "outside.lock"
        target.write_text("unchanged", encoding="utf-8")
        try:
            lock.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks are unavailable on this platform.")
        outputs = self.aligned_prefix() + [(0, "", "")]
        with self.run_git(outputs) as patched:
            with self.assertRaisesRegex(RuntimeError, "storage paths must not contain symlinks"):
                persist_ledger(self.repo)
        self.assertEqual(patched.call_count, 5)
        self.assertEqual(target.read_text(encoding="utf-8"), "unchanged")

    def test_refuses_symlinked_data_directory(self):
        data = self.repo / "data"
        ledger = data / "pro_delivery_ledger.json"
        ledger.unlink()
        data.rmdir()
        outside = self.repo / "outside"
        outside.mkdir()
        (outside / "pro_delivery_ledger.json").write_text(
            '{"version":1,"entries":{}}', encoding="utf-8"
        )
        data.symlink_to(outside, target_is_directory=True)
        outputs = self.aligned_prefix() + [(0, "", "")]
        with self.run_git(outputs):
            with self.assertRaisesRegex(RuntimeError, "storage paths must not contain symlinks"):
                persist_ledger(self.repo)

    def test_refuses_unrelated_staged_path_after_add(self):
        outputs = self.aligned_prefix() + [
            (0, "", ""), (0, "", ""),
            (0, "data/pro_delivery_ledger.json\nREADME.md\n", ""),
        ]
        with self.run_git(outputs):
            with self.assertRaisesRegex(RuntimeError, "unexpected staged paths"):
                persist_ledger(self.repo)


if __name__ == "__main__":
    unittest.main()
