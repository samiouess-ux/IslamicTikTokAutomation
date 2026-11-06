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

    def test_refuses_wrong_branch_before_staging(self):
        with self.run_git([(0, "main\n", ""),]):
            with self.assertRaisesRegex(RuntimeError, "expected"):
                persist_ledger(self.repo)

    def test_refuses_preexisting_staged_changes(self):
        with self.run_git([(0, EXPECTED_BRANCH, ""), (0, "README.md\n", "")]):
            with self.assertRaisesRegex(RuntimeError, "staged changes"):
                persist_ledger(self.repo)

    def test_commits_only_ledger_then_pushes_exact_branch(self):
        outputs = [
            (0, EXPECTED_BRANCH, ""),  # branch
            (0, "", ""),               # pre-existing staged paths
            (0, "", ""),               # git add
            (0, "data/pro_delivery_ledger.json\n", ""),  # staged paths
            (0, "[commit] saved", ""), # commit
            (0, "pushed", ""),         # push
        ]
        with self.run_git(outputs) as patched:
            self.assertTrue(persist_ledger(self.repo))
        commands = [call.args[0] for call in patched.call_args_list]
        self.assertEqual(commands[-1], [
            "git", "push", "origin", f"HEAD:refs/heads/{EXPECTED_BRANCH}"
        ])
        self.assertIn(["git", "add", "--", "data/pro_delivery_ledger.json"], commands)

    def test_refuses_unrelated_staged_path_after_add(self):
        outputs = [
            (0, EXPECTED_BRANCH, ""), (0, "", ""), (0, "", ""),
            (0, "data/pro_delivery_ledger.json\nREADME.md\n", ""),
        ]
        with self.run_git(outputs):
            with self.assertRaisesRegex(RuntimeError, "unexpected staged paths"):
                persist_ledger(self.repo)


if __name__ == "__main__":
    unittest.main()
