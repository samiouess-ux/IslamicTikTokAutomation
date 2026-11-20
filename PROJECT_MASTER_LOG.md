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


### 2026-11-19 — TikTok Growth phase 2: read-only implementation audit
**Branch**
- Active branch verified: `feature/telegram-review-notifications`.
- HEAD before this audit record: `0266fc86f440e3d2fb9fa59e23db235b70d16e78`.
- Audit only; no source, workflow, Cron, Telegram, credential, or delivery-history changes.

**Verified current behavior**
- `src/quran_social_caption.py` is the active caption builder invoked in the Telegram-send step of `.github/workflows/build-quran-audio-inventory.yml`.
- It builds Arabic and English captions, chooses one of a small set of themes by keyword counts in the English translation, and returns exactly five deterministic hashtags.
- The caption wording currently has only fixed generic endings ("استمع وتدبّر" / "Listen and reflect"); no dedicated opening-hook selection or CTA rotation was found in this builder.
- The workflow's regression-test step runs `test_quran_social_caption.py` and `test_send_telegram.py`.
- `src/send_telegram.py` composes the Arabic caption, Arabic tags, English caption, English tags, and manual-review notice; it rejects a caption longer than 1,024 characters before sending.
- The existing caption tests explicitly enforce exactly five unique hashtags. Any count increase therefore requires updating that contract and its tests.
- `src/hashtag_strategy.py` is present and defines a separate multilingual deterministic hashtag strategy, including French, Turkish, and Indonesian fields. The active inventory workflow does not call it in the inspected send path, and no corresponding test file appears in the repository tree. It must not be integrated blindly: the current project requirement is Arabic + English, not additional languages.
- `data/quran_delivery_history.json` is the Quran ayah reuse ledger. It is not an appropriate store for social caption/tag repetition history.

**Gaps and risks**
- No persistent global history for used captions, hooks, CTAs, or hashtag combinations was identified in the inspected active path.
- Theme matching is a lightweight English-keyword heuristic, not tafsir. New copy must avoid presenting inferred meanings as authoritative religious interpretation.
- More hashtags and bilingual copy must remain within Telegram's 1,024-character caption limit.
- A social-history store must be separate from the ayah ledger and must not mark content as delivered on test-only, failed, or ambiguous Telegram outcomes. The safe integration point needs an explicit idempotent design around confirmed Telegram delivery.

**Smallest proposed implementation plan — not yet approved**
1. Extend the active caption builder with a curated bilingual opening-hook library and respectful Arabic/English CTA variants, without changing Quran text or claiming tafsir.
2. Increase the hashtag set from five to a user-approved count above five; keep tags relevant and Arabic/English only. Validate the complete composed Telegram caption against 1,024 characters.
3. Add a dedicated social-content history file/module, separate from Quran ayah history, with deterministic candidate selection and duplicate avoidance. Record use only after confirmed Telegram delivery, with safe retry/idempotency handling.
4. Add focused unit tests and a test-only validation path that never sends Telegram or mutates production delivery history.

**Decision**
- This is a read-only audit and proposal only. No implementation has started.
- Wait for the user's explicit approval of the scope and hashtag target before changing code.


### 2026-11-19 — TikTok Growth phase 2: bilingual copy and hashtag rotation implemented
**Approval and confirmed requirements**
- The user approved implementation after the read-only audit.
- Corrected hashtag requirement: **exactly five hashtags per TikTok post**, not more than five.
- Use Arabic and English only; current implementation emits three Arabic and two English tags per post.
- The user clarified that the desired variety comes from a broad rotating library across posts, not a larger number of hashtags on one post.

**Implementation**
- Expanded the active hashtag pools to 20 Arabic and 20 English relevant tags. Two generic Arabic tags, one generic English tag, and the theme-matched Arabic/English pair make exactly five.
- Added ten curated bilingual opening hooks and ten bilingual CTA variants. Copy is selected with deterministic tie-breaking and least-used-first counts.
- Added a separate persistent social-content history. It tracks confirmed post hashtag use, hook IDs, and CTA IDs; it is not mixed with Quran ayah delivery history.
- The workflow reads this social history when preparing the caption and records the selected social content only after the Telegram sender step reports success. Test-only runs and push-triggered builds skip recording. Recording is idempotent for a repeated candidate ID and rejects conflicting content.
- Existing Telegram sender remains unchanged and continues to reject a complete caption longer than 1,024 characters.
- TikTok publishing remains manual. No Cron, Telegram credentials, bot, daily schedule, Quran text, translation, recitation, or Quran ayah history behavior was intentionally changed.

