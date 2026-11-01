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

## Live Telegram delivery and history correction (2026-11-01)
- Run `41309830990` completed a controlled real Telegram `sendVideo`; Telegram returned `ok: true` and `message_id=27`. The sent MP4 was Surah Hud 11:1–2, 40.046 seconds, 1080×1920, H.264 + original MP3.
- The source candidate spans Hud 1–123, while the duration selector chose only 1–2. The first recorder implementation incorrectly persisted all 123 candidate ayahs. This was caught during log audit, not hidden.
- Corrected `data/quran_delivery_history.json` to list only 11:1 and 11:2. Updated `record_quran_delivery.py` to require the audio report and record only `selected_verses`; updated the workflow invocation and regression tests.
- Test run `41310129350` passed the test phase including the new selected-prefix tests. Workflow update run `41310167242` is pending/running validation. Confirm its final result before calling this correction fully CI-verified.
- Do not resend the same test MP4. The existing Telegram message is already delivered for manual review.
- This proves one real MP4 send only. The scheduled 04:00/12:00/18:00 operation still needs an actual scheduled event and confirmed delivery-history commit.

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


## Scheduled-run observation (2026-11-01, 13:24 Tunisia time)
- A GitHub Actions run-history query filtered to `event=schedule` returned no runs for the active branch. The 12:00 Tunisia slot is therefore not confirmed as having executed, despite the cron entry being present.
- Recheck after 18:00 Tunisia time. Do not alter push-trigger behavior to send videos, and do not claim Telegram delivery until the scheduled sender logs a real positive `message_id` and delivery history is committed.


## One-off Telegram test procedure
- Do not infer automatic operation from successful rendering or a green push CI run.
- The existing workflow's Telegram step is intentionally skipped on normal pushes. For one controlled live test only, it accepts the exact commit-message marker `[telegram-live-test]`.
- Test commit: `391924dae1c1b4d5826386876f6395e7beae4b6d` on `feature/telegram-review-notifications`.
- Acceptance requires an actual Actions run plus Telegram API `ok: true` and positive `message_id`, followed by a committed delivery-history entry. After that, remove the temporary marker condition and verify scheduled operation separately.
- If no run starts, stop feature development and diagnose why Actions did not launch. Never claim delivery based on mocked sender tests or artifact upload.


## Immediate next actions after first visual redesign (2026-11-01)
1. Check production workflow runs `41310945442` and `41311053908`. Require the Arabic layout regression test, full render, and artifact upload to pass. A push-triggered run must not be described as Telegram delivery.
2. Inspect the rendered MP4 frame-by-frame (including long Arabic ayahs) before calling the layout acceptable. Confirm the gold surah title, legible white Arabic, true gold circular ayah number, smaller complete Saheeh International English translation, 1080x1920 dimensions, and <=65-second duration.
3. Keep background claims precise: current source is still the one approved Mixkit waterfall. Palette tint varies by surah/ayah but is not scene rotation. Build a real rotation pool only from distinct assets with verified rights and explicit user approval; never silently substitute unreviewed stock media.
4. Investigate inter-ayah silence using source MP3 timing/waveforms. Reduce only verified non-recitation gaps while preserving every recitation sample; compare durations and listen to the output. Do not use blind silence removal, trimming, or time-stretching.
5. Only after the user accepts the improved MP4, send one controlled review sample to the existing Telegram chat. Do not publish to TikTok; user approval and manual upload remain mandatory.
6. Continue to verify scheduled 04:00, 12:00, and 18:00 Tunisia slots separately. A green push build is not proof that a scheduled Telegram send occurred.


