# Agent work plan — IslamicTikTokAutomation

## User directive — simplify and finish the engine (2026-11-01)

This directive takes priority over optional enhancements and exploratory work:
- Stop sending the user repeated technical questions when the repository, logs, or tests can answer them. Make safe engineering decisions independently and fix ordinary implementation/test failures directly.
- Do not expand the architecture. One existing GitHub Actions engine + the original Telegram bot only; no new cloud services, bots, webhooks, orchestrators, paid agents, or user-operated infrastructure.
- Do not restart or replace working components. Preserve the proven Quran prototype and generalize it to other verified surahs/ayahs.
- The immediate deliverable is a valid varied Quran MP4 (Arabic + Saheeh International English, <=65 seconds, whole contiguous ayahs, no music) delivered by sendVideo to the existing Telegram chat. TikTok remains manual.
- Prioritize end-to-end operation over optional background-library expansion, new categories, or cosmetic refactoring. Fix blockers in order: candidate selection/content integrity -> render -> Telegram send -> delivery-history commit -> next-slot non-repetition.
- Test each concrete fix, inspect the actual Actions result, and update PROJECT_STATUS.md. Never call a preview/build/test a completed delivery unless Telegram confirms a real message_id.
- Work only on feature/telegram-review-notifications. Never modify main.
- The available Agent 1–4 entries are review responsibilities, not separate autonomous agents; do not imply independent agents are running.

Last updated: 2026-11-01

## Caption variation update (2026-11-01)
- Updated the scheduled Telegram caption builder to include the exact ayah range in English and retain the Arabic surah/range caption.
- Added three rotating, topic-relevant Arabic/English hashtag sets selected deterministically per passage, rather than repeating the same two tags on every video.
- Workflow change commit: `f46f7912e1b8deaddef3e725ec2151f7b87fab95`.
- The schedule remains 04:00, 12:00 and 18:00 Tunisia time (one video per slot). Telegram MP4 end-to-end delivery still needs a scheduled/dispatch run with a real Telegram message ID.
- Background limitation identified: the current preview renderer still uses one approved moving-video source; palette accents vary, but full scene/background rotation is not yet implemented. Do not claim background variety is complete or introduce unreviewed external assets.

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


## Final duration-gate test coverage (2026-11-01)
- Added focused regression tests against the renderer's actual ffprobe-based `probe()`: accept exactly 65.000 seconds, reject 65.001 seconds, and reject non-1080x1920 dimensions.
- Commit: `51c2952759ab738b636d129be41e320573cebcdd`.
- Await the push-triggered CI result; this is test coverage only, not proof of Telegram delivery.
- Keep the single approved background source unchanged until a second asset has verified usage rights and user approval.

## Latest operational check (2026-11-01)
- Verified the repository default branch is `feature/telegram-review-notifications`, so the scheduled workflow is correctly located on the default branch.
- Latest successful production build rendered Surah At-Tariq 86:12–13 in 14.55 seconds, 1080x1920, H.264 + original MP3. It was push-triggered; Telegram was skipped by design, so the next schedule event must verify actual delivery.
- Do not spend time on optional background rotation before confirming that the original Telegram bot receives a real MP4.

## Rotation fix — consecutive surah avoidance (2026-11-01)
- The next candidate batch now excludes the surah from the most recent confirmed Telegram delivery, as well as every already-delivered ayah reference. This avoids immediate same-surah repetition without permanently banning a surah.
- Regression coverage added. Await completion of runs `41306047454` and `41306050228` before calling the change tested.
- Telegram delivery still requires an actual `schedule` or `workflow_dispatch` event; push-triggered CI is not delivery evidence.

## Latest CI verification (2026-11-01)
- Surah rotation code and regression tests passed in runs `41306047454` (#92) and `41306050228` (#14). Build output was Surah At-Tariq 86:12–13, 14.55 seconds, 1080x1920, review-only.
- Artifact upload succeeded. Telegram step was skipped on push; wait for the next scheduled run to prove actual MP4 delivery and persistent history recording.
- Background library rotation remains pending; only the existing Mixkit waterfall source is currently used.