**Exact files changed**
1. `src/quran_social_caption.py`
2. `src/quran_social_history.py` (new)
3. `tests/test_quran_social_caption.py`
4. `tests/test_telegram_workflow_safety.py`
5. `.github/workflows/build-quran-audio-inventory.yml`

**Validation**
- First push run #521 (`44601646099`) exposed one outdated assertion that expected the old fixed hashtag to appear in every generated post. The implementation's new rotation correctly selected a different Arabic tag; the test was corrected to assert language classification and pool membership rather than a fixed per-post tag.
- Final push run #522: **PASS**, run ID `44601960747`, commit `c19b9f3d76ccebfc47e9be20a2c28d7aa8d60383`.
  - Link: https://github.com/samiouess-ux/IslamicTikTokAutomation/actions/runs/44601960747
  - Caption/rotation tests: 7 passed.
  - Telegram sender tests: 8 passed.
  - Telegram workflow safety tests: 9 passed.
  - The complete workflow completed successfully.
  - Because this was a `push` event, the Telegram reservation, Telegram send, confirmed-delivery history write, and history-sync steps were all skipped. No real Telegram video was sent.
- Branch HEAD verified after the implementation: `c19b9f3d76ccebfc47e9be20a2c28d7aa8d60383`.

**Open review item / next action**
- Code and automated validation are complete. The first actual scheduled delivery using this version will create the initial `data/quran_social_history.json` entry only after Telegram confirms delivery. The user can then review the caption variety on a normal delivered video; no separate test delivery is needed.
- Do not claim the new copy's TikTok performance is proven until actual post metrics are reviewed.


### 2026-11-19 — First Telegram caption sample reviewed after copy-rotation update
- The user shared the Telegram caption received for Surah Al-Humazah, verses 1–8.
- Observed output contains an Arabic caption and an English caption.
- Hashtag count and language split are exactly as required: **3 Arabic + 2 English = 5 total per video**. The user explicitly confirmed this is the intended per-video format.
- This sample is a successful format/count check. It does not by itself prove cross-video rotation or absence of repetition; compare subsequent delivered captions against the persistent social-content history.
- No code, hashtag pools, caption rules, scheduler, Telegram bot/settings, or delivery history were changed for this review.

### 2026-11-19 — TikTok Growth roadmap order confirmed by user
**Authoritative order — preserve this sequence; do not ask the user to repeat it**
1. **Completed; do not redo without evidence of a defect:** bilingual captions and hooks/CTAs, exactly five hashtags per post (3 Arabic + 2 English), expanded rotating hashtag pools, persistent social-content rotation/history, and the associated tests from Growth phases 1–2. Phase 1 Arabic hashtag classification fix and Phase 2 copy/hashtag rotation are recorded above; final validation was GitHub Actions run #522 (`44601960747`), with 7 caption/rotation, 8 Telegram sender, and 9 workflow-safety tests passing.
2. **Next priority — video-level growth/retention improvements:** inspect the existing video opening and first two seconds, then identify concrete improvements to the visual hook, pacing, and viewer retention. Audit the current renderer and design before changing anything; preserve Quran accuracy, approved visual rules, recitation-only audio, and manual Telegram review.
3. **Following priority — visual variety and anti-repetition:** inspect scene/background/layout/transition rotation and its persistent history; improve only the gaps actually found. Do not reintroduce unapproved backgrounds or claim full variety without evidence.
4. **Later, not now — TikTok analytics:** defer performance tracking/analytics until the preceding video-level and visual-variety work has been reviewed and completed. Do not jump to analytics as the next phase.

