# Agent work plan — IslamicTikTokAutomation

Last updated: 2026-11-01

## Telegram delivery confirmation hardening (2026-11-01)
- Sender now requires both Telegram API `ok: true` and a positive integer `message_id`; otherwise it exits unsuccessfully and delivery history is not recorded.
- Added a regression test for the missing-message-ID response.
- Commits: `6b159c9f4703fb52f6998a8de62fe4206a0fe91b` (sender), `eb4a6d1b585023bfee08014e83147f9e48083cfd` (test).
- Real Telegram MP4 delivery is still unverified; this hardening is not evidence of a successful send.

## Operating rules

- Repository: `samiouess-ux/IslamicTikTokAutomation`.
- Work only on `feature/telegram-review-notifications`. Never modify `main`.
- Use the existing GitHub Actions workflow and the original Telegram bot. Do not create another bot, webhook, Cloudflare Worker, KV store, or cloud service.
- TikTok publishing is manual only. The engine prepares and sends review MP4s to Telegram; the user downloads and publishes manually.
- Do not ask the user to perform routine technical steps. Inspect, implement, test, and report from the connected repository tools where possible.
- Never describe a build, artifact upload, mocked unit test, or green push run as successful Telegram delivery.
- Record a passage in delivery history only after Telegram API returns `ok: true`.

## Agent roles

These are the project's assigned work/review roles, not separately billed cloud agents.

### Agent 1 — Quran content and source integrity
- Validate exact surah/ayah references, Uthmani Arabic strings, translation pairing, and official audio archive mapping.
- Select different surahs/passages; exclude previously delivered ayahs using `data/quran_delivery_history.json`.
- Keep each passage contiguous and at or below 65 seconds. Never cut an ayah, speed up recitation, or invent religious text.
- Fail closed on missing or mismatched source data.

### Agent 2 — Audio and video production
- Reuse the existing renderer and approved visual reference; do not rebuild the prototype.
- Check vertical 9:16 output, readable Arabic, smaller paired translation, correct surah title and ayah numbers, no music, and stable backgrounds.
- Keep review previews distinct from production-approved videos. Do not silently treat an unreviewed source candidate as fully approved.

### Agent 3 — Telegram delivery
- Use the existing `src/send_telegram.py`, `TG_BOT_TOKEN`, and `TELEGRAM_CHAT_ID` secrets with the original bot/chat.
- Verify a real MP4 is sent using Telegram `sendVideo`; require the API success response and message ID.
- Retry transient network/API failures safely. Do not log secrets.
- Record delivered ayahs and push delivery history only after confirmed API success.

### Agent 4 — QA and release auditor
- Inspect workflow configuration, run steps, artifacts, and logs.
- Separate unit-test success, render success, artifact success, and Telegram delivery success.
- Confirm no TikTok auto-publishing path is enabled and no changes reach `main`.
- Update this plan and `PROJECT_STATUS.md` after verified milestones.

## Current verified repository facts (2026-11-01)

- The active workflow is `.github/workflows/build-quran-audio-inventory.yml`.
- It is scheduled at 03:00, 11:00, and 17:00 UTC (04:00, 12:00, and 18:00 Tunisia time); each slot prepares one distinct-surah review MP4, not a batch of three.
- The workflow contains a Telegram `sendVideo` step for `schedule` and `workflow_dispatch` events, using the existing two secrets.
- `src/send_telegram.py` validates non-empty MP4, a 50 MiB size ceiling, caption length, and Telegram API `ok: true`; it logs the returned message ID without exposing the bot token.
- `src/record_quran_delivery.py` records passage references and delivery timestamp. The workflow invokes it only after the sender returns successfully.
- A previous push-triggered run built an artifact but skipped Telegram by design. A Telegram test message was previously received, but neither fact proves that the scheduled production MP4 has reached Telegram.
- The GitHub integration available in this session exposes file reads/writes and some run/job inspection, but no workflow-dispatch action or general workflow-run listing action. A manual dispatch therefore cannot be honestly claimed from this session.

## Confirmed language decision (2026-11-01)

- The user has reaffirmed that the required output is **Arabic + Saheeh International English**.
- Keep the existing English translation source (`en.sahih`), English renderer field, and English workflow checks. Do not migrate to French or add French as a third language.
- The earlier French discussion is superseded. No translation-language migration is a pending task.

## Execution order and acceptance criteria

1. **Preserve the confirmed English translation path**: keep the Saheeh International English catalog and exact surah:ayah pairing; run its existing completeness and join tests. Do not change the language.
2. **Validate candidate-to-video pipeline**: run existing automated tests and inspect the complete workflow logs. Acceptance: one non-Ash-Sharh distinct-surah MP4 is rendered, 9:16, exact contiguous ayahs, duration <=65 seconds, correct paired translation, and caption metadata.
3. **Validate Telegram end-to-end**: use the existing scheduled/manual workflow path only. Acceptance: Telegram API returns `ok: true` with a message ID for the actual MP4, and the same passage is committed to delivery history afterward.
4. **Validate repeated operation**: verify the next scheduled slot selects a different eligible passage and does not repeat delivered ayahs or the previous background when an approved alternative exists.
5. **Only then declare the engine ready**: three daily slots are operational, each sends one distinct review MP4 to the original Telegram bot; user review and manual TikTok posting remain mandatory.

## Latest pipeline evidence (2026-11-01)

- GitHub Actions run `41289938290` completed successfully on the active branch at commit `78687c5988f69fc7d21c0d666e0f3dd47ad9082c`.
- The workflow built a non-Ash-Sharh candidate: Surah Muhammad (47), ayahs 16–17, and rendered `quran_s047_016_017_REVIEW_ONLY.mp4` as a vertical 9:16 review preview.
- The inventory, translation corpus, Arabic candidate corpus, exact-key join, regression tests, audio preparation, manifest generation, render, and artifact upload all completed successfully. Artifact ID: `13076309641`.
- The Telegram send step was **skipped**, not failed and not successful. The run was a push-triggered run; the workflow only sends for `schedule` or `workflow_dispatch`. Therefore this run proves a distinct-surah preview can be rendered, but does not prove MP4 delivery.
- The mocked sender unit test returned a fake Telegram message ID in the test; it is not a real Telegram delivery.

## Current release status

**Not yet declared ready.** English is the confirmed language and there is no French/English mismatch to resolve. The actual scheduled MP4 delivery has not been proven in the evidence reviewed on 2026-11-01. Do not tell the user the engine is complete until the remaining delivery and repeated-operation acceptance criteria are met.