## Edge-pause reduction implementation and verification (2026-11-01)
- Analyze the actual per-ayah MP3 edges at -50 dB; use the new synthetic MP3 regression test to verify that only leading/trailing silence is removed, a 0.12-second safety margin remains, and MP3 stream-copy is preserved.
- Confirm `processed_audio_files` is propagated from audio preparation into the preview renderer and that the renderer actually uses those paths for each ayah. Do not use the combined passage file for visual scene boundaries; each whole ayah must remain aligned to its own screen.
- Run the production workflow's complete audio and renderer regression suites. Inspect the newest render artifact and verify total duration <=65 seconds, correct selected contiguous ayahs, MP3 audio, and substantially shorter gaps between ayahs.
- If the silence test fails or the detected edges risk cutting recitation, revert only the edge-trimming behavior and keep the diagnostic evidence; do not weaken the threshold or remove internal pauses blindly.
- After CI and artifact review, update the user with the measured gap reduction. Only send a new Telegram sample after the revised visual/audio artifact has passed review; do not send on ordinary push runs.


## Measured preview and audio-gap result (2026-11-01)
- Run `41311768545` completed successfully and produced artifact `13085413677`. The generated Surah Fussilat candidate supplied ayahs 1–54; the duration selector chose whole consecutive ayahs 1–5 for a 62.912-second 1080×1920 H.264/MP3 review MP4.
- Audio measurement on the artifact: raw combined recitation 78.446s; processed combined recitation 63.007s. The four raw inter-ayah silences measured 3.266–3.558s; after edge-only silence handling they measured 0.260–0.267s. A 0.12s safety margin remains at each detected file edge; do not reduce this margin or process internal silence without new listening evidence.
- Sampled frames confirm the revised Amiri Bold typography, ornate double-line gold surah cartouche, gold circular ayah badge, white Arabic, and smaller Saheeh International English. This is a review preview, not user acceptance or production approval.
- Telegram was skipped on this push run. Do not resend or publish this artifact automatically.
- Latest follow-up run `41312075159` is validating the newer longest-processed-prefix regression test. Check its final conclusion before marking that test covered.
- Remaining visual gap: only the approved Mixkit waterfall scene is available. Keep scene rotation blocked until additional sources have both verified reuse rights and explicit user approval. Palette tint variation must not be described as true background rotation.


## Post-delivery workflow hardening and next work (2026-11-01)
- Confirmed Telegram sample: run `41312274181`, `message_id=28`, Surah Fussilat 41:1–5. The history was repaired on the feature branch after the workflow's stale-checkout push was rejected.
- Workflow is now split into Telegram send, history record, and history sync. History sync fetches and rebases onto `origin/feature/telegram-review-notifications` before push. Failure alerts now depend on the Telegram send step failing, not later history-sync failures.
- Temporary tagged-push trigger has been removed; ordinary pushes must never send videos. Only cron schedule and explicit workflow dispatch may deliver.
- Verify the current workflow-change run `41312848189` finishes green. Do not send another Telegram test video.
- Next visual task: create a small candidate pool of distinct nature/sky/landscape background clips from rights-cleared sources, upload a review artifact with thumbnails and source/license details, then add only explicitly user-approved assets to the rotation catalog. The existing asset chooser must fail closed if no approved non-recent background exists.
- Next operational task: independently verify the scheduled 04:00, 12:00, and 18:00 Tunisia slots. One controlled Telegram sample proves one send path, not three daily scheduled sends.
- Keep manual TikTok publishing and the no-auto-publish gate unchanged.

## Official archive network resilience fix (2026-11-01)
- Audited failed Actions run `41312848189`, job `124866668534`. The failure was a TCP connection timeout to `download.qurancomplex.gov.sa` while opening the official ZIP; no archive mapping mismatch was reported. All later steps were skipped because inventory is a required gate.
- Updated `src/build_official_audio_inventory.py` to use bounded request timeouts, HTTP retry/backoff for transient connection/read and 429/5xx failures, a 1 MiB initial ZIP range, and a project User-Agent. If the host remains unavailable, the inventory still fails closed; no stale or guessed mapping is substituted.
- Added `tests/test_build_official_audio_inventory.py` and wired it into the existing Actions workflow.
- Commits: `7d7214eeff00e9239308439ff3f506ac7318743c`, corrected escaping `3181e2b2ed244e0497d1121bd36d8fe6d646ab47`, tests `9ed2f575b64eff3df5048bb799ddafa6885665b0`, workflow `180fca4f55135f05a7e77b86ebb19cb43af934db`, status record `1ae2b3c514648607eb4ecb076472a55231071efc`.
- Await the push-triggered run to verify retry behavior and the complete downstream pipeline. This change does not implement background rotation and does not authorize any new background asset.

