# PROJECT MASTER LOG

## Project identity
- Repository: `samiouess-ux/IslamicTikTokAutomation`
- Authoritative working branch: `feature/telegram-review-notifications`
- Never modify `main`.
- Existing engine must be improved in place; do not rebuild it.
- TikTok publishing remains manual after the user's review.
- Daily delivery continues through the existing external Cron and original Telegram bot. Do not change Cron, bot, credentials, delivery architecture, or schedule without separate explicit approval.

## How to use this log
This is the ongoing project handoff and decision log. Read it together with [ORCHESTRATOR_BASELINE_2026-11-19.md](ORCHESTRATOR_BASELINE_2026-11-19.md) before resuming work.
After each meaningful phase, update this file with:
1. Date and active branch HEAD.
2. Evidence inspected.
3. Decisions confirmed by the user.
4. Exact files changed (if any).
5. Tests run, their exact results, and workflow links/IDs.
6. Open issues and the single next action.

Never claim a change, test, delivery, or documentation update succeeded unless the GitHub result or workflow evidence was checked. Distinguish code inspection from automated tests and from human visual/audio review.

## Non-negotiable working rules
1. Confirm the active branch and current HEAD before each task.
2. Inspect the relevant source, tests, workflow, and logs before proposing a change.
3. Prove the exact gap before suggesting a fix.
4. No code, workflow, configuration, or production behavior changes without the user's explicit approval.
5. Keep approved changes small, isolated, and reversible; preserve working functionality.
6. Run focused automated tests first, then only necessary regression tests. Do not repeat successful tests without a code/input/environment change or a diagnostic reason.
7. Do not ask the user to perform routine tests. Ask only for genuinely human-only checks, such as reviewing video appearance/audio or providing TikTok Studio metrics.
8. Never send a real Telegram video just to test code. Keep test-only execution isolated from production send and delivery-history writes.
9. Do not alter Cron, Telegram credentials, the original bot, delivery schedule, delivery architecture, or TikTok auto-publishing policy without separate explicit approval.
10. Record outcomes here. If a task is incomplete, say so clearly and leave the next step explicit.

## Confirmed operating requirements
- Three daily Quran videos are prepared and delivered to the original Telegram bot for the user's review.
- The user uploads to TikTok manually; no automatic TikTok publishing.
- Quran content must retain Arabic Quran text and the English Saheeh International translation; do not replace it with French.
- Quran recitation only; no music.
- Preserve whole ayahs; never cut an ayah or speed up recitation to satisfy a duration limit.
- Friday behavior prioritizes Surah Al-Kahf as previously specified.
- Keep variety in visual backgrounds and avoid unnecessary repetition where the finite approved asset library permits.
- User prefers short, clear, step-by-step guidance and does not want repeated low-value manual tests.