**Permanent execution constraints**
- Continue only in samiouess-ux/IslamicTikTokAutomation on feature/telegram-review-notifications; never modify main.
- Do not redo completed caption/hashtag work unless a specific regression is demonstrated.
- Do not change the user's working external Cron schedule (04:10, 12:10, 18:10 Africa/Tunis), Telegram bot/settings, or manual-only TikTok publishing.
- Before each implementation phase, inspect current code and logs, state the exact verified gap, make the smallest scoped change, run only relevant safe tests, and record the evidence here and in PROJECT_STATUS.md.
- No production test sends or schedule changes merely to validate growth work.

**Status at this checkpoint**
- This entry records the agreed roadmap and order only. No source code, workflow, Cron, Telegram, or production configuration was changed by this documentation update.
- Next action: read-only audit of the video opening/first-two-second experience and current renderer path; report the specific gap before implementation. Do not revisit completed caption/hashtag phases.

## TikTok Growth phase 2 — opening hook / retention implementation (2026-11-19)
- Active branch: `feature/telegram-review-notifications`; implementation commits: `e1510679bd6c1bc8a4e4107e8f2b2cd3a33dafda` (renderer) and `029a5ed55ac3f2147f4977b7c3714caf40d2763e` (regression test).
- Read-only audit evidence: `src/render_quran_review_previews.py` showed a 0.6-second opaque cover with a hard cut; the first ayah overlay was disabled until 0.6 seconds. `tests/test_render_quran_review_previews.py` explicitly asserted this no-fade behavior.
- Scoped change: the first ayah is now composited from t=0 beneath the opening cover; the cover fades out from 0.4s to 1.2s (0.8-second alpha fade), revealing the first ayah and live background smoothly. The original recitation still starts at t=0 and is not modified. Cover artwork, Quran text, translation, recitation, duration limits, background selection, Telegram, Cron, and TikTok publishing settings are unchanged.
- Updated the focused renderer regression test to assert the overlay order, exact fade timings, first-ayah visibility from t=0, and audio start at t=0.
- Validation status at documentation time: GitHub commit status returned no checks yet; tests and workflow render are **pending**. Do not call this verified until the relevant workflow completes successfully. The push-triggered workflow's Telegram reserve/send/history steps are guarded to run only for schedule or qualifying workflow_dispatch events; this change did not dispatch a send or alter Cron.
- Next action: inspect the CI result for commit `029a5ed55ac3f2147f4977b7c3714caf40d2763e`; if green, inspect the generated review-only preview before considering the retention step complete.


### 2026-11-19 — TikTok Growth phase 2: opening transition verified by Cron delivery and user review
- Active branch: `feature/telegram-review-notifications`; branch HEAD before this documentation update: `57aa4f178e629e4d60281ee0d5be272d68f7b658`.
- Renderer implementation: `e1510679bd6c1bc8a4e4107e8f2b2cd3a33dafda`; regression-test correction: `0a0fe1c0337a67febf0985c64bd12b316db63667` (uses approximate float comparison for the computed 0.4s fade start).
- Automated validation: all three push-triggered workflows for commit `0a0fe1c0337a67febf0985c64bd12b316db63667` completed successfully: Quran batch engine tests (`44612696387`), Quran-wide inventory (`44612696062`), and isolated request pipeline (`44612696031`). The request-pipeline and batch tests were green; inventory/catalog regression and review rendering stages were green.
- Real Cron-triggered workflow run #527 (`44613610568`) completed with conclusion `success` on the same implementation commit. The workflow successfully prepared a distinct-surah candidate, rendered the 9:16 review video, prepared and composited the staged background previews, reserved Telegram delivery, sent one review-only video to the existing Telegram bot, recorded Telegram-confirmed delivery history, and synced that history to the active branch.
- Telegram send and confirmed-history steps both completed successfully. GitHub Actions created the history commits `06df2c2c767add0ab811222a2f09b00a3ea84e9c` (reservation) and `57aa4f178e629e4d60281ee0d5be272d68f7b658` (confirmed delivery/history sync).
- Human review: the user confirmed the delivered video was “باهي برشا” (very good). This is the first actual user visual approval of the new opening transition. The first ayah appearing from t=0 beneath the cover and the 0.4–1.2s fade implementation are now accepted for this phase.
- Scope preserved: no changes to Cron schedule, Telegram bot/credentials, TikTok auto-publishing, Quran text/translation, recitation, or `main`. TikTok posting remains manual.
- Outcome: TikTok Growth phase 2 (opening hook / retention implementation) is complete and validated by automated tests, a successful Cron-triggered Telegram delivery, and user review.
- Next phase, per the user's approved roadmap: read-only audit of visual variety and anti-repetition (backgrounds/scenes/layout/transitions). Do not revisit captions/hashtags or alter production behavior until a concrete gap is verified and scoped.


