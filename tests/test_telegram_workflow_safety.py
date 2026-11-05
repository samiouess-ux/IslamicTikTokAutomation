import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "build-quran-audio-inventory.yml"


class TelegramWorkflowSafetyContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_reservation_is_committed_before_telegram_send(self):
        reserve = self.text.index("- name: Reserve Telegram delivery attempt before sending")
        send = self.text.index("- name: Send one review-only video to Telegram for manual approval")
        self.assertLess(reserve, send)
        reserve_block = self.text[reserve:send]
        self.assertIn("quran_delivery_attempt.py reserve", reserve_block)
        self.assertIn("git add data/quran_delivery_pending.json", reserve_block)
        self.assertIn("git push origin HEAD:refs/heads/feature/telegram-review-notifications", reserve_block)

    def test_confirmed_delivery_finalizes_history_after_sender_success(self):
        send = self.text.index("- name: Send one review-only video to Telegram for manual approval")
        finalize = self.text.index("- name: Record Telegram-confirmed Quran delivery history")
        sync = self.text.index("- name: Sync confirmed Quran delivery history to active branch")
        self.assertLess(send, finalize)
        self.assertLess(finalize, sync)
        finalize_block = self.text[finalize:sync]
        self.assertIn("quran_delivery_attempt.py", finalize_block)
        self.assertIn("finalize", finalize_block)
        self.assertIn("git add -A data/quran_delivery_history.json data/quran_delivery_pending.json", finalize_block)

    def test_unresolved_reservation_guard_runs_before_automatic_send(self):
        guard = self.text.index("- name: Block automatic sends when a previous Telegram outcome is unresolved")
        setup = self.text.index("- uses: actions/setup-python@v5")
        send = self.text.index("- name: Send one review-only video to Telegram for manual approval")
        self.assertLess(guard, setup)
        self.assertLess(guard, send)
        guard_block = self.text[guard:setup]
        self.assertIn("quran_delivery_attempt.py guard", guard_block)
        self.assertIn("data/quran_delivery_pending.json", guard_block)


    def test_test_now_dispatch_is_explicit_and_defaults_to_production_safe_false(self):
        dispatch = self.text[self.text.index("  workflow_dispatch:"):self.text.index("\npermissions:")]
        self.assertIn("test_only:", dispatch)
        self.assertIn("default: false", dispatch)
        self.assertIn("type: boolean", dispatch)

    def test_test_now_skips_production_reservation_and_history(self):
        guard = self.text[self.text.index("- name: Block automatic sends"):self.text.index("- uses: actions/setup-python")]
        reserve = self.text[self.text.index("- name: Reserve Telegram delivery"):self.text.index("- name: Send one review-only video")]
        finalize = self.text[self.text.index("- name: Record Telegram-confirmed"):self.text.index("- name: Sync confirmed")]
        sync = self.text[self.text.index("- name: Sync confirmed"):self.text.index("- name: Notify Telegram")]
        for block in (guard, reserve, finalize, sync):
            self.assertIn("inputs.test_only != true", block)

    def test_test_now_still_sends_review_video_to_telegram(self):
        send = self.text[self.text.index("- name: Send one review-only video"):self.text.index("- name: Record Telegram-confirmed")]
        self.assertIn("github.event_name == 'workflow_dispatch'", send)
        self.assertIn("src/send_telegram.py", send)
        self.assertIn("auto_publish", send)

    def test_telegram_send_is_review_only_and_never_tiktok_publish(self):
        send = self.text.index("- name: Send one review-only video to Telegram for manual approval")
        finalize = self.text.index("- name: Record Telegram-confirmed Quran delivery history")
        send_block = self.text[send:finalize]
        self.assertIn("src/send_telegram.py", send_block)
        self.assertIn("auto_publish", send_block)
        self.assertIn("TikTok publishing remains manual", send_block)


    def test_manual_telegram_send_requires_explicit_approval_and_not_test_mode(self):
        dispatch = self.text[self.text.index("  workflow_dispatch:"):self.text.index("\\npermissions:")]
        self.assertIn("send_to_telegram:", dispatch)
        self.assertIn("default: false", dispatch)
        send = self.text[self.text.index("- name: Send one review-only video to Telegram"):self.text.index("- name: Record Telegram-confirmed")]
        self.assertIn("inputs.test_only != true", send)
        self.assertIn("inputs.send_to_telegram == true", send)

    def test_test_now_description_promises_no_telegram_delivery(self):
        dispatch = self.text[self.text.index("  workflow_dispatch:"):self.text.index("\\npermissions:")]
        self.assertIn("TEST NOW: render a review-only preview; never send Telegram", dispatch)


if __name__ == "__main__":
    unittest.main()