## Existing baseline reference
- Baseline document: [docs/ORCHESTRATOR_BASELINE_2026-11-19.md](docs/ORCHESTRATOR_BASELINE_2026-11-19.md)
- Baseline documentation commit: `e26b7048fb6ee3be220f827fa0ef56a31b340180`
- Baseline inspection recorded the successful workflow run `44512334782` (#514), including a confirmed Telegram delivery (`message_id=124`) and a 30.725-second 1080x1920 video. These are historical observations, not a claim about current live status.
- The baseline notes the workflow has `push` (path-filtered) and `workflow_dispatch` triggers, while the user-confirmed daily launches are handled externally by Cron.
- The baseline also records the current source duration limit of 45 seconds and a mismatch with earlier user-approved 40-second guidance. Do not silently change the limit.

## Work log

### 2026-11-19 — TikTok Growth read-only audit (in progress)
**Branch / repository state**
- Branch: `feature/telegram-review-notifications`
- Latest observed branch commit before this log was created: `e26b7048fb6ee3be220f827fa0ef56a31b340180`
- The branch was confirmed to exist.
- No source code, workflow, schedule, Telegram, or production configuration was changed during this audit.

**Files and paths inspected**
- `src/quran_social_caption.py`
- `tests/test_quran_social_caption.py`
- `.github/workflows/build-quran-audio-inventory.yml`
- `docs/ORCHESTRATOR_BASELINE_2026-11-19.md`
- `src/prepare_quran_review_batch_audio.py` was previously inspected for the duration-limit mismatch.
- The workflow section inspected shows `build_social_caption()` is called immediately before Telegram send and its JSON output is saved under `output/telegram_captions/`.

**Observed current behavior**
- Caption generation produces Arabic and English text, with a limited theme selection based on words in the English translation.
- Exactly five hashtags are currently generated.
- Hashtag selection is deterministic from the video/candidate ID; this is not a persistent global history of previously used captions, hooks, CTAs, and hashtags.
- No dedicated opening-hook generator or varied CTA system was found in the inspected caption builder and workflow paths.
- No TikTok performance analytics/feedback loop was found in the inspected paths. This is a scoped finding, not proof that no related functionality exists anywhere in the repository.
- The Quran delivery history tracks used ayah references; it is not a social-caption/hashtag history and should not be repurposed without design review.
- Static review identified a likely Arabic hashtag classification bug in the Unicode range test in `src/quran_social_caption.py`. The existing tests do not appear to assert the actual Arabic-vs-English classification. This finding still needs a focused regression test against the current branch before any fix is proposed as fully confirmed.

**User-requested direction — proposed, not yet implemented**
- Increase the hashtag count above five; proposed initial target is 8–10 per post, subject to quality and tests.
- Every post should contain both Arabic and English hashtags.
- Mix broad relevant tags with tags genuinely related to the selected ayahs; avoid filler and irrelevant trending tags.
- Improve and vary bilingual captions.
- Add respectful, Quran-appropriate hooks and natural varied CTAs.
- Consider persistent rotation/history for captions, hooks, hashtags, and CTAs, avoiding duplicate systems and preserving history safely.
- Do not invent tafsir, religious claims, or unsupported meanings from keyword matching.
- Do not change Telegram delivery or enable TikTok auto-publishing.

**Approval boundary**
- The user approved creating this project log and recording the current findings.
- The user has NOT yet approved any source-code or workflow changes.
- The user has NOT yet approved a final hashtag count or implementation design.
- The audit is still read-only; no code fix or new social history file has been created.

**Next action**
1. Continue read-only inspection of all relevant caption/hashtag/history call sites and test coverage on this branch.
2. Run or otherwise establish a focused, non-production regression check for the Arabic hashtag classification defect; do not dispatch the production workflow or send Telegram.
3. Present a concise evidence-based implementation proposal (exact files, data-history strategy, migration/compatibility risks, and focused tests).
4. Wait for explicit user approval before changing code.

## Current status
- Project log: created and verified in this commit.
- TikTok Growth audit: in progress, read-only.
- Source changes: none in this phase.
- Production schedule / Telegram / publishing behavior: unchanged.


### 2026-11-19 — TikTok Growth audit: workflow and safety-path inspection
**Branch / repository state**
- Branch: `feature/telegram-review-notifications`
- Latest observed branch HEAD before this documentation update: `2a77d4d9c9d33b182f0f276a4ec6dc4a670db905` (the master-log creation commit).
- Branch existence was rechecked. The recent-commit listing identifies the same commit as the latest observed branch commit at inspection time.
- No source, test, workflow, Cron, Telegram, credential, or production configuration files were changed.

**Additional files and paths inspected**
- `src/record_quran_delivery.py`
- `src/quran_delivery_attempt.py`
- `src/send_telegram.py`
- `tests/test_send_telegram.py`
- `tests/test_telegram_workflow_safety.py`
- Relevant workflow sections covering candidate generation, caption creation, Telegram reservation, send, and confirmed-delivery finalization.

**Confirmed integration and safety observations**
- The active workflow creates each caption JSON by calling `build_social_caption(manifest, candidate_id)` immediately before calling `src/send_telegram.py`.
- `send_telegram.py` composes Arabic caption + Arabic hashtags + English caption + English hashtags, then appends the manual-review notice. It enforces Telegram's 1,024-character caption limit.
- The workflow reserves Quran delivery before Telegram send and records ayah history only after the send step succeeds. Existing safety tests assert this ordering and the test-only skip conditions.
- `data/quran_delivery_history.json` is specifically an ayah-reference/delivery ledger. It is not a safe substitute for a social-content repetition ledger.
- The workflow's test-only render path is designed not to send Telegram and not to reserve/finalize production ayah history. No workflow was dispatched during this audit.
- No separate caption/hashtag history file or social-performance feedback integration was established by the files inspected so far. This remains a scoped audit result, not a claim that every repository path has been exhaustively enumerated.

**Focused Unicode reproduction**
- Reproduced the exact current predicate from `src/quran_social_caption.py` against `#القرآن_الكريم` and `#Quran`.
- Current predicate result: Arabic field = empty; English field incorrectly contains both tags.
- Correct Unicode range predicate result: Arabic field contains `#القرآن_الكريم`; English field contains `#Quran`.
- This was an isolated Python reproduction of the fetched source expression, NOT execution of the repository's unittest suite and NOT a committed regression test.
- Existing `tests/test_quran_social_caption.py` does not currently assert Arabic/English classification directly.

**Current audit conclusion**
- The Unicode classification defect is now demonstrated with a minimal reproduction and is ready for a small regression test/fix proposal.
- The Telegram integration point is localized to caption generation before send; the sender already accepts the bilingual field structure.
- Any persistent social-content history should be a separate store/module, with an explicit rule for when an item is marked used. It must not mutate the Quran ayah ledger and must not interfere with Telegram's pending reservation/finalization protocol.
- Caption/hashtag growth must also account for the sender's 1,024-character Telegram caption cap; a larger hashtag count cannot be added blindly.
- No final hashtag count or persistent-history schema has been approved by the user.

**Next action**
1. Finish checking any remaining repository-wide social-history/caption call sites where accessible on this branch.
2. Present the minimal Unicode fix and a safe, separately scoped design for bilingual captions, hooks, CTAs, hashtag count/quality, and anti-repetition.
3. Wait for explicit approval before changing source code or workflow.


### 2026-11-19 — TikTok Growth phase 1: Arabic hashtag classification fix
**Branch / commit**
- Working branch: `feature/telegram-review-notifications` only.
- Starting HEAD verified before this change: `b783b3e188a60ad336b1be7b2e24cc4489f44d8a`.
- Change is limited to the caption classifier, its focused regression test, and this log.

**Change**
- Replaced the incorrectly escaped Unicode-string comparison with a numeric Arabic Unicode-block check (`0x0600 <= ord(ch) <= 0x06FF`).
- Added a regression test proving Arabic tags are classified as Arabic and English tags contain no Arabic-block characters.
- Hashtag count, caption wording, rotation, Telegram composition, workflow behavior, Cron, credentials, and delivery history are unchanged.

**Validation status**
- The regression test has been added but has not yet been run in the repository environment.
- No production workflow was manually dispatched and no Telegram video was sent by this change.
- Awaiting the push-triggered inventory workflow result; its push trigger is limited to the existing branch and this workflow's configured path filter.

**Next action**
- Inspect the resulting workflow run and its caption test result. If successful, close this phase; otherwise diagnose only the failing test without expanding scope.


### 2026-11-19 — TikTok Growth phase 1: isolated validation result
**Branch / commit**
- Branch HEAD confirmed before this documentation update: `e5257ba4ae4990bcc8c391ba00088c6cad5dca17`.
- No source, test, workflow, Cron, Telegram, credential, or production behavior was changed during this validation step.

**Validation**
- The push-triggered GitHub Actions run #516 (`44577566460`) completed with conclusion `success`: https://github.com/samiouess-ux/IslamicTikTokAutomation/actions/runs/44577566460
- This workflow did NOT execute `tests/test_quran_social_caption.py`; the caption test is not listed among its job steps. Therefore its green conclusion is not evidence that the new caption regression test passed.
- Ran a local isolated Python check using the exact corrected Unicode predicate and the same representative Arabic/English tags. Result: PASS — Arabic tags were classified as Arabic, English tags as English, and the five-tag total was preserved.
- Limitation: this was a focused predicate-level check, not execution of the repository's full unittest file. The committed regression test remains unverified in the repository test environment.
- No Telegram send, production workflow dispatch, Cron test, or delivery-history write occurred.

**Outcome / next action**
- The Unicode fix is committed and the focused predicate behavior passed an isolated check.
- Phase 1 is not marked fully test-complete until `tests/test_quran_social_caption.py` is executed as a repository test.
- Next action: obtain a safe way to run that exact test file without invoking the production video/Telegram workflow; then record its exact result. Do not ask the user to use external Cron for testing.


### 2026-11-19 — TikTok Growth phase 1: caption unit test execution
**Branch / source**
- Tested the exact contents fetched from `feature/telegram-review-notifications` at the time of validation.
- Source blob: `e1f0ea30d4e4d293b90ce5c5fcf11af534bdffe6`.
- Test blob: `fd0a163d9b4717a239ed7054d1e19617367053bc`.

**Test result**
- Executed `python -m unittest discover -s tests -v` in an isolated temporary Python directory populated with those fetched source and test file contents.
- Result: **PASS — 4 tests, 0 failures, 0 errors**:
  - exactly five hashtags and thematic caption
  - rotation between video IDs
  - general fallback for unknown topic
  - Arabic/English hashtag classification regression
- This verifies the fetched module and test file together. It was not a checkout of the full repository, and it does not replace the separate GitHub Actions workflow result.

**Safety**
- No source or test files were changed in this validation step.
- No Cron test, production workflow dispatch, Telegram send, credential change, or delivery-history write occurred.

**Outcome**
- The targeted `test_quran_social_caption.py` suite is now verified: 4/4 passing.
- TikTok Growth phase 1 (Arabic hashtag language classification fix) is test-complete. Any next growth improvements remain a separate phase and require the user's approval.