### 2026-11-19 — TikTok Growth phase 3: read-only visual variety and anti-repetition audit
- Active branch: `feature/telegram-review-notifications`; HEAD before this documentation update: `a2b1648e9b3f79637c9910c9f0c85e4314752a3c`.
- Audit was read-only. No renderer, workflow, background catalog, photo asset, Cron, Telegram, or production setting was changed.
- Active production path confirmed: `.github/workflows/build-quran-audio-inventory.yml` invokes `src/render_quran_review_previews.py` and passes `GITHUB_RUN_NUMBER` as `--background-rotation-index`. The separate `src/render_video_scenes.py` is not invoked by this active scheduled render step; its photo-scene xfade implementation must not be mistaken for a transition already used by the active production renderer.
- Active renderer loads approved moving-video candidates from `data/background_candidates.json` and downloaded stills from `data/background_photos_manifest.json`. The latest successful Cron-triggered run #527 (`44613610568`) recorded 15 eligible moving-video backgrounds + 35 valid photo backgrounds = 50 combined assets. The 35 photo files were present and passed the renderer's image verification in that run.
- Actual run #527 preview report recorded a mountain-sunset photo (`pexels-33406291`) followed by an approved moving mosque-waterfront clip (`pexels-mosque-waterfront-12536108`). The user separately confirmed the delivered video was very good. This proves mixed-media selection worked for that one video; it does not establish cross-video anti-repeat performance.
- Existing protections: per-video selection tracks `used_background_ids` and avoids reusing the same asset until the eligible pool is exhausted; background start selection is deterministic from the run number; four opening-cover templates rotate using the same run-number index.
- Verified gaps:
  1. No persistent background/cover usage history exists alongside `data/quran_delivery_history.json` and `data/quran_social_history.json`. Cross-video avoidance relies on the workflow run number, not confirmed delivery history. Any unrelated workflow run can advance that index; it does not express a true “recently delivered visual assets” window.
  2. The active renderer joins the per-ayah MP4 segments using FFmpeg concat with stream copy. It does not apply a dedicated crossfade/transition at verse-scene boundaries. The 0.8-second alpha fade applies only to the opening cover, not to later scene changes.
  3. The active background order is driven by a single run-number index and a fixed interleaving/order of the photo/video pools; there is no persisted category-level balancing (for example, avoiding several visually similar mosque-exterior or sea/water scenes in consecutive posts).
- Existing test coverage verifies deterministic rotation, within-video non-reuse, asset approval gates, and schedule-index arithmetic. It does not test a persistent cross-video history or scene-transition variety in the active renderer.
- Recommended smallest next design (not implemented): add a separate visual-usage ledger, independent of Quran ayah and social-caption histories, recording background IDs/categories and cover template IDs only after Telegram confirms delivery; use a bounded recent window with safe idempotency for retries. Separately introduce a small curated transition policy for verse boundaries, with tests proving duration/audio/ayah timing remain unchanged. Keep the existing 50 verified assets and approval gates; do not activate unapproved candidates or change Cron/Telegram.
- Approval boundary: this phase was read-only. No source-code or production behavior changes have been made. Wait for explicit approval of the implementation scope before editing renderer/history/workflow.