## Background candidate staging (2026-11-01)
- Added `data/background_candidates.json` containing four individually referenced Pexels candidates (sea, mountain lake, sunset sky, mountain bridge), with creator, source page, page-reported dimensions/aspect ratio/duration, and license provenance.
- The official Pexels help page says its media is under the Pexels License and free for personal/commercial use without attribution. This is not treated as permission to enable the clips without checking the downloaded asset and current terms.
- All four entries remain disabled: `direct_video_url=null`, `download_verified=false`, `approved=false`, `user_approved=false`. The bridge candidate is landscape 16:9 and must pass a 9:16 crop review. The existing production background and renderer are untouched until explicit approval.
- Commit: `903dc3902d854edc030a3f74142cd0b886d43605`.

## Archive resilience CI result (2026-11-01)
- Verified run `41313825363` / #151 on `feature/telegram-review-notifications`: conclusion `success`.
- Archive retry regression test passed; the official archive enumerated all 6,236 ayahs; translation, Uthmani candidate corpus, exact surah:ayah join, regression tests, eight distinct-surah candidate selection, one-slot audio preparation, manifest generation, and review-only vertical preview rendering all passed.
- Telegram delivery and delivery-history steps were correctly skipped for the push event. No extra Telegram test was sent. A scheduled/manual run is still required to verify the next real delivery.
- Background rotation remains pending; the four Pexels candidates are staged but not downloaded/verified/user-approved. Existing production renderer still uses the one previously approved Mixkit source.
- Run: https://github.com/samiouess-ux/IslamicTikTokAutomation/actions/runs/41313825363

## Pexels direct-source capture and CI guard (2026-11-01)
- Captured the direct MP4 destinations by following the Pexels page's own Free download link for all four staged candidate clips. Source-page IDs and direct MP4 path IDs match.
- data/background_candidates.json now stores direct URLs, but every candidate remains disabled and unverified. Do not feed these URLs into production manifests or change the active background until actual downloads pass file-integrity/ffprobe checks, vertical crop/contrast review is completed, and the user explicitly approves the selected assets.
- Added tests/test_background_candidates.py and wired it into the existing inventory workflow. It validates the Pexels direct URL path/source page identity and ensures all approval flags remain false.
- Latest CI run at time of writing: 41314687147 / #152, still in progress. Check the final result before closing this task.
- Schedule audit: no schedule event was present at 14:08 UTC on 2026-11-01; next configured cron is 17:00 UTC (18:00 Tunisia). Verify it separately; do not use a push event to claim Telegram delivery.


## Latest successful render checkpoint (2026-11-01)
- Run #153 (41314717304) is green. It produced a distinct-surah review-only preview for Ar-Rahman 55:1–10 (57.65s, 1080×1920, H.264/MP3); audio processing reduced measured inter-ayah silence to 0.24s while preserving internal recitation audio.
- The artifact is available as GitHub Actions artifact 13087310229 (official-quran-audio-inventory-and-probe). The preview is not approved for production and Telegram delivery was skipped because the run was push-triggered.
- Frame sampling confirmed the existing approved Mixkit waterfall design and current Arabic/English layout. The four Pexels candidates are still only staged metadata; no downloads, crop QA, or user approval have occurred.
- Next: keep all approval gates closed; prepare visual previews for the four candidate backgrounds (including a 9:16 crop for the landscape bridge), then ask the user to approve/reject individual assets. Separately verify a scheduled Telegram send and exact history sync. Do not modify main or enable TikTok auto-publishing.