### 2026-11-19 — TikTok Growth phase 3 implementation: visual history and scene transitions
- Implemented on `feature/telegram-review-notifications`; code/test commits: `ff2c14b0a2abd934b2ecba576bc1fd73b7b77840`, `eb654d6fc8a5256bb86ef2318265c5a4e8d5a506`, `d02d247478d6f0a19de0e787940cac4870338c42`, `36c4170879c38f651955fd442fb78315b2db8107`, `d9b4e3b76639677435b16fa7e86c6686659a14ca`.
- Added independent `data/quran_visual_history.json` and `src/quran_visual_history.py`. It stores delivered background IDs/categories and cover template IDs, is idempotent by candidate ID, and refuses to record without an explicit Telegram-confirmed gate. The production workflow calls it only after the Telegram-send step succeeds, then commits/syncs it with the existing delivery/social histories.
- Renderer now reads the last six confirmed visual deliveries for background ID/category avoidance and the last three for cover rotation. It also tries to avoid category repetition between ayah scenes within the current video. Existing approved 50-asset library and approval checks are unchanged.
- Active renderer now applies 0.35-second video-only crossfades between ayah scene segments. It builds a separate crossfaded video stream, concatenates the MP3 streams with stream copy, and muxes them without audio re-encoding. Crossfade overlap is padded/trimmed to preserve the sum of segment durations. Single-scene previews retain the prior simple concat path.
- Workflow passes `data/quran_visual_history.json` to the renderer and records it only after confirmed delivery. The history JSON itself is intentionally excluded from push path filters to prevent a history-only commit from re-triggering the workflow.
- Added unit tests for bounded visual history, Telegram confirmation/idempotency, recent asset/category avoidance, cover/scene rotation, crossfade offsets/duration padding, and audio stream-copy assembly. The FFmpeg concat manifest newline is tested and fixed.
- Automated validation: Quran batch engine tests run #200 (`44618085196`) succeeded; 103 tests and module compilation passed. Isolated Quran request pipeline run #134 (`44618085318`) succeeded. An earlier run #200 predecessor failed only because the new test asserted a literal backslash-n; corrected in commit `d9b4e3b`, after which both suites passed.
- Full inventory/render smoke run #532 (`44618085215`) is still in progress as of this log entry. It was triggered by a push, not schedule/dispatch; the Telegram reservation/send and delivery-history steps are gated off for this event. No Cron, Telegram send, TikTok publishing, schedule, bot, credentials, or production secrets were changed.
- Completion gate: wait for run #532's real renderer step to pass before marking phase 3 validated. User visual review of the next normally scheduled Telegram video remains separate from automated validation.

### 2026-11-20 — Exceptional whole-ayah duration allowance (45s normal / 60s single-ayah exception)
- User approved a 60-second maximum only as an exception for one complete ayah; the ordinary maximum remains 45 seconds. This supersedes the blanket 45-second cap only for a single ayah whose processed duration is greater than 45.0 and no greater than 60.0 seconds.
- Audio partitioning isolates any 45–60 second ayah into its own video part. It is never combined with neighboring ayahs, cut, or speed-adjusted. Multi-ayah videos remain capped at 45 seconds; a single ayah over 60 seconds remains deferred intact.
- Updated audio preparation, active renderer validation, Telegram reservation validation, and regression tests. The low-level renderer probe accepts at most 60 seconds, while render and reservation gates enforce the single-ayah-only exception.
- Cron schedule, Telegram bot/credentials, Telegram send behavior, TikTok publishing, and `main` were not changed. No manual workflow dispatch or production Telegram test was initiated. Push-triggered CI may run on this branch; push-event delivery gates remain in force.
- Validation status: implementation committed; await the resulting GitHub Actions test/render-only workflow conclusions before calling the change verified.

### 2026-11-20 — Duration-policy validation checkpoint
- Latest code commit: `efb6f710e8a6fafd47e82f350f82a180aabfad8b`.
- Quran engine test workflow run #205 (`44688267334`) passed on that commit.
- Isolated request-pipeline test workflow run #139 (`44688267567`) passed on that commit.
- Full inventory/render-only workflow run #537 (`44688267390`) is still in progress at the distinct-surah audio-preparation step. It was triggered by push; Telegram reservation/send/history steps are gated off for push events. No production Telegram delivery or Cron test was initiated by this change.
- Do not mark end-to-end rendering verified until run #537 completes successfully.