## Background candidate review checkpoint (2026-11-01)
- Run #154 (41315704678) passed, downloaded and ffprobe-validated all four staged Pexels MP4s, created center-cropped 9:16 still previews, and uploaded contact sheet/report in artifact 13087152545.
- Initial visual observations: ocean bright (may need dark overlay); mountain lake visually strong; sunset calm; bridge center crop loses some landscape framing. These are observations only, not approvals.
- Next: add a QA preview stage that composites the actual Quran text panel over each candidate and checks legibility/contrast, plus a short motion preview if practical. Keep all production flags false until user explicitly approves each one. Verify a scheduled (not push-triggered) Telegram delivery separately.


## Run #158 follow-up (2026-11-01)
- CI run `41317460948` passed after fixing the background overlay preview path lookup. Artifact `13087478281` contains the 57.65s Surah Ar-Rahman 55:1–10 review MP4 and the four-background overlay contact sheet/report.
- Review-only status is unchanged: no Quran audio/rendering/production approval, no Telegram send on this push event, and no TikTok auto-publishing.
- Inspect actual rendered frames and validate the complete Arabic ayah text, ayah number, and translation layout; the current background contact sheet samples only one ayah frame and is not sufficient as full-video QA.
- All four Pexels assets remain disabled and unapproved. Ask for explicit user approval individually before enabling any asset.
- After visual QA, separately verify one scheduled Telegram send and history sync; then verify subsequent slots and distinct passage selection. Do not claim three daily videos from the one-video-per-slot implementation until schedule events and sends are evidenced.


## Scheduled Telegram delivery checkpoint (2026-11-01)
- User screenshot confirms the review bot received a video at 18:02 Tunisia time, following the 18:00 scheduled slot: Surah Az-Zukhruf, ayahs 1–7, displayed size 33.0 MB.
- Caption includes Arabic title, hashtags, English description, and the manual-review-only notice. TikTok remains manual; never enable auto-publishing.
- Treat this as one confirmed scheduled delivery only. Still verify the corresponding Actions run, Telegram delivery-history recording/sync, and later scheduled slots. Do not claim all three daily videos are reliable based on one receipt.


## Latest scheduled delivery and history-sync checkpoint (2026-11-01, reconciled)
- Scheduled run #159 (`41329118203`) completed successfully on the active feature branch at 17:02:53 UTC (18:02:53 Tunisia time).
- The engine selected Surah Az-Zukhruf (43), ayahs 1–7, rendered a 60.15-second 1080x1920 H.264/MP3 review video, and Telegram `sendVideo` returned `ok: true` with real `message_id=30` (33.0 MB). The user confirmed receipt in Telegram.
- The workflow recorded exactly the seven delivered ayahs (43:1–43:7) and successfully synced `data/quran_delivery_history.json` to this branch in commit `18bed634d52a90e113dacfa478419788e17cad77`.
- `PROJECT_STATUS.md` has the matching detailed checkpoint. This section supersedes older statements above that say no scheduled MP4 delivery or history sync has yet been verified.
- This proves a real scheduled send and history sync for this slot only. It does not prove three daily slots are reliable over multiple days. Each scheduled slot still creates one video; TikTok remains manual.
- The four Pexels candidates have passed download/ffprobe and overlay-preview preparation, but their final visual review and explicit per-background user approval are still outstanding. Keep all four disabled; the approved Mixkit waterfall remains the only production background.
- Next actions: (1) inspect the actual Quran overlay contact sheet and representative frames for text/number/translation legibility, (2) ask the user to approve or reject candidate backgrounds individually before enabling any, and (3) continue verifying later scheduled slots and exact history sync. Do not add cloud services, bots, or auto-publishing.


## Newly agreed task — Quran opening cover (2026-11-01)
- Implement a short opening cover as the first video image: Arabic Quran label, surah name, and exact selected ayah range, in the approved gold cartouche / dark panel visual style.
- Keep the cover to about 1.6 seconds with a gentle fade; start the original recitation at t=0 so there is no added silence and no change to Quran audio.
- The first frame should be usable as the TikTok cover candidate, selected manually by the user inside TikTok.
- Add tests and inspect a fresh review-only artifact before acceptance. Do not send an extra Telegram test, enable TikTok auto-publishing, change delivery schedules, or modify main.