### 2026-11-20 — Exceptional 46.733-second Al-Kahf ayah verified end-to-end (review-only)
- Full inventory/render workflow run #537 (`44688267390`) completed with conclusion `success` on code commit `efb6f710e8a6fafd47e82f350f82a180aabfad8b`.
- The Friday candidate was Surah Al-Kahf (18), ayah 17. Original ayah duration: 49.050 seconds; after the existing edge-silence-only processing: 46.733 seconds. The complete ayah was selected alone; next ayah 18 remained unselected for continuation.
- The active renderer produced `quran_s018_017_110_part_001_REVIEW_ONLY.mp4`, duration 46.733 seconds, 1080x1920, preserving the MP3 audio stream. This directly validates the new 45–60-second single-ayah exception against the previously blocked ayah.
- Quran engine test workflow #205 (`44688267334`) and isolated request-pipeline workflow #139 (`44688267567`) both passed on the same code commit.
- This was a push-triggered render-only validation. Telegram reservation, Telegram send, delivery-history recording, and sync were all skipped; no Telegram video was sent and no production Cron was run. The regular 45-second limit for multi-ayah videos and the 60-second absolute cap for one complete ayah remain enforced.


### 2026-11-20 — Surah-title ornament refinement
- Refined the title cartouche on `feature/telegram-review-notifications` using a restrained manuscript-inspired composition: pointed double contour, symmetrical eight-point rosette terminals, and mirrored leaf-like arabesque details.
- Kept the existing title text and placement, gold accent treatment, and the independent divider/diamond ornament beneath the title. This change is isolated to the surah-title decoration; it does not alter Quran text/translation, audio timing, cover fade, ayah layout, verse medallions, backgrounds, transitions, duration limits, Telegram delivery, Cron, or TikTok publishing.
- Added regression checks for the cartouche top and both rosette terminals. Awaiting automated tests and visual preview review before acceptance.


### 2026-11-20 — Run #540 send-gate diagnosis, correction, and safe recovery
**Evidence**
- Run #540 (`44719548618`) completed with failure on the correct branch. Its render and background-preview preparation steps succeeded; the 46.733-second single-ayah Al-Kahf 18:17 preview was prepared.
- The reservation step committed `data/quran_delivery_pending.json`. The Telegram send step then rejected the preview at a stale inline `duration_seconds > 45` check. The log shows this happened before `subprocess.run(... src/send_telegram.py ...)`; therefore the MP4 send was never attempted. The separate failure notification was accepted by Telegram.
- Delivery-history recording and sync were skipped. The failure did not represent a Telegram API rejection.

**Changes on `feature/telegram-review-notifications`**
- `src/quran_delivery_attempt.py`: added `delivery_duration_limit_seconds(selected_verses)`, the shared rule of 60 seconds for one complete selected ayah and 45 seconds for multiple ayahs; reservation validation now calls this helper.
- `.github/workflows/build-quran-audio-inventory.yml`: send guard now matches the preview to exactly one prepared audio-report item, reads its selected ayahs, and calls the same helper. It no longer has a separate hard-coded 45-second limit.
- `tests/test_quran_delivery_attempt.py`: added focused tests for the shared 60/45-second policy and invalid empty selection. Existing integration tests retain the 46.733-second one-ayah acceptance and multi-ayah-over-45 rejection cases.
- `data/quran_delivery_pending.json`: removed the stale pending reservation only after confirming the send subprocess had not run. No delivery history was written; no ayah was marked as delivered.

**Commits**
- Shared policy: `eb78d36b71869acf60c3fb88cd92f66cdf102041`
- Tests: `f5604c1788f3565f34505bef36f0810fb7379b34`
- Workflow send gate: `6dfbc396cd2330b2288e49320ab47917e8cf01c1`
- Pending reservation cleanup: `20c077653b949c535b43996938145bc0b657d0a8`

**Safety and next step**
- No changes to Cron, schedule, bot, credentials, TikTok publishing, or `main`.
- Await the push-triggered test/render-only workflow result. Push-event conditions keep Telegram reservation/send/history disabled.
- Do not rerun Cron or manually dispatch a production Telegram send until CI is green and the user asks to test.
