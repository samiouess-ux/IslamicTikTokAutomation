## Official Quran archive preflight guard (2026-11-04)
- Created isolated branch `fix/official-archive-preflight` from `feature/telegram-review-notifications`; the active production branch and `main` were not changed.
- Added a preflight check before `RemoteZip` inspects the existing official King Fahd Complex archive URL. It uses HEAD first and falls back to a one-byte ranged GET only when HEAD is unsupported (HTTP 405/501).
- The existing bounded retry policy remains in place. Persistent HTTP errors fail closed with a clear message; no alternate recitation source is selected and no partial inventory is accepted.
- Added unit tests for successful HEAD, unsupported-HEAD range fallback, and HTTP 503 fail-closed behavior.
- Changes are code-only on the isolated branch. No workflow was dispatched, no Telegram message/video was sent, no Cron settings or secrets were changed, and no production catalog/background was modified.
- Validation is pending; do not claim the tests or archive availability have passed until executed. Do not merge into the active branch or trigger a delivery run without separate approval.

## Renderer layout fix verified (2026-11-02)
- Latest active-branch commit `c1cec3fbd246871fbd856542ae95c1bc039d2645` passed the full push-triggered inventory workflow run `41491587024` (conclusion `success`). The previously failing 9:16 preview render now passed, as did background crop/overlay previews and artifact upload.
- The isolated Quran request pipeline run `41491586953` also completed successfully; all its test steps passed.
- Both runs were `push` events. Telegram reservation/send/history/sync steps were skipped by design; no video was sent by these validations.
- Checked `data/quran_delivery_pending.json`: file is absent on the active branch at this checkpoint, so there is no recorded unresolved reservation in repository state.
- Translation layout now permits up to eight lines and smaller fallback fonts while preserving all words; the renderer still fails closed rather than clipping. This validates the automated render path, not final human visual approval.
- Existing cron-job.org schedule remains 04:10, 12:10, 18:10 Africa/Tunis. No schedule, trigger, bot, or `main` changes were made. Next: review the uploaded preview artifact and await the next existing scheduled delivery; do not manually dispatch a test send.

## Latest validation — duplicate-send safeguards and full preview pipeline (2026-11-02)
- GitHub Actions run `41476070230` completed with conclusion `success` on the active branch. It validated the new Telegram reservation and sender safety tests, Tunisia-local Friday detection, weekday-aware candidate preparation, 9:16 preview rendering, background crop preview, and artifact upload.
- This was a push-triggered validation run. Telegram reservation/send/history/sync steps were correctly skipped; no new Telegram video was sent by this run.
- New reservation ledger and sender behavior remain fail-closed: an unresolved pending attempt blocks later automatic sends; transport/5xx ambiguity is not retried. This lowers duplicate risk but does not guarantee atomic exactly-once delivery across GitHub and Telegram.
- Latest known branch HEAD before this documentation checkpoint: `3fa3ad5213c4763e7b667798962677f2b63c97f3`.
- Preserve existing cron-job.org schedule exactly: 04:10, 12:10, 18:10 Africa/Tunis. Do not modify Cron, add another scheduler, or change `main`.
- Next real-world validation is to observe the next already-scheduled Cron-triggered run and verify the pending reservation is pushed before Telegram send, then the confirmed history is pushed and pending file cleared. Do not manually dispatch a send just for testing.

## Latest workflow contract validation (2026-11-02)
- Run `41476070230` passed the new static Telegram workflow safety contract tests, catalog/regression tests, candidate/audio preparation, 9:16 rendering, background crop previews, and artifact upload.
- Telegram reservation/send/history steps were skipped because this was a push event. No video was sent.
- At the latest check, only the post-checkout cleanup step remained in progress; all substantive workflow steps had succeeded.
- This still does not test a real reservation push or Telegram send. The live Cron configuration remains untouched.

## Follow-up validation of Telegram send safeguards (2026-11-02)
- Full push-validation run `41475084051` completed successfully on commit `4c944465b0a3820212b8620073a1838979712739`: catalog and translation checks, new delivery-reservation/sender tests, weekday candidate preparation, 9:16 rendering, background crop previews, and artifact upload all passed.
- Because the run event was `push`, the reserve/send/history/sync steps were skipped by design. No Telegram video was sent by this run.
- Added `tests/test_telegram_workflow_safety.py` to assert that the reservation commit/push occurs before the Telegram send, finalization occurs only afterward, and the unresolved-reservation guard is present. Its test command passed in run `41476070230`; the remainder of that run is still being validated.
- A successful push validation is not a live reservation-push or Telegram delivery test. Keep the external cron unchanged and do not manually dispatch a test send.

## Telegram duplicate-send protection (2026-11-02)
- Sender change: `src/send_telegram.py` no longer retries transport failures or HTTP 5xx responses because Telegram may have accepted a video before the response was lost. An explicit HTTP 429 may be retried once.
- Added `src/quran_delivery_attempt.py` and `tests/test_quran_delivery_attempt.py`. The workflow now reserves the exact candidate and ayah references in `data/quran_delivery_pending.json`, commits/pushes that reservation before calling Telegram, then records confirmed history and removes the reservation only after the sender receives `ok: true` plus a valid `message_id`.
- If the result is ambiguous or history sync fails, the pending reservation remains on the branch. A later workflow_dispatch is blocked before another send. This is intentionally fail-closed and may pause automated delivery until the pending attempt is reconciled against the Telegram chat.
- Regression tests for the new reservation ledger and sender's ambiguous-error behavior passed in GitHub Actions run `41475084051` (commit `4c944465b0a3820212b8620073a1838979712739`). That run is push-triggered: Telegram send/history steps are skipped; it is not a real Telegram delivery test. The full render/background/artifact path passed in run 41475084051; the separate static workflow-contract run 41476070230 is in progress.
- This reduces automatic duplicate risk but does not create an atomic transaction across Telegram and GitHub; do not claim mathematically guaranteed exactly-once delivery.
- External `cron-job.org` remains unchanged: user-confirmed 04:10, 12:10, 18:10 Africa/Tunis. Never add a second scheduler. TikTok publishing remains manual. Translation remains Arabic + Saheeh International English; French is not required.

## Tunisia Friday detection and full weekday pipeline validation (2026-11-02)
- Added `src/tunisian_day_status.py` as the single timezone-aware source for the workflow's local weekday/date/time outputs.
- Added `tests/test_build_quran_tunisian_day_status.py` covering Friday detection at the UTC/Tunisia date boundary, Friday daytime, Monday, and rejection of naive datetimes.
- Updated the workflow to use this helper and run its tests. GitHub Actions run `41473125589` completed **successfully** on `feature/telegram-review-notifications` at `bd3eff8e4343c1d02046e958465cbaf20ad73139`.
- In that run, the complete weekday-aware pipeline succeeded through catalog checks, Tunisia day detection, candidate selection, audio preparation, draft manifest, 9:16 rendering, background crop preview, and artifact upload.
- The run was push-triggered. Telegram send, delivery-history recording, and history sync were correctly skipped; this run did not send a video and is not evidence of another Telegram delivery.
- Friday selection itself remains covered by the builder unit test; the new date helper is independently tested with fixed Friday dates. No real Friday Telegram run has been triggered.
- External `cron-job.org` configuration was not accessed or changed. Its user-confirmed slots remain 04:10, 12:10, and 18:10 Africa/Tunis. TikTok posting remains manual. English Saheeh International remains the agreed translation; French is not required.
- Remaining delivery-safety concern: Telegram `sendVideo` and GitHub history commit are two separate systems. If Telegram accepts a video but the subsequent history push fails, an automatic retry could potentially send a duplicate. The current workflow has a per-branch concurrency group, but that alone does not make the cross-system send+commit atomic. Do not claim exactly-once delivery until this recovery window is addressed and tested.

# Project status — IslamicTikTokAutomation

## Verified Telegram MP4 delivery and exact-history correction (2026-11-01)
- Controlled live test run `41309830990` completed successfully. The existing Telegram bot accepted the actual MP4 through `sendVideo` with `ok: true` and `message_id=27` (28.1 MiB). This is a real delivery, unlike mocked tests or artifact uploads.
- The delivered review video is Surah Hud (11), ayahs 1–2, 40.046 seconds, 1080×1920, H.264 video + original MP3 recitation. The source candidate contains 123 ayahs, but the audio selector correctly chose only the first two complete ayahs under the 65-second limit.
- Audit caught a delivery-history bug: the recorder had marked the full 123-ayah source candidate as delivered instead of the two ayahs actually included in the MP4. The history was corrected to only `11:1` and `11:2`.
- Fixed `src/record_quran_delivery.py` to require the audio report and record only its exact `selected_verses` contiguous prefix. Updated the workflow to pass that report and added regression tests proving a two-ayah selection never marks the remaining candidate ayahs as delivered.
- The updated history and code are on `feature/telegram-review-notifications`. Test run `41310129350` passed the catalog/test phase including the new delivery-history regression tests; run `41310167242` is checking the workflow-file update.
- Do not send this same test video again. It is already in Telegram for the user's manual review. TikTok publishing remains manual.
- A one-off live send is proven; automatic scheduled delivery at all three daily slots is still not proven. Earlier schedule query found no scheduled runs, so do not declare the daily schedule operational yet.

Last updated: 2026-11-01

## Caption variation update (2026-11-01)
- Updated the scheduled Telegram caption builder to include the exact ayah range in English and retain the Arabic surah/range caption.
- Added three rotating, topic-relevant Arabic/English hashtag sets selected deterministically per passage, rather than repeating the same two tags on every video.
- Workflow change commit: `f46f7912e1b8deaddef3e725ec2151f7b87fab95`.
- The schedule remains 04:00, 12:00 and 18:00 Tunisia time (one video per slot). Telegram MP4 end-to-end delivery still needs a scheduled/dispatch run with a real Telegram message ID.
- Background limitation identified: the current preview renderer still uses one approved moving-video source; palette accents vary, but full scene/background rotation is not yet implemented. Do not claim background variety is complete or introduce unreviewed external assets.

## Telegram delivery confirmation hardening (2026-11-01)
- Tightened `src/send_telegram.py`: Telegram `ok: true` is no longer sufficient by itself; the response must also contain a positive integer `message_id` before the sender exits successfully.
- Added a regression test proving an `ok: true` response without `message_id` is rejected. The workflow therefore cannot record delivery history on an incomplete Telegram response.
- Commits: sender `6b159c9f4703fb52f6998a8de62fe4206a0fe91b`; regression test `eb4a6d1b585023bfee08014e83147f9e48083cfd`.
- This is code/test hardening only. It does **not** prove a real MP4 has reached Telegram; end-to-end delivery remains unverified until a scheduled run logs a real message ID.

## Autonomous agent plan and release gate (2026-11-01)
- The active work roles, execution order, known blockers, and acceptance criteria are maintained in `AGENT_WORK_PLAN.md`.
- This plan is authoritative for the next implementation steps on `feature/telegram-review-notifications`; it does not create separate paid agents or external infrastructure.
- **Language is confirmed: Arabic + Saheeh International English. Keep English; French is not required and must not be reintroduced.** The existing translation catalog, renderer, and workflow already use English.
- Current readiness remains **not verified** because an actual scheduled MP4 delivery to the original Telegram bot has not yet been evidenced.
- Do not declare the engine ready until a distinct-surah MP4 passes render checks at <=65 seconds, Telegram confirms `sendVideo` with a message ID, and delivery history is committed only afterward.
- TikTok publishing stays manual. Keep all changes on this branch; never modify `main`.


## Latest delivery-slot correction and render fixes (2026-11-01)
- This section supersedes older schedule notes below: the required schedule is **one distinct Quran review video at each Tunisia slot: 04:00, 12:00, and 18:00** (GitHub cron: `0 3,11,17 * * *` UTC). GitHub may delay scheduled starts under load.
- Each scheduled run prepares one video only; it must not expect a three-video batch.
- Fixed `src/build_quran_draft_manifests.py`: its old minimum of two manifests contradicted the one-video-per-slot workflow. It now accepts one prepared distinct-surah draft while retaining all review/production gates. Added a one-manifest regression test.
- A subsequent run exposed a long Saheeh translation that exceeded the renderer's fixed five-line layout. Updated `src/render_quran_review_previews.py` to step down the translation font size while preserving every word; it refuses clipping if the text still cannot fit. Added a wrapping regression test.
- Relevant commits: `99fd01bba9a149ec136398d12f36127fe0503eb1` (single manifest), `0eeabe3c07fa4c1dd92bd4478d1a9f8225059bad` (single-manifest test), `78687c5988f69fc7d21c0d666e0f3dd47ad9082c` (translation fitting), `ff1cf0e2955fc5a2e9ea8cddd3d80521826473a1` (translation test).
- Test workflow `test-quran-request.yml` run `41289938456` passed. Full scheduled-pipeline validation run `41289938290` is still being checked; do not declare the renderer or Telegram delivery verified until it completes.
- Telegram delivery is not proven by push-triggered tests. The user confirmed a Telegram test message, but the first scheduled MP4 delivery still needs an actual Telegram API confirmation and a successful delivery-history push.
- TikTok publishing remains manual-only; never enable automatic TikTok publishing. Do not modify `main`.


## Latest verified run evidence (2026-11-01)
- GitHub Actions run `41289938290` completed successfully through Quran-wide inventory, catalog joins, tests, one distinct-surah audio preparation, draft manifest, 9:16 preview render, and artifact upload (artifact `13076309641`).
- It rendered a non-Ash-Sharh review candidate: Surah Muhammad (47), ayahs 16–17, file `quran_s047_016_017_REVIEW_ONLY.mp4`.
- Telegram step 18 was **skipped** because this was a push-triggered run. No MP4 delivery is proven by this run. The successful mocked sender test is not a real Telegram send.
- See `AGENT_WORK_PLAN.md` for the four operational roles, acceptance criteria, and next execution order.

## Project goal (current)
Prepare **three distinct Quran videos per day** first. Each video contains the Quran in Arabic with authentic recitation and a paired English Saheeh International translation. Select different surahs/passages; do not repeat the Ash-Sharh prototype as the default. Each clip must contain complete consecutive ayahs and stay at or below 65 seconds.

The engine sends the three review-only MP4s and ready-to-use captions to Telegram. The user personally reviews, downloads, and publishes manually to TikTok. TikTok auto-publishing is permanently disabled for this workflow. Dua and dhikr are later optional content categories; their absence must never block Quran production.

## Agreed video style
- Format: vertical 9:16, target 1080x1920, 30 FPS.
- Arabic Quran text is the main visual element and must be larger.
- English translation appears underneath in a noticeably smaller font.
- Quran recitation is required; music is not allowed.
- Vary backgrounds and layouts across a curated set of calm, respectful designs; do not reuse the same background by default. Select a suitable background for each video.
- Recitation must be authentic and match the displayed verses exactly.
- Never invent Quran text, hadith, attribution, source, or translation.

## Caption rules
- Include the surah name and exact verse number/range (or identify a complete surah).
- Prepare Arabic and English captions with relevant, restrained hashtags.
- Do not display or mention the reciter's name in the video or public caption, per user preference.
- Keep audio provenance and reuse-permission records internally for compliance; these are not public captions.

## First test video
Theme: hope and ease after hardship.
- Surah Ash-Sharh (94), verses 5–6.
- Arabic: فَإِنَّ مَعَ الْعُسْرِ يُسْرًا ۝٥ إِنَّ مَعَ الْعُسْرِ يُسْرًا ۝٦
- Language choice updated by user: English replaces French (not an additional third language).
- English translation: Sahih International, wording verified for both verses against Quran.com / Quranic Arabic Corpus; retain the exact verse-specific wording.
- Proposed background: peaceful natural scenery, gently animated; Pexels candidate is documented in content/first_video.json.

## Current technical state
- Arabic + English output configuration is in place.
- Official King Fahd Complex recitation audio was extracted and the exact verses 94:5–6 clip was reviewed and approved by the user.
- A Mixkit nature background was reviewed and approved by the user.
- First test video render completed successfully in GitHub Actions: run `41165699435`, artifact `13029197609`, output `ash-sharh-94-5-6-review.mp4` (1080×1920, 30 FPS).
- The first render is a successful prototype, not yet a reusable multi-surah production pipeline.
- No automatic publishing is enabled.

## Next steps
1. Turn the successful one-off render into a reusable renderer driven by a content manifest.
2. Support full-surah, verse-range, and single-verse formats.
3. Add caption generation fields: surah name, verse range, Arabic and English descriptions, and hashtags; exclude reciter name from public output.
4. Add a curated rotating set of approved backgrounds and design layouts.
5. Keep every generated video and caption in a review stage; no publishing without explicit user approval.

## Non-negotiable constraints
- Prefer free/open-source tools; no upfront paid services.
- Work step by step and test each phase.
- Do not publish automatically.
- Do not use music.
- Do not use recitation audio without documented reuse permission for the exact recording.
- Do not make repository changes beyond the agreed project scope.

## Research checkpoint (2026-10-31)
- Language decision reaffirmed on 2026-11-01: Arabic + Saheeh International English only. Ignore earlier French exploration; do not change the translation pipeline to French.
- Candidate background source: Pexels videos. Its official license/help pages state that videos can be used and modified for commercial projects, subject to restrictions and third-party rights. Save the specific asset page and creator details when selecting a clip.
- Recitation audio: reciter selected by user — Maher Al-Muaiqly (Hafs). The official King Fahd Complex page grants free public-use permission for the listed recordings in apps, websites, broadcast channels, and private/institutional works inside and outside Saudi Arabia. The official reciter page lists full-surah and verse-by-verse downloads. The exact Surah Ash-Sharh file has not yet been downloaded, listened to, or technically checked; do not embed it until that check is complete.
- User's initial preferred reciters: Islam Sobhi or Yasser Al-Dosari. No reuse permission has been verified for their recordings. Quran.com states it cannot grant reuse rights; rights belong to the reciter or rights manager. A public reuse-permission candidate was found from the King Fahd Complex: Maher Al-Muaiqly (Hafs), with Surah Ash-Sharh listed on his official recitation page. User approval is still needed before switching reciter.
- The Pexels ocean-and-mountains clip by Engin Akyurt remains a candidate only; it has not been downloaded or approved.


## Mobile-only workflow decision (2026-10-31)
- User clarified they are working with ChatGPT from a phone and do not have Codex or a computer available. Do not instruct them to run local commands, use Android Studio, or upload files manually as the default path.
- Preferred approach: build and operate the project from the existing GitHub repository using cloud execution where feasible (e.g. GitHub Actions), with ChatGPT making repository changes and checking workflow results.
- Audio source remains the King Fahd Complex official Maher Al-Muaiqly Hafs collection. Its public-use permission is documented on the Complex site. The official page currently exposes downloads for the complete surah archive and complete verse archive; a direct individual Surah 94 URL has not yet been verified.
- The complete-surah archive is about 1.26 GiB. Avoid downloading it unnecessarily. A third-party page listing a separate Surah 94 MP3 is not accepted as a substitute until reuse rights for that exact recording are established.
- The official Surah Ash-Sharh MP3 has been extracted in GitHub Actions. The user listened to it and confirmed it is the complete surah and the audio sounds good. This is user-confirmed listening, not an independent audio analysis by ChatGPT. No video has been generated. Keep auto-publishing disabled and user approval mandatory.


## Cloud runner setup (2026-10-31)
- Added `.github/workflows/cloud-runner-check.yml` in commit `6db478ea2fe6be7b1e9c73d9c37f072f27fe7cea`.
- The workflow is triggered by a push changing that workflow file on `main`, and also supports manual `workflow_dispatch`.
- It checks out the repository and reports Python/FFmpeg availability on a GitHub-hosted Ubuntu runner. It does not download or process audio.
- The GitHub connector available in this session can create/update repository files and inspect some workflow run data, but it does not expose a workflow-dispatch action or general workflow-runs listing. The run status therefore still needs to be confirmed from GitHub's Actions page before building the audio-processing workflow.
- Official Maher Al-Muaiqly Hafs collection page publishes the surah-archive SHA-256: `1F99418CD52D2E84BD144A751FBD01BAC8ACBFCEF4CEF62CF792607AAEE466D28` (verify exact value against the official page before use); verse-archive SHA-256: `3EDCC70407F9D19C972C002C69A43CC245A62A0FCC497D3C719406A69965E18E`. The page provides full-surah and verse-level archive download controls; no individual Surah 94 URL is confirmed yet.


## Official Surah Ash-Sharh audio extracted (2026-10-31)
- GitHub Actions run: `41163898712` completed successfully.
- Source: official King Fahd Complex Maher Al-Muaiqly Hafs archive; archive entry: `sura/10-094D00-A08.mp3`.
- Extracted only that MP3 remotely; no full archive download was required.
- Extracted file size: 680,837 bytes. FFprobe duration: 56.565750 seconds.
- Extracted MP3 SHA-256: `78d40c55bfece24bdc738a88408264f3ef94f31e05dda77228f05d2de1e403b1`.
- GitHub Actions artifact: `official-maher-ash-sharh-audio`, artifact ID `13027479483`, expires 2026-11-07.
- Extraction and technical metadata check succeeded. The recording has NOT yet been listened to and checked against verses 94:5–6; therefore it is not yet approved for video production.


## User audio review (2026-10-31)
- User listened to the extracted official Maher Al-Muaiqly Hafs recording and confirmed: it is the complete Surah Ash-Sharh and the audio is good.
- Treat the recording as approved for use in the first test-video workflow, based on the user's listening confirmation.
- Technical extraction details and SHA-256 remain recorded above. Do not claim ChatGPT independently listened to the recording.


## Official verse-level audio extracted (2026-10-31)
- GitHub Actions run: `41164756151` completed successfully; all extraction, concatenation, and artifact-upload steps succeeded.
- Source: official King Fahd Complex Maher Al-Muaiqly Hafs verse archive.
- Extracted the exact official archive entries for Surah Ash-Sharh 94:5 and 94:6 individually, then joined them in order using FFmpeg stream copy (no re-encoding).
- Combined MP3: `maher_almuaiqly_ash_sharh_verses_5_6.mp3`; duration reported by FFprobe: 15.882449 seconds; size: 111,403 bytes; SHA-256: `3e2a91674ce2ee604885e06fba0ee67c425e5dbece54cc3256803e3b5f02c5a0`.
- Audio stream: MP3, 22,050 Hz, stereo, 56 kb/s.
- Artifact: `maher-ash-sharh-verses-5-6-review`, ID `13028735937`, available until 2026-11-07.
- The individual verse files and combined clip are available in the artifact. The user listened to the exact combined 94:5–6 clip and confirmed that the sequence is correct. The verse-level audio is now approved for the first test video.
- The previously listened-to complete-surah recording remains approved by the user's earlier confirmation, but this exact verse-level cut is pending review.

## First render completed (2026-10-31)
- GitHub Actions run `41165699435` completed successfully.
- Artifact `ash-sharh-first-video-review`, ID `13029197609`.
- Output `ash-sharh-94-5-6-review.mp4`, 1080×1920, 30 FPS.
- The user reacted positively to the overall test render. Detailed review remains a separate approval step before publishing.
- Approved background candidate: Mixkit “Waterfall Between Green Hills”, 720×1280 source, upscaled during rendering. User approved its representative preview.

## Reusable design and caption rules committed (2026-10-31)
- `DESIGN_SPEC.md` now defines full-surah, verse-range, and single-verse formats; background/layout rotation; caption requirements; and no public reciter attribution.
- `content/first_video.json` records the approved Mixkit waterfall background and bilingual caption draft for Ash-Sharh 94:5–6. Internal audio provenance remains recorded.
- Commits: design `16c52f976dc546e296da46b3829bd1ee70db50e7`; manifest `1a6f108ba14d6057ba6b8a6d6ee8f6b6f016cf18`.

## Agreed content and caption behavior (2026-10-31)
- Support a complete surah, a selected verse range, or a single verse depending on the content.
- Rotate among multiple calm backgrounds and layouts; avoid repeating one background by default.
- Every video should have a ready-to-review Arabic and English caption that names the surah and verse range (or complete surah) and includes relevant hashtags.
- Do not show or mention the reciter's name in the video or public caption, per user preference. Retain rights/provenance details internally.
- User approval remains mandatory before publishing; auto-publishing stays disabled.


## Current approved design checkpoint (2026-10-31)
- The user approved the preview generated by GitHub Actions run 12 (`41170065024`), commit `fb519f49ff61c7feae83120b332bfaa28b2ae085`.
- Approved visual reference: larger bold gold Arabic surah title in an ornate pointed Islamic cartouche with rosette details; larger bold gold verse numbers in separate ornamental medallions; exact white Quran text remains unchanged; English translation remains smaller below.
- The renderer in `src/render_video.py` implements this reference. The workflow completed successfully and produced a review artifact. User approved the appearance.
- Next phase: retain this visual identity while preparing reusable layout/background variations for single-verse, verse-range, and full-surah manifests. Inspect current code and test changes incrementally.
- No video has been published. Automatic publishing remains disabled; explicit user approval is mandatory.

## Handover checkpoint — Telegram review workflow and Friday plan (2026-10-31)
- Active project repository: `samiouess-ux/IslamicTikTokAutomation`.
- Only work on branch: `feature/telegram-review-notifications`. Do not modify `main`.
- The current review workflow is `.github/workflows/render-second-ash-sharh-review.yml`. It is a specific Surah Ash-Sharh 94:1–8 workflow, not yet a general daily content scheduler.
- The workflow sends the rendered MP4 to Telegram with Approve and Reject buttons, then polls for the decision. Approve records approval for review only; it does not publish. Reject records rejection. User confirmed receiving the buttons and rejecting a video; run logs confirmed `Telegram review decision: rejected` and `Review result: rejected`.
- No TikTok publishing is implemented or enabled. Never describe approval as publication.
- Important implementation caution: do not add a cron schedule to the existing Ash-Sharh workflow as-is; it would repeatedly generate the same fixed content. First create reusable content selection/queue support or a separate Friday workflow.
- User wants a dedicated Surah Al-Kahf video every Friday, planned delivery time 08:00 Tunis local time, for Telegram review. This is an agreed plan, NOT yet implemented or scheduled.
- User explicitly wants varied backgrounds and layouts: rotate among an approved set of calm, respectful backgrounds; avoid using the same background repeatedly, especially in consecutive videos. The renderer/layout rotation still needs implementation and testing.
- Existing visual checkpoint remains the approved gold surah title in an ornate Islamic cartouche, gold verse-number medallions, white Arabic Quran text, and smaller English translation.
- Before implementing Friday automation: choose and verify the exact Al-Kahf passage/content strategy, exact matching permitted recitation audio, translation, background asset/license, and ensure Telegram polling runs cannot overlap (concurrency protection / callback isolation).
- GitHub Actions cron uses UTC. Tunisia is UTC+1 for this checkpoint; an 08:00 Tunis run corresponds to 07:00 UTC. Reconfirm timezone rules if scheduling at a later date.
- Next safe step: inspect the current branch head, workflow, renderer, and content manifests; then implement one small change at a time and run tests. Keep auto-publishing disabled.
- This section is the handover source of truth for resuming after a chat/account change. Update it after each meaningful implementation or test result; distinguish confirmed behavior from plans and unverified work.


## Daily content plan clarification (2026-10-31)
- User clarified the daily target is **three varied Islamic videos per day**, not one Arabic Quran video plus one English Quran video.
- Quran videos remain in Arabic with a verified translation shown alongside/below the Arabic text (English translation may be used; do not create an English-only Quran recitation/video as the default).
- The three daily slots should rotate naturally among:
  1. Quran recitation in Arabic with verified translation.
  2. Authentic morning/evening adhkar and duas (choose according to the day's slot where practical).
  3. Another verified Islamic reminder: Quran passage, dua, dhikr, or other sourced content.
- This is a varied content mix, not a rigid requirement that every day contain exactly one of each category. Avoid repetitive topics, backgrounds, and layouts.
- Every Quran verse, translation, dua, hadith, attribution, and source must be checked; never invent or paraphrase sacred wording as a quotation. Record reliable source/provenance internally.
- Deliver three separate 9:16 MP4 files to Telegram, each with its own ready-to-use caption and relevant hashtags, for the user to upload manually to TikTok.
- Do not enable the daily schedule yet. First implement reusable content selection and rendering, then test three distinct videos and confirm quality and Telegram delivery. Automatic TikTok publishing remains disabled.


## Telegram delivery implementation checkpoint (2026-10-31)
- Inspected the active branch and confirmed that Telegram delivery in `.github/workflows/render-second-ash-sharh-review.yml` was intentionally disabled with `if: false`; the latest Ash-Sharh 94:1–8 render succeeded, but its Telegram step was skipped. Do not claim that run delivered a video.
- Added `src/send_telegram.py` as a reusable, review-only MP4 sender. It requires `TG_BOT_TOKEN` and `TELEGRAM_CHAT_ID` from GitHub Secrets, rejects empty/missing credentials, missing/empty files, videos above the configured 50 MiB safety limit, and captions above Telegram's 1024-character limit. It sends the MP4 and bilingual caption; it has no TikTok publishing capability.
- Added `tests/test_send_telegram.py` covering bilingual review captions, caption length, missing credentials, and oversize rejection before any network call.
- Updated `.github/workflows/render-manifest-video.yml` with a manual `send_to_telegram` boolean input (default true for manual dispatch) and a Telegram send step after successful render validation and artifact upload. Push-triggered workflow runs do not request dispatch inputs, so Telegram remains skipped on code pushes; this avoids accidental duplicate sends during development.
- Commits on `feature/telegram-review-notifications`: sender `dc10611606f780ccff8859d6248aeafcad93793c`; tests `769022e817cc68fe6624e019a0b2ed02e5eca00a`; workflow integration `3061a31a39177f69cd4482d4f68acbb2f94c6d9c`.
- GitHub Actions run `41235405617` completed successfully and produced artifact `ash-sharh-94-1-8-video-review` (artifact `13055730388`, 34,101,084 bytes). Its Telegram step was skipped because the dedicated Ash-Sharh workflow still contains `if: false`; this is not proof of Telegram delivery. Run `41235407692` completed successfully: all render/validation/artifact steps passed and produced artifact `islamic-video-review` (ID `13055525766`, 48,363,815 bytes). Its Telegram step was skipped as expected for a push-triggered run. Run `41235405611` remained in progress at last check. A success-path Telegram sender unit test was added in commit `177be619d997da42ca353ecb943e08296d383136`; its push-triggered runs are `41235591309` and `41235591321` and must be checked for final conclusions.
- Telegram delivery has NOT yet been proven end-to-end. The actual send requires the two GitHub Secrets to exist and a deliberate manual workflow dispatch with a reviewed manifest. TikTok publishing remains manual and disabled.
- Next: confirm the three Actions runs, fix any failures, then perform one controlled Telegram send using an already approved video and confirm Telegram's success response. Do not send draft/unreviewed content or schedule daily/Friday runs yet.

- Follow-up sender test commit: `177be619d997da42ca353ecb943e08296d383136`; adds a mocked successful Telegram API response test and asserts the request contains the MP4 bytes and review-only caption.

- Follow-up check (2026-10-31): run `41235405611` also completed successfully. The sender-test runs `41235591309` and `41235591321` were still in progress at the latest API check; no failures were reported, but their final conclusions remain unverified.
- The available connected GitHub actions can inspect runs, artifacts and logs, but do not expose a workflow-dispatch action. A real Telegram delivery therefore still needs one manual dispatch from GitHub Actions; do not enable Telegram sending on push events to work around this limitation.
- Phone-friendly manual send (only after the current CI runs finish successfully): open repository > Actions > “Render manifest video for review” > Run workflow; keep branch `feature/telegram-review-notifications`, manifest `content/second_video_ash_sharh_94_1_8_draft.json`, `use_rotation=false`, and `send_to_telegram=true`; tap Run workflow. This requires repository secrets `TG_BOT_TOKEN` and `TELEGRAM_CHAT_ID`. Never paste either secret into chat.


## Current authoritative checkpoint — Telegram sender CI and production readiness (2026-10-31)
- The daily target is three varied Islamic videos, not two language variants. See the "Daily content plan clarification" and current handoff.
- Latest completed CI runs on commit `177be619d997da42ca353ecb943e08296d383136`: manifest workflow `41235591309` and Ash-Sharh review workflow `41235591321` both completed successfully. The manifest workflow ran the full unittest suite, including `tests/test_send_telegram.py`; the dedicated Ash-Sharh render and its tests also passed. Telegram delivery steps were skipped on these push-triggered runs.
- The Telegram sender has a mocked success-path test as well as safeguards for missing secrets, >50 MiB videos, and overlong captions. A mocked API success proves request construction and response handling only; it is not a real Telegram delivery.
- A follow-up change adds regression tests for selecting three distinct approved manifests and failing closed when fewer than three are available. Its manifest workflow's full unit-test step has passed in run `41236627114`; final rendering and MP4 validation are still in progress.
- Current content inventory has three Quran JSON files, but they are not three rotation-ready items: the first test manifest is a user-positive prototype with approved audio/background but is not marked `rotation_approved`; Al-Ikhlas is explicitly a candidate with unapproved audio and background; Ash-Sharh 94:1–8 is a review draft. There are no approved dua/dhikr manifests.
- `src/render_video_scenes.py` currently renders Quran manifests only and explicitly rejects dua/dhikr. Do not claim multi-category rendering or three-video daily batch production is ready.
- No actual Telegram send has been confirmed. A deliberate manual dispatch of `Render manifest video for review` with an appropriately reviewed manifest and `send_to_telegram=true` is still required; repository secrets `TG_BOT_TOKEN` and `TELEGRAM_CHAT_ID` must be configured privately in GitHub.
- Daily and Friday schedules remain disabled. TikTok publishing remains manual and disabled.

- Follow-up check: run `41236627114` has passed manifest selection, Quran structure/reference checks, the full unittest suite (including the new three-item batch tests), and exact Quran text validation; video rendering is still in progress. Run `41236627093` has passed its audio rebuild, background download, Quran validation, and automated tests; its MP4 render is still in progress. Neither run has yet completed or uploaded the new artifacts.


## Rendering performance adjustment (2026-10-31)
- Runs `41236627114` and `41236627093` both remained active for an extended period in their MP4 render step, with preceding validations and tests completed. The connector could not retrieve their live log blobs, so the exact runtime bottleneck is not proven.
- Inspection found an unnecessary FFmpeg `deshake` filter on the approved moving nature background. Removed it in commit `2c7684e57f46739d764a4b7ff25623172b04cba1`; the natural background motion remains intact and the visual layout is unchanged. This is a targeted performance hypothesis, not yet a confirmed fix.
- The new push-triggered render runs must complete and produce technically validated MP4 artifacts before the change can be considered successful. Telegram sending remains skipped on push events.


## Render completion update (2026-10-31)
- The earlier Ash-Sharh render run `41236627093` eventually completed successfully on the pre-optimization commit `3339853714fda6da77b8394ad8567130aa21bb3d`. Its render, artifact upload and post-job steps passed; Telegram was skipped as expected for a push. Artifact `ash-sharh-94-1-8-video-review`, ID `13055821597`, size 34,107,653 bytes, expires 2026-11-07.
- The paired manifest run `41236627114` was still in its render step at the latest check.
- The no-deshake optimization commit `2c7684e57f46739d764a4b7ff25623172b04cba1` triggered new runs `41236886998` and `41236886984`. Both were in progress during setup/install at the latest check; no result yet.
- The old successful Ash-Sharh artifact confirms the renderer can complete, but does not test the no-deshake optimization. Real Telegram delivery remains unverified.


## Verified optimized render results (2026-10-31)
- Both workflows on renderer optimization commit `2c7684e57f46739d764a4b7ff25623172b04cba1` completed successfully:
  - Manifest review run `41236886984`: all Quran validation, regression tests, render, MP4 technical checks and artifact upload passed; Telegram was skipped on push. Artifact `islamic-video-review`, ID `13056036545`, 47,548,029 bytes.
  - Ash-Sharh 94:1–8 run `41236886998`: audio rebuild, background preparation, Quran validation, tests, render and artifact upload passed; Telegram was skipped because the dedicated workflow remains paused. Artifact `ash-sharh-94-1-8-video-review`, ID `13055697994`, 33,641,467 bytes.
- Downloaded and independently inspected the optimized manifest artifact. FFprobe reports 1080×1920, 30 fps, video and audio streams, duration 62.8 seconds; file size 47,562,889 bytes. A representative frame retains the approved gold cartouche, white Arabic verse, separate gold verse medallion, smaller English translation and approved waterfall background.
- The matching pre-optimization manifest artifact was 48,372,661 bytes and took about 3m52 from workflow start to completion; the optimized run took about 1m45. Runner timing varies, but the new revision completed faster in this observed pair. The deshake removal is now validated as a working change.
- The three-item batch-selection regression tests also passed in both optimized manifest workflow and Ash-Sharh workflow test steps.
- No real Telegram send has occurred; push workflows correctly skipped delivery. No daily/Friday schedule or TikTok publishing is enabled.


## User delivery preference — authoritative clarification (2026-10-31)
- User explicitly rejected a workflow where they must open GitHub Actions and manually dispatch each video to Telegram.
- Intended operation: once the production engine and schedule are ready, it generates the planned videos and sends each finished MP4 directly to the user's Telegram automatically. The user downloads the videos from Telegram and uploads them to TikTok manually.
- Do not ask the user to run a GitHub Actions manual dispatch as the normal delivery process. Manual dispatch may remain only as an internal/one-time diagnostic while testing, not as a recurring user task.
- TikTok publishing must remain manual; no TikTok API publishing or automatic posting.
- This preference does not mean enabling an incomplete daily schedule now. First finish three distinct, validated content outputs (Quran plus authentic dua/dhikr/reminders), verify real Telegram delivery end-to-end, then enable the intended automated schedule and Telegram delivery. Until those gates pass, schedules stay disabled.


## Background variety — user reaffirmation (2026-10-31)
- User explicitly reaffirmed that generated videos must not keep using the same background.
- Rotate through a curated library of multiple user-approved, rights-verified backgrounds (e.g. nature, sky, sea, architecture) and avoid repeating the immediately previous background whenever another eligible background exists.
- Keep background choice calm and respectful, preserve Quran/text readability, and vary backgrounds independently of the approved visual identity.
- Never select an unreviewed or rights-unverified asset merely to force variety. If no eligible alternative exists, fail safely or reuse only according to an explicit fallback rule rather than silently claiming rotation.


## Quran variety safeguard and verified inventory (2026-10-31)
- User requests varied surahs and ayah selections while preserving every approved audio and visual rule.
- `src/render_video_scenes.py` already supports Quran manifests with one verse per timed screen, preserving verse order and paired English translation; it currently rejects non-Quran content.
- `src/validate_quran_text.py` performs exact Unicode comparison against `data/reference/quran_text_uthmani.json` and fails closed for missing, changed, duplicated, or reordered verses.
- The reviewed reference snapshot currently covers only Ash-Sharh 94:5-6 and Al-Ikhlas 112:1-4. The Ash-Sharh 94:1-8 approved reference exists separately and is used by its dedicated validation path.
- Al-Ikhlas remains an unapproved candidate: exact audio rights/recording and a matching user listening review are not yet complete. Do not rotate it into production.
- Do not invent or auto-select new surahs/ayahs. Add a passage to production rotation only after exact Arabic reference, sourced translation, matching permitted recitation, and user review are all documented.
- Current background catalog file is not present in the repository tree; the renderer reads the approved background URL from each manifest. Do not claim automated catalog-based background rotation is active.
- Daily scheduling and Telegram delivery remain disabled pending complete approved content and real delivery confirmation.


## Full Quran rotation and duration requirement (2026-10-31)
- User clarified that the engine must work across the full Quran, not remain tied to the Ash-Sharh prototype. The approved first video is a reusable design/render example only.
- Target coverage: all 114 surahs and all ayahs, rotating across varied single-ayah or contiguous-ayah clips. Each clip must be no longer than 65 seconds.
- Implemented in `src/render_video_scenes.py`: a hard fail-closed duration guard rejects source audio longer than 65.000 seconds. It does not yet automatically select or split Quran passages from a full-corpus inventory.
- Added `tests/test_render_video_duration.py` for 65-second boundary, shorter clips, over-limit rejection, and invalid durations. CI should run this with the full test suite.
- Full-Quran automatic selection is NOT yet production-ready: the checked-in exact Uthmani reference covers only a small sample; the official verse archive has an identified URL and individual extraction has been demonstrated for Ash-Sharh, but a verified Quran-wide mapping/selection pipeline and sourced translation corpus are not yet integrated.
- Next engineering milestone: create a Quran-wide catalogue/selector that uses trusted text and translation datasets plus the official verse archive's exact entry map; select contiguous verse ranges using actual processed audio durations with a 55–60 second target and 65-second hard cap. Never truncate/speed up a verse or synthesize missing recitation.
- Keep schedules and automatic Telegram delivery disabled until the full-corpus selector, 3 varied sample renders, and a real Telegram delivery have been tested.


## Quran-wide archive inventory automation (2026-10-31)
- Added `src/build_official_audio_inventory.py` and `.github/workflows/build-quran-audio-inventory.yml` to enumerate the official King Fahd Complex Hafs verse archive and validate the mapping against all 6,236 verses across 114 surahs.
- Workflow run `41238698032` completed successfully. Artifact `official-quran-verse-audio-inventory` (ID `13056259931`, 42,188 bytes) was downloaded and inspected: JSON contains 6,236 unique verse keys and archive-member paths. The filename mapping is confirmed; it is not a listening, translation, or rights approval.
- This step builds an internal verse-to-official-audio archive index; it does not yet mean every recording has been individually listened to, nor does it complete the trusted Arabic text/translation catalogue or the automatic 65-second passage selector.


## Official Quran audio inventory confirmed and passage preparer added (2026-10-31)
- Confirmed successful inventory workflow `41238698032` and inspected artifact `13056259931`; JSON reports exactly 6,236 mapped verses across the 114-surah canonical counts. It records Hafs and the internally retained reciter/source metadata.
- Added `src/prepare_official_quran_passage.py`: reads the inventory, downloads only contiguous official verse MP3s from the archive, probes each actual duration with ffprobe, and selects complete consecutive ayahs toward 60 seconds without exceeding 65 seconds. It never speeds up or trims the recitation. It explicitly labels its output as still requiring text, translation, rights, and user review.
- Added `tests/test_prepare_official_quran_passage.py` for contiguous packing, hard-cap handling, missing entries, and invalid durations. The CI runs triggered by these commits are pending; do not mark the new code tested until they finish.
- Important remaining blockers: the checked-in Uthmani reference still has only six verses; the verified Sahih International translation corpus is not Quran-wide; exact archive mapping does not by itself prove the usage terms for every file; and no new recording beyond the previously user-reviewed Ash-Sharh 94:5-6 clip has been individually listened to and approved.
- Do not enable Quran-wide rotation, three-video daily scheduling, or Telegram automatic delivery until those blockers and the dua/dhikr content/rendering gates are closed and a real Telegram send is confirmed.


## Full translation source integration in progress (2026-10-31)
- Added `src/build_quran_translation_catalog.py` to retrieve the Saheeh International edition (`en.sahih`) from AlQuran Cloud, preserving translation wording verbatim and validating all 114 surahs / 6,236 ayahs with exact per-surah counts and no missing, duplicate, or empty entries.
- The API's public documentation identifies `en.sahih` as Saheeh International. Its terms say translations are contributed by rights-holders or sourced from public-domain editions and require translator attribution when republished; commercial reuse of this specific edition still needs confirmation before monetized distribution.
- The workflow now builds the translation corpus alongside the official archive index and duration-probed candidate audio. The latest workflow run after switching to a single full-corpus request is `41239290344`; wait for its result before treating the translation corpus as validated.
- New tests cover full-surah shape, exact verse coverage, duplicates, missing rows, and empty text. The test workflow triggered on commit `246a713058b5cac352b4c6a88d0313d4c8d9e4d9` is still running at the latest check.
- Source references: AlQuran Cloud API documentation and terms are recorded in the script metadata. The Arabic Uthmani reference corpus remains a separate outstanding task; the existing six-verse reviewed snapshot is not yet expanded.


## Quran corpus verification checkpoint (2026-10-31)
- GitHub Actions run `41239290344` completed successfully on feature branch commit `df8b8e7df379d3eec857512c6ad8d42388285243`.
- The official King Fahd Complex audio archive mapping validated all 6,236 verse entries across 114 surahs.
- The Saheeh International API build validated exactly 6,236 non-empty, unique verse translations across all 114 surahs. This is source-corpus completeness, not a verse-by-verse religious/editorial review or permission for commercial reuse.
- The duration probe selected contiguous Ash-Sharh 94:1–8 audio at 62.579 seconds. It remains a candidate and is not newly user-approved for production.
- Artifact inspection found a packaging defect: the workflow generated `output/saheeh_international_translation.json` but attempted to upload the nonexistent `output/english_saheeh_translation.json`. The artifact therefore omitted the translation corpus even though its build step passed.
- Fixed the workflow on this feature branch in commit `46cf87d48d18ce41679341254ed9695c8927abfb`: it now checks the generated file, edition, 6,236-entry count and review/rights status, and uploads the correct filename. A new Actions run must pass and its artifact must be inspected before considering the packaged corpus available.
- The current exact Arabic Uthmani reference snapshot is still only a small reviewed sample. Quran-wide Arabic text integration, per-passage review, recording review/rights gates, varied approved backgrounds, dua/dhikr source approval, and real Telegram delivery remain outstanding.
- No daily/Friday schedule or TikTok auto-publishing is enabled.


## Arabic corpus and next-stage scope (2026-10-31)
- User explicitly deferred item 5 (dua/dhikr/trusted-reminder engine). Do not work on that category in the current stage.
- The artifact packaging fix is verified: Actions run `41239606864` succeeded, and artifact `13056184502` contains `saheeh_international_translation.json` (964,284 bytes), the 6,236-entry official audio inventory, candidate 94:1-8 audio files and passage report.
- Added `src/build_quran_uthmani_catalog.py` and regression tests. It fetches edition `quran-uthmani` from the documented AlQuran Cloud complete-Quran endpoint, checks all 114 surahs and exact canonical verse counts, rejects missing/duplicate/empty entries, and preserves the API strings verbatim.
- Critical safety gate: this output is explicitly `source_fetched_not_human_reviewed`, `rendering_allowed=false`. It is a candidate source corpus only and must never replace the small reviewed local reference until exact source comparison and human review have been completed.
- Updated the Quran inventory workflow to build, validate, test and package the full Arabic candidate corpus alongside the audio and Saheeh corpora. New run `41239881872` is queued at this checkpoint; verify its full job and artifact before claiming success.
- Regression-test push also started existing review-render workflows `41239875399` and `41239875389`; inspect their conclusions and artifacts. Push-triggered runs do not send to Telegram because the Telegram step requires explicit dispatch input.
- Existing approved audio remains limited to the exact user-reviewed Ash-Sharh 94:5-6 recording. Do not treat candidate 94:1-8 audio from the duration probe as user-approved. The 94:1-8 text approval and audio approval are separate.
- After Arabic corpus artifact verification, next focus is a safe data-join/preparation path that uses exact `surah:ayah` keys and refuses unreviewed Arabic or unapproved audio/translation. Then produce distinct Quran-only review candidates where approved content permits, run render/technical checks, and complete an explicit real Telegram MP4 delivery test. No schedule, daily/Friday automation, or TikTok publishing.


## Quran-only build progress update (2026-10-31)
- Scope confirmed by user: defer item 5 (dua/dhikr/trusted-reminder engine) for now. Current work is Quran corpus, rendering candidates, technical checks, and Telegram delivery only.
- Added `src/build_quran_video_catalog.py`: joins Arabic Uthmani, Saheeh International and the official Maher Al-Muaiqly Hafs archive inventory by exact `surah:ayah` key. It fails on mismatched keys, missing/empty fields, incorrect editions, incomplete audio coverage, or weakened review gates. Output is explicitly review-only with `rendering_allowed=false`.
- Added join regression tests and expanded the inventory workflow to package `quran_joined_candidate.json` as an artifact.
- CI exposed an import-path problem in the newly added catalog tests. Added explicit `src` path setup to the three catalog test modules. The latest workflow run on commit `421ea074b4fc17d2cd1b8787257806e68ae75e8f` is `41239949487`; verify this run after it finishes. Earlier failures `41239881872` and `41239886858` occurred before the import-path fix and must not be reported as the final test result.
- A successful Arabic fetch (6,236 entries) only establishes source/API coverage, not correctness for production. Candidate Arabic corpus and joined catalog remain blocked from rendering pending independent exact-text review. The existing reviewed reference snapshot remains unchanged.
- The separate rendering workflows started by test-file pushes are review-only; push-triggered Telegram step remains skipped. Any render artifact based on 94:1-8 is a candidate only; the only recording the user explicitly reconfirmed as approved is Ash-Sharh 94:5-6.
- Do not work on dua/dhikr yet. Do not enable schedules or TikTok publishing. Do not claim Telegram delivery until a real MP4 is confirmed in the user's Telegram chat.


## Full Quran candidate catalog verified (2026-10-31)
- Latest complete catalog workflow: `41239949487`, conclusion `success`, on the feature branch. Every step passed, including the Arabic builder, exact-key join, 6,236-entry safety check, regression tests, duration probe and artifact upload.
- Artifact `13056753361` was downloaded and inspected. It contains:
  - `official_verse_audio_inventory.json`: 6,236 verse-to-archive mappings.
  - `saheeh_international_translation.json`: 6,236 translations.
  - `quran_uthmani_candidate.json`: 6,236 Uthmani Arabic entries, explicitly unreviewed and `rendering_allowed=false`.
  - `quran_joined_candidate.json`: 6,236 exact-key joined records, explicitly review-only and `rendering_allowed=false`.
  - Ash-Sharh 94:1-8 duration candidate and 8 original verse MP3 files; total probed duration 62.579 seconds (candidate only; not the user's reconfirmed approved 94:5-6 recording).
- Current renderer Actions runs `41239949435` and `41239949423` were still rendering review MP4s at the last check. Inspect their final outcomes and artifacts; neither push-triggered workflow sends to Telegram.
- Current hard gates remain unchanged: only 94:5-6 recording is explicitly reconfirmed approved by the user; the fetched Uthmani corpus must not be used as a reviewed reference; Saheeh commercial reuse rights and verse-level review remain open; Telegram MP4 receipt is not yet confirmed.
- Continue Quran-only work. Dua/dhikr item 5 is deferred. No schedules, daily/Friday runs, or TikTok auto-publishing.


## Review MP4 render result (2026-10-31)
- `render-manifest-video` run `41239949435` completed successfully. It rendered Ash-Sharh 94:1-8 as a review candidate, passed Quran text validation and the renderer, passed MP4 technical checks, and uploaded artifact `13057186058`.
- Downloaded and inspected the artifact: `review.mp4` is 1080x1920, H.264, 30 fps, AAC audio, 62.8 seconds, 47,561,791 bytes (<65s). The matching caption marks `review_required` and `publishing=disabled`.
- The frame check shows the gold Ash-Sharh title cartouche, white Arabic verse, gold verse medallion, English meaning below, and the approved nature background.
- Important: this 94:1-8 MP4 is a review candidate only, not a publish-ready approved recording. The user's latest explicit confirmation is for the 94:5-6 recording; do not mark the 94:1-8 audio approved or publish it without separate user listening approval.
- Telegram step on run `41239949435` was skipped (push-triggered workflow). No actual Telegram MP4 receipt is confirmed.


## Second review-render workflow completed (2026-10-31)
- Run `41239949423` also completed successfully: text validation, regression suite, audio preparation, MP4 render and artifact upload all passed.
- Artifact `13056917911` (`ash-sharh-94-1-8-video-review`) was uploaded. Its Telegram step is explicitly skipped.
- Both generated 94:1-8 MP4s are review-only candidates. Keep the user's explicit audio approval boundary: 94:5-6 is the only recording reconfirmed by the user; neither 94:1-8 render is approved for publishing.


## Recording approval boundary and caption cleanup (2026-10-31)
- Corrected the 94:1-8 manifest: its recording is now `approved=false`, `preview_only=true`, `exact_recording_user_reviewed=false`, with official reuse rights documented. This reflects the user's latest explicit confirmation that only the 94:5-6 recording is approved.
- Updated `validate_content_manifest.py` to permit a rights-cleared `preview_only` Quran recording solely for a review render; it rejects preview candidates marked production-approved, candidates without documented reuse rights, and unapproved recordings lacking the preview flag. Added regression tests.
- Renamed the relevant workflow steps so the 94:1-8 audio is not mislabeled as user-approved. The preview-only video remains manual-review content; Telegram/TikTok publishing is not triggered by these push runs.
- Corrected the second-video caption strings to contain real line breaks instead of literal backslash-n characters. Latest render workflow runs `41240247858` (manifest renderer) and `41240243912` (second renderer) are in progress at this checkpoint; verify the latest one and inspect the resulting caption before sharing.


## Renderer preview-only gate follow-up (2026-10-31)
- The first preview-only render attempt passed all 71 tests but the renderer had a second, independent "audio must be approved" guard. That correctly stopped the 94:1-8 candidate rather than silently treating it as approved.
- Added `validate_quran_audio_approval()` to the renderer: approved audio still requires user listening review; a candidate may render only when `preview_only=true`, `approved=false`, and reuse rights are documented. It rejects missing rights and any preview marked production-approved.
- Added five renderer regression tests for the approval/preview combinations. Latest full review-render run `41240328907` includes these changes; inspect its result before treating the refreshed preview artifact as complete.
- Existing earlier 94:1-8 artifact is technically valid as a visual preview, but its caption JSON had literal escaped newline markers. Use only a refreshed artifact after run `41240328907` completes if available; the corrected manifest caption now has actual line breaks.


## Latest renderer gate verified (2026-10-31)
- GitHub Actions run `41240328907` completed successfully on `feature/telegram-review-notifications`, commit `b9b33009b5c1a1827bb79dfec286b842223b559b`.
- All render-job steps passed: Quran reference structure, regression tests, exact Arabic validation, audio preparation, video rendering, MP4 technical verification, and artifact upload.
- Renderer regression tests now enforce the approval boundary: the exact user-reviewed 94:5–6 recording may be production-approved; 94:1–8 may render only as a rights-cleared preview candidate and cannot be marked production-approved.
- Latest artifact `islamic-video-review`, ID `13056564523`, contains `review.mp4` and `review.caption.json`. MP4 independently checked: H.264, AAC, 1080×1920, 30 FPS, 62.8 seconds. Caption JSON parses and contains actual line breaks; it says `review_required` and `publishing=disabled`.
- Telegram step was skipped because this was a push-triggered run. No real Telegram receipt is confirmed; manual Telegram delivery test remains open.
- This 94:1–8 output is still a review-only candidate. Do not publish or treat its recording as user-approved without the user's separate listening approval.


## Latest render and rotation checkpoint (2026-10-31)
- Run `41240985110` completed successfully on `feature/telegram-review-notifications`.
- Quran reference validation, regression tests, exact Arabic validation, audio preparation, video rendering, MP4 verification, and artifact upload all passed.
- Artifact `islamic-video-review`, ID `13056804985`, size 47,412,647 bytes.
- The render uses 0.02 seconds of inserted silence between verses. It does not time-stretch or speed up the recitation.
- Telegram step was skipped because this was a push-triggered run. No actual Telegram delivery is confirmed.
- Rotation engine currently selects only manifests explicitly marked `rotation_approved=true`; the existing Al-Ikhlas candidate is not approved, and the Ash-Sharh 94:1–8 manifest remains preview-only. The approved 94:5–6 recording is the only explicitly user-reviewed exact passage.
- Therefore automatic variety is not yet production-ready: there are not yet three distinct eligible reviewed manifests/assets. Do not weaken approval gates or mark candidate content rotation-approved to make the selector run.
- Next: prepare additional Quran candidates with exact official audio, verified text/translation, approved visual assets, and user review; then batch-render three distinct videos and verify real Telegram delivery. TikTok publishing remains manual-only.


## Quran-only daily engine correction (2026-11-01)
- Active work remains exclusively on `feature/telegram-review-notifications`; `main` was not modified.
- User clarified that the daily orchestrator must not require dua and dhikr manifests. The current phase is Quran-only; dua/dhikr are future optional extensions.
- Updated `src/orchestrator.py` to select a configurable batch of three distinct Quran manifests by default, using the existing rotation helper. It validates the complete batch before rendering, retains manual-review requirements, and keeps TikTok auto-publishing disabled.
- Added/rewrote `tests/test_orchestrator.py` for Quran-only selection, three distinct items, incomplete-batch blocking, manifest category validation, and history handling.
- Added orchestrator compilation and tests to `.github/workflows/quran-batch-engine-tests.yml`. GitHub Actions run `41288273347` completed successfully: compile, 11 existing Quran engine tests, the new orchestrator tests, and the test-only workflow guard all passed.
- Inspected the existing Quran-wide workflow `.github/workflows/build-quran-audio-inventory.yml`: it already builds a full 6,236-verse Arabic/translation/audio join, selects distinct surahs, prepares whole-ayah audio under 65 seconds, renders review-only previews, and has a Telegram delivery step. The earlier assumption that no scheduled workflow existed was incorrect.
- Found and corrected the schedule/delivery mismatch. The workflow now runs once daily at 03:07 UTC and is intended to send all three distinct-surah review-only MP4s in that one run, rather than rebuilding the full corpus three times per day and selecting one video per run. Each successful Telegram delivery is recorded and pushed to this feature branch immediately before attempting the next video, reducing duplicate-delivery risk if a later send fails.
- Workflow changes keep Telegram review-only captions, require manual TikTok posting, and do not enable TikTok publishing.
- Integration run `41288335048` was triggered by a push before the final delivery-loop optimization. At last inspection it had successfully completed archive inventory, full Saheeh translation, Uthmani corpus, exact-key catalog join, catalog tests, diverse candidate selection, whole-ayah audio preparation, and draft-manifest generation; the three-preview rendering step was still running. It was a push-triggered validation run, so its Telegram delivery step is not eligible to run. Check its final outcome before claiming end-to-end rendering success.
- Latest workflow-delivery implementation commit: `37d92d402701a90408e504263b79ff49a63cc591`. It has not yet been verified by a scheduled or manually dispatched run that actually sends all three videos to Telegram.
- No automatic TikTok publishing is enabled.


### Confirmed integration preview run (2026-11-01)
- GitHub Actions run `41288335048` completed successfully end-to-end through the preview and artifact-upload stages. The Telegram-send step was correctly skipped because this was a push-triggered validation, not a scheduled/manual delivery event.
- It verified the full Quran data pipeline and rendered exactly three distinct-surah review-only MP4s:
  - Al-Mulk 67:26–27 — 37.616 seconds.
  - At-Takwir 81:15–16 — 16.588 seconds.
  - Al-Alaq 96:2–3 — 15.543 seconds.
- All three were verified as 1080x1920, H.264 video with the original MP3 audio stream, and below the 65-second limit. All are explicitly marked review-only; audio/production approval remains false.
- Uploaded artifact: `official-quran-audio-inventory-and-probe`, artifact ID `13076490971`, retention 30 days. This confirms preview generation, not Telegram delivery.
- The final delivery workflow update is commit `37d92d402701a90408e504263b79ff49a63cc591`; it consolidates the three daily sends into one daily run and records each confirmed Telegram delivery immediately. Await a schedule/manual-dispatch run to verify the Telegram send and persistent history update.


## Daily three-video render verification (2026-11-01)
- GitHub repository metadata confirms `feature/telegram-review-notifications` is the repository's default branch. Therefore its `schedule` trigger is eligible to run without modifying `main`.
- Daily schedule is `07 03 * * *` (03:07 UTC / 04:07 Tunisia time), and one run builds three different Quran review videos together.
- GitHub Actions run `41288444911` completed successfully on commit `37d92d402701a90408e504263b79ff49a63cc591`. It rebuilt the full 6,236-verse Arabic/English/audio candidate catalog, selected three distinct surahs, prepared whole-ayah audio, and rendered three review-only MP4s.
- Verified outputs: Al-Mulk 67:26–27 (37.616s), At-Takwir 81:15–16 (16.588s), Al-Alaq 96:2–3 (15.543s); all 1080x1920 H.264 video with MP3 audio; all under 65 seconds.
- Artifact `official-quran-audio-inventory-and-probe`, ID `13076490971`, contains MP4s, audio, manifests, and reports; retained for 30 days.
- This run was triggered by a code push, so the Telegram delivery and failure-notification steps were correctly skipped. No claim of Telegram delivery is made from this run. The next scheduled run is the first automatic end-to-end Telegram delivery attempt.
- The delivery step sends all three review-only MP4s sequentially to Telegram, then records each confirmed ayah delivery in `data/quran_delivery_history.json` and pushes that history to this default feature branch. The workflow has `contents: write` permission. The history file is initially absent and is created only after the first confirmed Telegram delivery.
- The daily candidate builder reads this persisted history and avoids reusing previously delivered ayahs. It excludes the already-used Ash-Sharh prototype from the daily rotation.
- Telegram secrets cannot be inspected through the available GitHub interface; successful delivery still depends on valid `TG_BOT_TOKEN` and `TELEGRAM_CHAT_ID` repository secrets.
- The renderer currently uses the previously user-approved Mixkit waterfall moving background with palette variations; distinct backgrounds per video are not yet implemented. Audio/text/translation and reuse approvals remain human review items. TikTok auto-publishing remains disabled.

## Handover update — 2026-11-01 (latest verified checkpoint)
- User confirmed that the Telegram bot receives a test message successfully. This confirms the test-message path and that the bot/chat setup is reachable; it does not by itself prove that the scheduled three-MP4 delivery has completed.
- Latest workflow run checked: `41288831454` (run #77), commit `ee1481ead4d4151b1ded3bbd850ffa344b2dff60`, event `push`, conclusion `success`. All inventory, translation, catalog, candidate selection, audio preparation, manifest, preview-render, and artifact steps passed.
- In that push-triggered run, Telegram delivery and failure-notification steps were correctly skipped by their event guards. This is expected and is not a delivery failure.
- Three distinct-surah previews were previously verified in run `41288444911`: Al-Mulk 67:26–27 (37.616s), At-Takwir 81:15–16 (16.588s), and Al-Alaq 96:2–3 (15.543s), all vertical 1080x1920 and below 65 seconds.
- Daily schedule remains `03:07 UTC` (04:07 Tunisia local time). Since the 2026-11-01 scheduled time has passed, the next scheduled attempt is 2026-11-02 at 04:07 Tunisia time. The scheduled run must be inspected for three Telegram API confirmations and a successful delivery-history push before declaring automatic video delivery proven.
- User explicitly confirmed Telegram test-message receipt; use that confirmation as context, but continue to distinguish it from actual MP4 batch delivery.
- The active branch remains `feature/telegram-review-notifications`; do not modify `main`. TikTok publishing remains manual and disabled.
- Known remaining visual gap: all three recent previews still use the same approved Mixkit waterfall source with palette changes; true distinct background rotation is not yet implemented.


## Orchestrator history-safety correction (2026-11-01)
- Updated `src/orchestrator.py` so a render-only run never writes rotation/delivery history. Rendering is not Telegram delivery; only the production workflow's Telegram API confirmation path may record delivered ayahs.
- Added a regression test proving `--render` leaves the existing history file unchanged.
- Commits: orchestrator fix `d58002f9648f7d40935d45d3443719dcf18ca92e`; regression test `fda4325c500293021eb791b17ebe3e35bababc2d`.
- GitHub Actions run `41289246850` completed successfully on the active feature branch. Compile, Quran catalog/batch/visual tests, all orchestrator tests including the new history-safety test, and the test-only workflow guard passed.
- The production daily Quran workflow remains unchanged and independent of this helper orchestrator. Latest push-triggered integration run `41288831454` succeeded through three review previews and artifact upload; Telegram was correctly skipped for a push event.
- The user's successful Telegram test message confirms bot/chat reachability only, not delivery of three MP4s. The next scheduled batch attempt is 2026-11-02 at 03:07 UTC (04:07 Tunisia time); verify three Telegram send confirmations and history updates before declaring daily delivery proven.
- Known visual gap remains: all three preview videos use the same approved Mixkit waterfall source with palette variations. True background rotation requires additional separately licensed and user-approved background assets.
- No TikTok auto-publishing is enabled; user review and manual posting remain mandatory.

## Schedule correction — three Tunisia delivery slots (2026-11-01; supersedes prior 03:07-only schedule)
- User clarified the agreed daily delivery times are **04:00, 12:00, and 18:00 Tunisia local time**, with one distinct Quran review MP4 sent to Telegram at each slot. The earlier single daily 04:07 schedule and one-run/three-video batch did not match this requirement.
- Corrected `.github/workflows/build-quran-audio-inventory.yml` to GitHub Actions cron `0 3,11,17 * * *` UTC, corresponding to 04:00, 12:00, and 18:00 Tunisia time (UTC+1). GitHub repository metadata confirms `feature/telegram-review-notifications` is the default branch, so the schedule is eligible without changing `main`.
- Each scheduled invocation now prepares one candidate video: audio `--target-count 1`, exactly one draft manifest, renderer `--minimum-previews 1`, and Telegram delivery guards require exactly one distinct-surah MP4. The candidate pool still samples eight distinct surahs and uses an hour-specific seed; confirmed deliveries are recorded in history so subsequent slots avoid already-delivered ayahs.
- Added `--minimum-previews` to the renderer CLI and aligned audio-preparation readiness status with its configured target count.
- Workflow commits: schedule/batch correction `dacf07ba48af1abdc86d103180ad1a9b0c167f92`; renderer CLI `f1de4205237294138f654c69869717f7814fe22c`; audio readiness status `c301a1634dc718665a3ae83a7710a40c5b9da49d`; validation wording `666aa85d0ec900c785f633851150746aa77801ea`; one-video target and shell continuation correction `15a75dc3e036d31618a6d389e36b08f9abcdbf98`.
- These are nominal GitHub Actions start times; GitHub may delay scheduled runs under load. Do not claim Telegram delivery until each run confirms one MP4 send and the history push succeeds. A successful bot test message is not proof of scheduled MP4 delivery.
- Keep `main` untouched. TikTok auto-publishing remains disabled; the user reviews and posts manually.

## Telegram on-demand request implementation (2026-11-01; not yet deployed)
- Added a separate workflow `.github/workflows/telegram-quran-request.yml` with manual `workflow_dispatch` input `request_text`. It rebuilds the exact Arabic/translation/audio catalog, parses one request, prepares the requested passage, renders one review-only MP4, and sends it to the configured Telegram chat. It is isolated from the daily workflow and only runs on `feature/telegram-review-notifications`.
- Added `src/select_requested_quran_range.py`: when the user sends only a surah name, it probes the official whole-ayah audio files and chooses the longest opening contiguous range (maximum 10 ayahs) that fits 65 seconds. It never trims audio. Single-ayah requests are now parsed as an exact one-ayah range.
- Added regression tests for single-ayah parsing and safe automatic range selection; expanded `.github/workflows/test-quran-request.yml` to install `remotezip` and run the new selector tests.
- Added Cloudflare Worker bridge source at `cloudflare/telegram-bridge/worker.js`, KV binding template `cloudflare/telegram-bridge/wrangler.toml`, and setup instructions `docs/telegram-on-demand-setup.md`. The Worker checks Telegram's webhook secret and authorized chat ID, deduplicates update IDs in KV, then dispatches the isolated GitHub workflow.
- Commits in this implementation sequence: `6c0b7d53`, `35b464b4`, `75c17655`, `d3b650a5`, `4a546e55`, `63f1cdfc`, `8c22a764`, `312f1475`, `26ace894`, `6fff46a5`, `565075a7`, `f9e31cc5`, `5e71fd44`, `c720f70c`, `efa90daa`.
- Verification still pending: GitHub Actions results for the new selector/parser tests and an end-to-end workflow run. No Worker has been deployed and no Telegram webhook has been set; therefore the bot does not yet execute requests from Telegram. A one-time Cloudflare Worker/KV setup, private secrets, and Telegram webhook registration remain necessary.
- Whole-surah requests auto-select an opening passage; explicit ayah/range requests are exact. All outputs remain review-only; Telegram delivery is the only send destination and TikTok publishing remains manual/disabled.

### On-demand request CI verification (2026-11-01)
- The first CI attempt exposed a normalization mismatch for the Arabic phrase `الآية`: the parser normalizes `آ` to `ا`, so the marker was updated to accept `الاية`. The initial failing run was `41291158253`; it is not counted as a pass.
- Corrected parser/selector suite run `41291299022` completed successfully. All steps passed: parser tests (including single ayah), automatic 65-second whole-ayah range-selection tests, authorized inbox tests, request-state deduplication tests, requested-passage tests, and single/daily review-renderer tests.
- The new on-demand workflow YAML was accepted by GitHub Actions. Push-validation run `41291338533` completed with `skipped`, as intended because the workflow only processes actual `workflow_dispatch` requests; this validates that the workflow file was recognized, not that it rendered/sent a video.
- Still not operational end-to-end: Cloudflare Worker/KV deployment, private Worker secrets, Telegram webhook registration, and a real Telegram request/MP4 receipt remain outstanding. No daily workflow or schedule was changed.

### Cloudflare bridge syntax and request regression suite (2026-11-01)
- Added a Node.js module syntax check for `cloudflare/telegram-bridge/worker.js` to the isolated request CI workflow.
- Run `41291401349` completed successfully. The Worker JavaScript syntax check, parser tests, automatic whole-surah range selection tests, inbox authorization, update deduplication, requested passage tests, and review-renderer tests all passed.
- This is code/CI validation only. No Cloudflare deployment, KV binding, Telegram webhook registration, workflow dispatch from Telegram, or real requested MP4 delivery has been performed.


## Original Telegram automatic MP4 delivery audit — 2026-11-01
- User clarified that the required destination is the existing original Telegram bot/chat that receives MP4 videos automatically from GitHub Actions. This is not a Telegram command bot. Do not add or require Cloudflare Worker, webhook, KV, or Telegram command handling for this delivery path. TikTok upload remains manual by the user.
- Audited only `feature/telegram-review-notifications`; `main` was not modified. No repository files, bot settings, secrets, or infrastructure were deleted or changed during this audit.
- Confirmed the production workflow is `.github/workflows/build-quran-audio-inventory.yml`, with schedule `0 3,11,17 * * *` UTC (04:00, 12:00, 18:00 Tunisia time). It prepares one distinct-surah review MP4 per scheduled invocation and has a guarded Telegram send step using the existing `TG_BOT_TOKEN` and `TELEGRAM_CHAT_ID` secrets.
- The send step runs only for `schedule` or `workflow_dispatch`. Push-triggered CI runs do not send MP4s to Telegram; their skipped send step is expected and is not proof of delivery.
- Failure evidence: run `41289848267` (push event) passed catalog, audio preparation, and manifest steps but failed at `Render distinct-surah 9:16 review-only video previews` with `ValueError: Translation for ayah 16 does not fit; refusing to clip.`. Because rendering failed, artifact upload and Telegram delivery were skipped.
- Later run `41289952819` (push event) completed inventory/build/audio/manifest/render/artifact successfully. Its Telegram send step was skipped because the event was `push`; this proves a successful preview build, not MP4 delivery.
- The latest run list inspected contained no `schedule` event run. Therefore automatic scheduled MP4 delivery to the original Telegram chat is not yet verified. The user's successful Telegram test message confirms the bot/chat can receive a test message, but not that this production workflow delivered an MP4.
- `src/send_telegram.py` uploads an MP4 through Telegram `sendVideo`, validates a non-empty file, 50 MB limit, caption length, and requires existing GitHub secrets. Secret values are not readable through the available GitHub interface and were not changed.
- Next safe action: inspect the next actual scheduled run (or deliberately dispatch this existing production workflow) and verify render success, Telegram API confirmation in logs, and the delivery-history commit. Do not create a second bot or Cloudflare bridge. Do not mark ayahs delivered unless Telegram confirms the MP4 send.
- Separate CI note: isolated parser test run `41291090647` failed in its single-ayah parser test; preceding run `41291083162` passed. This request-parser workflow is separate from the scheduled MP4 delivery path.


## Final preview duration regression tests (2026-11-01)
- Added direct tests for the renderer's real `probe()` validation: exactly 65.000 seconds is accepted, 65.001 seconds is rejected, and a non-1080x1920 output is rejected.
- This tests the actual ffprobe result-validation function rather than a mocked render-level duration report.
- Test commit: `51c2952759ab738b636d129be41e320573cebcdd`.
- The test commit triggers the existing push-validation workflow. A green CI result will validate the regression tests; it will not count as Telegram MP4 delivery because push events skip Telegram.
- Background rotation remains unresolved: the renderer still uses one previously approved Mixkit moving-video source. No unreviewed asset or extra cloud service was introduced.

## Simplified execution directive and latest CI verification (2026-11-01)
- Recorded the user's instruction to stop unnecessary technical back-and-forth and prioritize a single working engine using the existing GitHub Actions workflow and original Telegram bot. No new cloud service, bot, webhook, paid agent, or orchestrator is to be introduced.
- Priority is now strictly: varied verified Quran candidate -> complete <=65-second MP4 render -> real Telegram sendVideo confirmation with message_id -> delivery-history commit -> verify next-slot non-repetition. Optional background-library expansion is secondary to this end-to-end path.
- The Agent 1–4 entries are internal review responsibilities, not separate autonomous agents. This is stated explicitly to avoid implying that independent agents are running.
- Latest production build run 41305424879 (run #91, push event, commit 51c2952759ab738b636d129be41e320573cebcdd) completed successfully. Inventory, translation, catalog checks, tests, candidate preparation, manifest generation, render, and artifact upload all passed. Telegram send and failure-notification steps were skipped because this was a push event. This confirms a successful build, not a real Telegram MP4 delivery.
- Latest isolated request test run 41305424858 (run #31) also completed successfully. Earlier parser failures are superseded by this passing test run for the current tested commit.
- The connected GitHub actions available in this session do not expose a workflow-dispatch operation. Do not claim a manual dispatch or real Telegram delivery until an actual schedule/dispatch run provides Telegram's message_id.

## Default-branch and latest distinct-surah render verification (2026-11-01)
- Verified through the GitHub repository API that the repository default branch is `feature/telegram-review-notifications`. Therefore the existing `schedule` workflow is on the default branch; the GitHub scheduled-workflow default-branch restriction is not a blocker.
- Production build run `41305424879` rendered candidate `quran_s086_012_013` (Surah At-Tariq 86, ayahs 12–13), duration 14.55 seconds, 1080x1920, H.264 video with the original MP3 audio. It is distinct from Surah Ash-Sharh and within the 65-second cap.
- This was a `push` event, so Telegram delivery was skipped by the workflow condition. No real MP4 Telegram `message_id` has yet been observed. The next actual `schedule` run is the end-to-end delivery check; the workflow already targets the original bot and records history only after confirmed sendVideo success.

## Prevent immediate repeat of the previous surah (2026-11-01)
- Updated `src/build_quran_review_batch.py` to read the most recent confirmed delivery from `data/quran_delivery_history.json` and automatically exclude that surah from the next candidate pool, in addition to the existing delivered-ayah exclusion. This prevents two consecutive scheduled Quran videos from using the same surah while still allowing later reuse of a surah with fresh ayahs.
- Added regression tests for selecting the last delivered surah, empty history, and invalid history values.
- Source commit: `003ee2693c5a86cac61fd4bc5b432953e67c4f39`; test commit: `cdbbeeff260cb546fe103304789936f8bf449287`.
- Validation is currently running: production workflow run `41306047454` (#92) and test workflow run `41306050228` (#14). Their outcomes must be checked before marking this change verified. These are push-triggered runs, so Telegram delivery is expected to be skipped.

## Validation result — consecutive-surah rotation (2026-11-01)
- Production build run `41306047454` (#92) completed successfully. The updated batch selector ran against the full Quran candidate catalog; the run prepared and rendered Surah At-Tariq (86), ayahs 12–13, as a 14.55-second 1080x1920 review-only MP4.
- Test run `41306050228` (#14) completed successfully. The regression suite includes the new history rotation checks, renderer duration/format checks, Telegram sender safety checks, and delivery-history tests.
- Artifact `13082954368` was uploaded successfully. The Telegram send step was skipped because this was a push-triggered run. Therefore no actual Telegram delivery or history update was confirmed by this run.
- Background rotation is still not implemented: the renderer continues using the one previously approved Mixkit waterfall clip. No claim of 15–20 integrated backgrounds is made.
- Commits for code/tests/docs: `003ee2693c5a86cac61fd4bc5b432953e67c4f39`, `cdbbeeff260cb546fe103304789936f8bf449287`, `10f7c22815b8aea5cead2d9af697e1def5fb0659`, `69f48a5b82210c153f30bf0b600877ac141c8083`.


## Scheduled-run check (2026-11-01, 13:24 Tunisia time)
- Queried the branch's GitHub Actions run history specifically for `event=schedule`; no scheduled runs were returned. The latest visible production/test runs remain push-triggered, with Telegram skipped by design.
- The configured cron remains `0 3,11,17 * * *` UTC (04:00, 12:00, 18:00 Tunisia time). The 12:00 Tunisia slot has not been evidenced in Actions history as of this check.
- Next verification point is the 18:00 Tunisia slot. Confirm the scheduled event, sender step, real positive Telegram `message_id`, and subsequent delivery-history commit before declaring end-to-end delivery.
- No code or workflow trigger was changed to force a Telegram send. No new bot, cloud service, or TikTok publishing path was added.


## One-off live Telegram test trigger (2026-11-01)
- The user correctly challenged the assumption that a cron schedule alone proves unattended delivery. The workflow had successful push-triggered builds, but Telegram was skipped on every push; no real scheduled sendVideo/message_id had been evidenced.
- Added a narrowly scoped one-time test condition to the existing workflow: Telegram send and failure notice also run only when a push commit message contains `[telegram-live-test]`. This avoids enabling Telegram delivery on ordinary code pushes.
- Trigger commit: `391924dae1c1b4d5826386876f6395e7beae4b6d` on `feature/telegram-review-notifications`. Because the workflow file itself is in the push path filter, this commit should launch the test run.
- This is a trigger configuration change, not proof that a run started or a video arrived. Verify the run's event, render, Telegram `sendVideo` response with a real positive `message_id`, and delivery-history commit. If successful, immediately remove the temporary tagged-push condition so ordinary pushes do not send videos.
- If the run does not start, investigate Actions scheduling/enabled state and repository workflow permissions before adding more engine features. No `main` changes, new bot, Cloudflare, webhook, or TikTok auto-publishing.


## User-confirmed Telegram MP4 arrival and subsequent failure alert (2026-11-01)
- User supplied a Telegram screenshot showing the original chat "Islamic Videos Review bot" received an actual playable MP4 for Surah At-Tariq, ayahs 12–13, with Arabic caption, hashtags, English caption, and manual TikTok approval notice. This is direct user-provided evidence that at least one real MP4 sendVideo delivery succeeded; it supersedes the earlier statement that no real delivery had been observed.
- The same screenshot also shows a subsequent failure notification saying the daily Quran video batch failed and the videos were saved as GitHub Actions artifacts for 30 days.
- Therefore delivery itself succeeded for the shown MP4, but the overall workflow later entered its failure path. The exact failing step is not established from the screenshot alone. Inspect the corresponding Actions job logs before changing code; likely points to verify include delivery-history recording/commit/push after send, but do not assume this is the cause.
- Keep the one-off tagged-push test condition temporary. Once the corresponding run is identified, verify the actual Telegram response/message_id and pinpoint the later failing step. Then fix only that step, remove the temporary test condition, and separately prove the three scheduled slots (04:00, 12:00, 18:00 Tunisia).


## Review of first user-received Telegram video — quality defects (2026-11-01)
- User reviewed the actual Telegram MP4 (Surah At-Tariq 86:12–13) and reported: only two ayahs, long pauses between ayahs, and poor design. These are accepted defects; the received sample is not approved as the target quality.
- Root cause for the two-ayah limit is confirmed in .github/workflows/build-quran-audio-inventory.yml: candidate creation explicitly passes --verses-per-passage 2 (line 137). This is a fixed count, not duration-aware selection. The renderer/audio stage must instead select the largest contiguous complete-ayah passage that fits <=65 seconds, with no verse truncation, and carry the exact selected verse list through manifest/render/caption/history.
- Audio preparation currently concatenates complete MP3 files with ffmpeg concat demuxer and -c copy (src/prepare_quran_review_batch_audio.py). It performs no pause/silence analysis or inter-ayah gap handling. Long gaps are therefore a known unaddressed issue. Any gap reduction must preserve the complete recitation and be validated by listening/probing; do not blindly cut audio or time-stretch it.
- Design defect confirmed in src/render_quran_review_previews.py: current frame uses a large transparent panel over the waterfall, Arabic body font 66px, English translation 22–30px, and one ayah per full-screen segment. User feedback says this design is not acceptable. Redesign layout for clearer hierarchy/readability and calmer background treatment before calling output ready.
- Background is still one waterfall clip. Palette changes are not scene rotation.
- The previously documented Agent 1–4 are only review responsibilities in AGENT_WORK_PLAN.md; no independent agents are running. Do not describe them as active workers. Work must be carried out and verified directly, one tested change at a time.
- Next priority: fix duration-aware contiguous ayah selection and exact selected-verse propagation; then inspect audio waveforms/silence and safely reduce excessive inter-ayah pauses; then redesign video layout. Keep Telegram send and TikTok manual-only. Do not send another sample as approved until user accepts its quality.


## First passage-length correction after user video review (2026-11-01)
- Changed the scheduled candidate builder from a fixed 2 complete ayahs to 3 complete consecutive ayahs (`--verses-per-passage 3`) in `.github/workflows/build-quran-audio-inventory.yml`.
- Commit: `7069ad5936d153f40fe66620c1624cc0bb667ffc` on `feature/telegram-review-notifications`.
- The existing audio preparation still refuses any complete passage over 65 seconds; it does not trim an ayah. This is a safe interim improvement, not yet duration-aware variable-length selection. If a 3-ayah passage exceeds 65 seconds, the candidate is blocked and the workflow may fail rather than shortening it.
- Ordinary push-triggered CI can validate this change but will not send Telegram; the temporary live-delivery marker remains separate.
- Next: inspect CI for this commit, then implement/test duration-aware selection of the largest contiguous complete-ayah passage fitting 65 seconds, ensuring the exact selected list is propagated consistently to manifest, render, caption, and delivery history. Do not claim this dynamic behavior is implemented yet.


## Correction: do not impose a fixed ayah count (2026-11-01)
- User correctly pointed out that a fixed count of 3 ayahs is not the requirement; short surahs/passages may fit under 65 seconds and longer ones may not.
- Reverted the temporary `--verses-per-passage 3` workflow change back to 2 in commit `48bc2a1fde80ce9b52dda16c3929f82cc6d0ec84`. This restores the previous setting only as a temporary safe rollback; fixed 2 is still not the desired final behavior.
- Required implementation: choose complete contiguous ayahs dynamically based on measured official audio durations, allowing a whole short surah where it fits, and the longest suitable contiguous passage up to 65 seconds otherwise. Never trim an ayah. Ensure the exact selected verse list and paired Arabic/English text flow consistently into rendering, caption, and delivery history. Add tests for variable counts and exact 65-second boundary before enabling production.


## Quran review-preview visual redesign — first implementation (2026-11-01)
- Updated `src/render_quran_review_previews.py` on `feature/telegram-review-notifications` (never `main`): replaced the oversized translucent frame with a more compact centered reading panel, stronger contrast, clearer title hierarchy, a true gold circular ayah-number badge, and a better-separated English translation area.
- Arabic text now uses adaptive Amiri/Naskh-compatible font sizing and complete-word wrapping; it refuses to clip the ayah. Added regression test `test_arabic_layout_keeps_every_word_and_fits_compact_block`.
- Palette tint is now derived from surah and ayah as well as the ayah index, so the same approved moving footage receives different calm color treatments across passages.
- Code commits: `f19aa7e5` (layout), `a3338608` (Arabic layout test), `0ec7c8c2` (test import correction), `2ebc6e04` (surah/ayah palette variation).
- The renderer regression suite passed in production workflow run `41310945442` at the catalog regression-test step; its render step was still running at the time of this note. The subsequent palette commit run `41311053908` was queued/pending and must also be checked before declaring the latest revision validated.
- Important limitation: the underlying background is still the one previously approved Mixkit waterfall clip. Palette variation is not genuine scene rotation. No additional background was added without rights verification and the user's approval.
- This is a first visual improvement iteration, not final design approval. Inspect the resulting MP4 before asking the user to accept it. Audio inter-ayah pause reduction is still a separate unresolved task. Push-triggered CI does not send Telegram MP4s.


## Quran preview typography and audio-gap correction iteration (2026-11-01)
- Further visual refinements are committed on the active branch: ornate double-line surah cartouche, more legible title/number typography, stronger but restrained English translation size, and Amiri Bold installed and selected for Arabic title/body/ayah number. Short ayahs now have a larger adaptive size ladder (up to 96 px) rather than always rendering at the smallest standard size.
- A downloaded review artifact from run `41310945442` was inspected directly. It confirmed 1080x1920 output and a 47.856-second clip, and exposed that a very short ayah appeared too small. This prompted the larger adaptive Amiri sizing and the visual cartouche refinement; the artifact was not sent to Telegram.
- Audio analysis of the artifact's official per-ayah MP3s (Surah Fussilat 41:1–4) found leading silence of about 0.83–1.45 seconds and trailing silence of about 2.02–2.36 seconds per file at -50 dB, explaining the approximately 3.5-second inter-ayah gaps.
- Implemented `trim_edge_silence` in `src/prepare_quran_review_batch_audio.py`: detect only leading/trailing silence at -50 dB for at least 0.25 seconds, retain a 0.12-second safety margin at each detected edge, and stream-copy MP3 frames. Internal silence and recitation content are not filtered, time-stretched, or re-encoded. The 65-second selector now sums processed whole-ayah durations.
- The audio report records original and processed per-ayah durations plus exact processed file paths. `src/render_quran_review_previews.py` now uses those processed per-ayah files, rather than falling back to the untrimmed originals when the map is present.
- Added synthetic-MP3 regression coverage for edge-only silence handling and MP3 preservation, and renderer coverage to assert that processed per-ayah files are used.
- Validation status at this note: isolated request pipeline run `41311627949` passed, but this is not the audio/render suite. Production workflow run `41311627871` is queued behind an earlier render; full audio tests and latest render still need a green result. Do not claim the pause fix or latest visual design is CI-verified until that run completes.
- No Telegram MP4 was sent by these push-triggered runs. The original approved waterfall remains the only underlying scene; palette tints vary, but genuine scene rotation is still pending distinct rights-cleared and user-approved assets.


### Edge-pause CI validation update (2026-11-01)
- Production workflow run `41311768545` passed the full catalog/audio/renderer regression-test step, including the synthetic MP3 edge-silence test and the renderer test that checks processed per-ayah paths.
- In that same run, official audio preparation and draft-manifest generation completed; the 9:16 render step was in progress at the time of this update.
- Added a further regression test for selecting the longest processed whole-ayah prefix under 65 seconds (e.g. source 40s + 30s becomes 35s + 28s after safe edge-only silence reduction, so both complete ayahs fit). This is in run `41311817665`, which is queued/pending and must pass before the latest test set is fully verified.
- The previous run `41311627871` failed only because a test expected JSON string keys before serialization while the in-memory Python report uses integer keys. Corrected in `bbf33b1e`; the production test step then passed in `41311768545`.


### Real-candidate edge-silence render result (2026-11-01)
- Production workflow run `41311768545` completed successfully, including the full audio/renderer regression suite, candidate preparation, draft manifest generation, 9:16 render, and artifact upload.
- Actual selected passage: Surah Fussilat 41:1–5 (5 complete consecutive ayahs). The duration selector measured original source total 78.538s and processed whole-ayah total 63.008s, so five complete ayahs fit under the 65-second cap; no fixed 2/3-ayah count was imposed.
- Final MP4: 62.912s, 1080x1920, H.264 video + MP3 audio. This is a push-triggered build, so Telegram delivery was skipped; the artifact was inspected locally and not sent.
- Each of the five processed MP3s had no leading/trailing silence segment >=0.25s at -50 dB, confirming that the long edge pauses were reduced. The source sample previously had about 0.8–1.4s leading and 2.0–2.4s trailing silence per ayah.
- The rendered frames show the Amiri Bold Arabic, double-line surah cartouche, gold circular ayah number, white Arabic text, and smaller Saheeh International English translation. This is a substantial improvement but still awaits the user's review.
- Remaining CI work: validate the additional variable-length selector test and the draft-manifest processed-timing propagation on the latest head (runs after `41311768545`). Then perform one controlled Telegram review send, verify Telegram `ok: true` plus message_id and the exact 5-ayah history record, and remove the temporary tagged-push trigger.
- Background caveat remains: only the one approved Mixkit waterfall scene is currently used. Palette tint varies, but real background scene rotation is not yet implemented.


## Verified variable-length Quran render and edge-pause reduction (2026-11-01)
- Production workflow run `41311768545` completed successfully on `feature/telegram-review-notifications`. Artifact: `13085413677` (`official-quran-audio-inventory-and-probe`). The run passed catalog/audio/renderer regression tests, prepared audio, generated the draft manifest, rendered the preview, and uploaded the artifact. Telegram was skipped because this was a push-triggered run.
- The engine supplied the complete unused suffix of Surah Fussilat (41:1–54) to the audio selector. Based on measured processed audio duration, it selected the longest complete contiguous prefix that fits: ayahs 1–5. This is no longer a fixed two-ayah candidate.
- The review MP4 is 62.912 seconds, 1080×1920, H.264 video + MP3 recitation. It contains Arabic and paired Saheeh International English for 41:1–5. The exact recording and output remain review-only; no Telegram send or TikTok publishing occurred.
- Direct inspection of the artifact's raw and processed audio measured raw combined duration 78.446 seconds and processed combined duration 63.007 seconds (about 15.44 seconds shorter). Raw inter-ayah silence measured 3.266, 3.350, 3.447, and 3.558 seconds; processed inter-ayah silence measured 0.262, 0.267, 0.260, and 0.267 seconds. Only detected leading/trailing silence was reduced, retaining a 0.12-second guard at each file edge; internal recitation was not filtered or time-stretched.
- Sampled frames at 2, 14, 40, and 56 seconds show the refined double-line gold surah cartouche, Amiri Bold Arabic, separate gold circular ayah number, and smaller English translation. The long sampled ayah fits within the frame; visual review is still required from the user.
- The underlying scene is still the one previously approved Mixkit waterfall. Palette tint varies by surah/ayah, but actual scene/background rotation is not implemented because no additional background has both verified reuse rights and explicit user approval.
- A further regression test for choosing the longest processed whole-ayah prefix under 65 seconds was added after the successful run. Latest validation run `41312075159` must complete before that newest test is called CI-verified.


## Telegram review sample delivery confirmed (2026-11-01)
- One improved review-only MP4 was successfully sent to the existing Telegram bot by workflow run `41312274181`. Telegram returned `ok: true`, `message_id=28`, video size `34.6 MB`; the file contained Surah Fussilat 41:1–5. TikTok publishing remained manual.
- The send succeeded and the workflow printed `Recorded 5 actually delivered ayahs`, but its same-step Git push for history was rejected because concurrent documentation commits had advanced the branch after the workflow checkout. No video resend was needed.
- Repaired `data/quran_delivery_history.json` directly on the current feature branch in commit `ec2fe6bd`, adding exactly `41:1`–`41:5` with the delivery timestamp from the confirmed run. The current history now contains 11:1–2 and 41:1–5.
- The failed overall job also sent a misleading failure alert after the video had already arrived. The user was informed. Hardened the workflow in commit `503a4a39`: video send, history recording, and branch sync are now separate steps; history sync fetches and rebases on the current feature branch before pushing; the failure alert is conditioned on the Telegram send step itself not succeeding.
- Removed the temporary `[telegram-live-test]` push trigger. Future Telegram sends are restricted to scheduled runs or explicit workflow dispatch; ordinary code pushes do not send videos.
- Latest workflow validation run `41312848189` is a normal push run after this workflow change; Telegram send/record/sync steps are correctly skipped for push events.
- Still pending: verify the scheduled 04:00 / 12:00 / 18:00 Tunisia runs independently, and build a real pool of multiple rights-verified, user-approved background scenes. The currently approved waterfall remains the only actual scene; palette tint variation is not scene rotation.

## Official archive network resilience (2026-11-01)
- Investigated failed run `41312848189`, job `124866668534`: the official Quran archive host timed out during TCP connection to `download.qurancomplex.gov.sa`; the archive mapping did not fail validation. Downstream steps were skipped because inventory is a required gate.
- Added bounded request timeouts, retry/backoff for transient connection/read and HTTP 429/5xx failures, a larger initial ZIP range request, and a project User-Agent. The inventory still fails closed if the official source remains unavailable.
- Added `tests/test_build_official_audio_inventory.py` and wired it into the existing Actions workflow.
- Commits: `7d7214eeff00e9239308439ff3f506ac7318743c`, `3181e2b2ed244e0497d1121bd36d8fe6d646ab47`, `9ed2f575b64eff3df5048bb799ddafa6885665b0`, `180fca4f55135f05a7e77b86ebb19cb43af934db`.
- CI verification is pending. Background rotation remains unimplemented; no new external background is enabled.

## Background candidates staged safely (2026-11-01)
- Added `data/background_candidates.json` with four Pexels page references: sea, mountain lake, sunset sky, and mountain bridge.
- Pexels' official help page states its uploaded media use the Pexels License and are free for personal/commercial use without attribution. Individual pages are marked Free. The bridge clip is 16:9 and needs a vertical crop check.
- These are review candidates only: all `approved` and `user_approved` flags are false, direct MP4 URLs are empty, and download verification is false. The production renderer remains unchanged and cannot select them. No asset has been activated or sent to Telegram.
- Commit: `903dc3902d854edc030a3f74142cd0b886d43605`.

## Archive resilience CI verification (2026-11-01)
- Push-triggered Actions run `41313825363` (run #151, commit `180fca4f55135f05a7e77b86ebb19cb43af934db`) completed with `success`.
- All 17 inventory job steps that were expected to execute passed, including the retry/filename regression test, complete 6,236-entry official audio mapping, full Saheeh translation corpus, Uthmani candidate corpus, exact-key join, catalog tests, eight-distinct-surah candidate pool, one distinct-surah audio preparation, draft manifest generation, and review-only 9:16 preview render.
- Telegram send/history steps were skipped because this was a push event, not a scheduled/manual delivery event. No new video was sent. This confirms the archive fix and preparation pipeline; it does not yet prove the next scheduled Telegram delivery.
- Run: https://github.com/samiouess-ux/IslamicTikTokAutomation/actions/runs/41313825363

## Background source URL verification (2026-11-01)
- Re-opened all four staged Pexels clip pages and followed each page's own Free download link to capture the direct MP4 URL. The links resolve to videos.pexels.com/video-files assets whose path IDs match the four source page IDs.
- Added the exact direct MP4 URLs to data/background_candidates.json; this is metadata only. All four remain download_verified=false, approved=false, and user_approved=false. The production renderer and current approved Mixkit background remain unchanged.
- Added tests/test_background_candidates.py to check source-page/direct-file ID consistency and ensure approval gates remain closed. Added the test to the existing workflow's push path filter and CI steps.
- Commits: a7388a7 (URLs), b014ad9 (test + workflow), 9b426bf / e596498 (regex correction).
- CI run 41314687147 / #152 was observed in progress at 14:09 UTC; wait for its final conclusion before marking the new test verified.
- External page checks: ocean https://www.pexels.com/video/peaceful-ocean-waves-crashing-on-shoreline-35036280/, lake https://www.pexels.com/video/serene-mountain-lake-with-pine-forest-37675265/, sunset https://www.pexels.com/video/serene-sunset-sky-with-soft-clouds-35477402/, bridge https://www.pexels.com/video/drone-footage-of-mountain-forest-and-a-bridge-above-the-lake-5903759/. Pexels pages label the clips free; the bridge is 16:9 and still needs a crop review.
- Scheduled-run audit at 14:08 UTC found no event=schedule runs on the active branch yet; the next cron slot is 17:00 UTC / 18:00 Tunisia. The only workflow_dispatch run found was an older 2026-10-31 run. Scheduled Telegram delivery is not yet verified.


## Distinct-surah preview render verification (2026-11-01)
- Corrected the background-candidate URL test regex; the earlier run #152 failed only on an over-escaped dot in the test expression, not on any source URL or Quran data.
- Run #153 (41314717304) completed successfully on feature/telegram-review-notifications. The archive retry test, all 6,236 ayah mappings, Saheeh International corpus, Uthmani candidate corpus, exact-key join, catalog regression tests, diverse candidate selection, audio preparation, draft manifest generation, 9:16 render, and artifact upload all passed.
- Artifact 13087310229 contains the review MP4 quran_s055_001_078_REVIEW_ONLY.mp4: Surah Ar-Rahman (55), ayahs 1–10, 57.65 seconds, 1080×1920, H.264 + MP3. Whole consecutive ayahs were selected under the 65-second cap. The audio report measures 0.24 seconds of inter-ayah silence after edge-only silence processing; no internal silence was removed.
- Sampled frames show the existing approved Mixkit waterfall background, gold surah cartouche, white Arabic ayah text, gold circular ayah badge, and smaller Saheeh International English translation. This is a preview of the existing approved background, not a test of the four newly staged Pexels backgrounds.
- The Pexels candidates remain disabled/unverified/unapproved. The manifest and preview remain review-only: audio rights, exact Arabic/translation content, and production rendering are not approved. No Telegram send or delivery-history step ran because this was a push event.
- Run: https://github.com/samiouess-ux/IslamicTikTokAutomation/actions/runs/41314717304


## Background preview package verified (2026-11-01)
- Run #154 (41315704678) completed successfully on feature/telegram-review-notifications.
- Downloaded all four staged Pexels clips to the ephemeral GitHub Actions runner, validated video streams with ffprobe, extracted center-cropped 9:16 still previews, and uploaded the contact sheet plus review report as part of artifact 13087152545 (official-quran-audio-inventory-and-probe; 41,134,275 bytes).
- Verified source dimensions/durations: ocean 2160x3840 / 5.874s; mountain lake 2160x3840 / 10.11s; sunset 2160x3840 / 5.639s; mountain bridge 3840x2160 / 12.948s. The bridge is landscape and its center crop loses some original framing.
- All candidates remain not approved and not production-enabled. The contact sheet is only a first-frame crop review; overlay contrast and motion review remain outstanding. No Telegram send/history step ran because this was a push-triggered run.
- Run: https://github.com/samiouess-ux/IslamicTikTokAutomation/actions/runs/41315704678


## Run #158 — overlay preview and candidate-background QA (2026-11-01)
- Run `41317460948` completed successfully on commit `115940fbb519c37306611381b35626fd906905d6` on `feature/telegram-review-notifications`. The previous `preview_path` KeyError is fixed; the background-QA stage now completes.
- Artifact `13087478281` contains the full Quran inventory/corpora, a review-only Surah Ar-Rahman 55:1–10 MP4 (57.65s, 1080×1920, H.264/MP3), audio report, and four Pexels background stills composited with an actual Quran overlay.
- Audio report: 10 complete ayahs selected; processed passage duration 57.861s; measured inter-ayah silence 0.24s. The candidate remains explicitly unapproved and blocked from production/Telegram.
- Four Pexels files passed download and ffprobe checks; overlay contact sheet is generated. This is a QA artifact only: all four backgrounds still have `visual_approval=false`, `production_enabled=false`, and `user_approved=false`. Do not enable any of them without the user's explicit per-background approval.
- Important limitation: the run generated one distinct-surah preview, not three videos in one run; Telegram send/history steps were skipped because this was a push-triggered run. This run does not prove a new Telegram delivery or daily schedule operation.
- Visual contact sheet needs further review: the overlay sample is a single ayah frame and should be checked for complete Quran text/ayah-number rendering and contrast before treating the design as accepted. The main preview also remains review-only.
- Next: inspect the actual preview frames and full video content, resolve any text/layout issue, then verify a scheduled Telegram delivery separately. Preserve all approval gates and manual TikTok posting.


## First scheduled Telegram delivery confirmed (2026-11-01)
- User confirmed receipt in the Telegram review bot at 18:02 Tunisia time, shortly after the 18:00 scheduled slot.
- Received review video: Surah Az-Zukhruf, ayahs 1–7; Telegram displayed 33.0 MB. Caption includes Arabic title, varied hashtags, English description, and the manual-review-only notice.
- This is the first user-confirmed scheduled-slot delivery in this verification cycle. It confirms that a scheduled video reached the user's Telegram chat; it does not by itself verify the Actions run ID, delivery-history sync, or reliability of all three daily slots.
- TikTok publishing remains manual and requires the user's personal approval. Continue monitoring later scheduled slots and confirm the GitHub run/history record before declaring the schedule fully reliable.


## Second scheduled Telegram delivery and history sync verified (2026-11-01)
- Scheduled GitHub Actions run #159 (`41329118203`) completed successfully on `feature/telegram-review-notifications` at 17:02:53 UTC (18:02:53 Tunisia time).
- The engine selected Surah Az-Zukhruf (43), ayahs 1–7, and rendered a 60.15-second 1080x1920 H.264/MP3 review video, within the 65-second cap.
- Telegram `sendVideo` returned `ok: true` with real `message_id=30` and a 33.0 MB video. This matches the user's Telegram receipt at 18:02.
- The workflow then recorded exactly the seven selected ayahs (43:1–43:7) and successfully committed/synced `data/quran_delivery_history.json` back to the active feature branch (`18bed634d52a90e113dacfa478419788e17cad77`).
- Full inventory, 6,236-entry Arabic/translation/audio join, regression tests, eight-surah candidate pool, one-slot audio preparation, manifest generation, review MP4 rendering, and background QA preview steps all passed in the same run.
- This confirms one additional successful scheduled slot and exact delivery-history sync. It does not yet prove that all three daily slots run reliably over multiple days. Only one video is generated per scheduled slot; TikTok remains manual.
- The run artifact is `13092647613`. The four Pexels backgrounds remain QA candidates only; none is user-approved or enabled in production.


## Quran opening cover implementation (2026-11-01)
- Added a short surah-title opening cover to the review renderer on `feature/telegram-review-notifications`.
- The cover displays the Arabic surah name and exact selected ayah range in the established gold cartouche style. It fades away over the first ayah; original Quran audio starts at 0 seconds, with no silent lead-in and no audio modification.
- Added renderer regression coverage for the cover image, exact ayah range passed to it, and FFmpeg alpha-fade overlay. The normal 1080x1920, MP3-preservation, <=65-second and review-only gates remain unchanged.
- This is a code/test implementation checkpoint. Wait for the push-triggered Actions test/render run and inspect its artifact before calling the new visual verified or asking the user to use it. TikTok cover selection and publishing remain manual.


## Background rotation render checkpoint (2026-11-01)
- Push-triggered GitHub Actions run `41342769583` completed successfully on the active feature branch at commit `84479e96e8eb47caccea317c2bccd9f79b14723a`.
- All job steps passed, including Quran catalog regression tests, diverse distinct-surah candidate selection, one-slot preparation, 9:16 review-only video rendering, and download/crop preparation of the four visually user-approved Pexels backgrounds with actual Quran overlay.
- The daily review renderer now calculates a UTC day-and-slot rotation index for the scheduled slots (03:00, 11:00, 17:00 UTC) and selects the matching approved background. The selected background remains consistent across ayah segments within a single video.
- The isolated request pipeline test also passed on this commit. The inventory artifact is `official-quran-audio-inventory-and-probe` (artifact ID `13097433352`).
- Important boundary: this was a push-triggered validation run. The Telegram send, delivery-history record, and history sync steps were correctly skipped; this run does not prove a new Telegram delivery. The Pexels backgrounds are user-approved as visual candidates, but remain outside the separate production renderer's enabled assets until its own production/legibility gates are passed. TikTok posting remains manual.


## Scheduled delivery timing audit — 2026-11-02
- Audited the branch-filtered Actions run history and the actual job logs, not only the local delivery-history JSON.
- Scheduled run #159 (`41329118203`) started at 2026-11-01 16:59:28 UTC (17:59 Tunisia), completed at 17:02:53 UTC, and Telegram confirmed `message_id=30`. It delivered Surah Az-Zukhruf 43:1–7 and synced the exact seven ayahs.
- Scheduled run #177 (`41350077797`) started at 2026-11-01 21:04:25 UTC (22:04 Tunisia), completed at 21:08:19 UTC, and Telegram confirmed `message_id=31`. It delivered candidate `quran_s025_001_077`; the audio selector chose exactly Al-Furqan 25:1–3 and the recorder added only those three ayahs. History sync pushed commit `42e7593` to the active feature branch.
- The workflow cron is explicitly `0 3,11,17 * * *` UTC, intended as 04:00, 12:00, and 18:00 Tunisia (UTC+1). The run #177 event is genuinely `schedule` but its recorded start is 21:04 UTC, four hours after the 17:00 UTC cron slot. This is a GitHub scheduled-event delay, not an arithmetic offset in the project code. Do not change the cron to compensate for one delayed run; that would shift the intended slots.
- Only two scheduled events are present in the queried branch history: run #159 and run #177. No 12:00 Tunisia scheduled run is present in this audit. Thus two real scheduled Telegram deliveries are confirmed, but three daily slots and punctuality are not yet proven.
- Next: keep the explicit UTC cron unchanged; continue checking the next 04:00 / 12:00 / 18:00 Tunisia slots separately. If GitHub continues to start schedule events hours late or omits slots, document the exact delay and then choose a minimal solution within the existing GitHub Actions + Telegram architecture. Do not add an orchestrator, another bot, cloud service, or automatic TikTok publishing.
- Active branch only: `feature/telegram-review-notifications`. TikTok remains manual.


## Schedule minute adjustment (2026-11-02)
- Changed only the existing schedule in `.github/workflows/build-quran-audio-inventory.yml` from `0 3,11,17 * * *` to `10 3,11,17 * * *` UTC.
- New intended Tunisia (UTC+1) slots: 04:10, 12:10, and 18:10. This avoids scheduling exactly at minute 00, which GitHub documents as a period of elevated scheduled-workflow load; it may reduce queue delays but does not guarantee punctual starts or prove that a missing schedule trigger is fixed.
- No engine, Telegram bot, delivery logic, secrets, or TikTok behavior changed. Only `feature/telegram-review-notifications` was modified; `main` was not touched.
- Next acceptance: observe actual schedule-triggered runs for the new slots and confirm Telegram positive `message_id` plus delivery-history sync. If schedule events remain absent, investigate workflow enablement/actor state rather than adding infrastructure.


## Engine continuation and regression fixes (2026-11-02)
- Repository rechecked on `feature/telegram-review-notifications`; it remains the only active/default branch. `main` was not modified.
- Fixed a batch-audio regression-test fixture that had one too few mocked ffprobe results after the implementation began probing the concatenated MP3. Commit: `4a24def6d7a1e74d290ae5bb721bd82dd97e5a5e`. The full inventory workflow run `41460327362` passed the Quran catalog regression tests and batch-audio preparation stage; rendering was still in progress at the time of this note.
- Fixed an independent requested-surah duration bug: `select_requested_quran_range.py` had imported the scheduled batch's 40-second target as its maximum, contradicting the user's 65-second clip limit. It now uses its own 65-second limit. Commit: `69782c97aa6f7a33c873d2a34fde314553918fa0`. Isolated request-pipeline tests passed in run `41460788595`.
- A controlled Telegram dispatch attempt `41455143210` confirmed the send path was blocked because a rendered review MP4 was 68.3 MiB, above the sender's 50 MiB safety ceiling. The renderer now uses H.264 CRF 23 with a 6 Mbps VBV maximum and 12 Mbps buffer to keep a 65-second clip below Telegram's file ceiling while retaining 1080x1920/30 FPS and copying the original MP3 audio. Renderer commit: `a9d1ebffe4d0da7b5a2481acaa886c6f594fb657`; regression assertions added in `7a68a7e62c08711e3c032a82fbcdcc6fe3c3250a`. The next full inventory workflow run must confirm output size and render quality; do not claim the size fix is proven until then.
- The first isolated request-pipeline run on the renderer commit exposed the 40-vs-65-second mismatch; this was corrected and its follow-up run passed. Do not resend the already delivered test video.
- Current accepted schedule configuration remains the external Tunisia scheduler at 04:10, 12:10, and 18:10; one distinct Quran video per slot, using the same GitHub workflow and original Telegram bot. A scheduled Telegram delivery still requires a real API `message_id` and history sync. TikTok publishing remains manual only.
- Content-selection constraint to preserve: spread different surahs/passages across the daily slots; do not force all daily videos to use one surah. Friday is the special case: always prioritize Surah Al-Kahf, splitting it across slots only when necessary to respect complete-ayah and duration limits.
- Latest validation still pending for the 6 Mbps renderer settings in full workflow run `41460691894` (or its latest replacement after the active run completes). No claim of full engine readiness until Telegram delivery, exact history sync, and repeated-slot non-repetition are all verified.


## Renderer size verification (2026-11-02, run 41460691894)
- Full inventory/render workflow completed successfully on commit `7a68a7e62c08711e3c032a82fbcdcc6fe3c3250a`.
- Downloaded and inspected the actual workflow artifact. The rendered MP4 `quran_s033_043_073_REVIEW_ONLY.mp4` is 24,643,323 bytes (about 23.5 MiB), 31.846 seconds, 1080x1920, H.264 video, original MP3 audio. This is below the sender's 50 MiB safety limit. The CRF 23 / 6 Mbps maxrate / 12 Mbps buffer change therefore produced a file within the configured Telegram size ceiling in this run.
- The actual candidate in this run was Surah Al-Ahzab 33:43-44, on a moving ocean-shore background; it was not the old Surah Ash-Sharh prototype. The generated artifact also contains the 6,236-verse Arabic/translation/audio candidate catalogs and the four background preview assets.
- Important: this run was triggered by a code push, so the Telegram-send, delivery-history-record, and history-sync steps were intentionally skipped. This proves successful preparation and rendering plus safe file size, but does NOT prove a new Telegram delivery. Next acceptance must be a deliberate `workflow_dispatch`/external scheduled trigger, verify Telegram API positive `message_id`, then verify history sync. Do not count this push artifact as a delivered video.
- The workflow currently declares `push` and `workflow_dispatch` triggers in its YAML; there is no native GitHub `schedule` trigger in that file. The 04:10/12:10/18:10 Tunisia timing therefore depends on the already-configured external scheduler invoking workflow dispatch. Confirm that scheduler's three local-time triggers independently; do not add a second scheduler or infrastructure without need.


## Daily scheduler reality check (2026-11-02)
- Inspected the active branch's actual `.github/workflows/build-quran-audio-inventory.yml`: its `on:` block currently contains only `push` and `workflow_dispatch`; there is no GitHub Actions `schedule` trigger. Therefore this workflow itself cannot start at 04:10, 12:10, or 18:10 Tunisia time at present.
- GitHub repository metadata confirms the default branch is `feature/telegram-review-notifications`, so a GitHub Actions cron added later to this workflow would be eligible to run on the intended branch without touching `main`.
- The repository's Cloudflare Telegram bridge is only an on-demand webhook worker; the handoff records that Worker/KV/secrets/webhook deployment is not configured. No deployed external daily scheduler is evidenced in the repository. Do not assume an external scheduler exists.
- Do NOT activate the daily schedule yet. The actual MP4 build and size are now verified (23.5 MiB, 31.846 seconds, 1080x1920), but the latest successful run was a push event and skipped Telegram send/history steps. A controlled real Telegram MP4 delivery and history sync are still mandatory acceptance gates. Once those pass, add a native GitHub Actions cron of `10 3,11,17 * * *` UTC (04:10, 12:10, 18:10 Tunisia, UTC+1) to this workflow, then verify each scheduled delivery and history update. GitHub scheduled starts may be delayed under load.
- The latest candidate was Surah Al-Ahzab 33:43-44, not the old Ash-Sharh-only prototype. This confirms the review candidate selector can produce a different surah in this build, but does not alone prove long-term no-repeat behavior; verify history exclusion over confirmed deliveries.
- No TikTok auto-publishing is enabled. User continues to approve/download/post manually.


## External Cron and confirmed Telegram delivery (2026-11-02, supersedes earlier scheduler notes)
- User-confirmed external scheduler is cron-job.org, job Quran Video Scheduler, enabled in Africa/Tunis at 04:10, 12:10, and 18:10. It POSTs GitHub Actions workflow_dispatch to this active branch. Preserve this configuration exactly; do not add a native GitHub schedule or another scheduler.
- A real workflow-dispatch run 41463758861 started at 2026-11-02T14:37:44Z on branch feature/telegram-review-notifications (commit 5df43a84162eef13b6b52aab3b4a346518e41b2b). This is evidence the external Cron dispatch reached GitHub.
- The run completed successfully. Distinct-surah rendering, review background preparation, Telegram send, delivery-history recording, and history sync all completed successfully.
- User independently confirmed receiving the MP4 in Telegram: Surah Al-Ahzab, ayahs 43-44, ocean background, about 30 seconds. The generated artifact was measured at 31.846 seconds, 1080x1920, H.264 with MP3 audio, 24,643,323 bytes (about 23.5 MiB), below the Telegram 50 MiB limit.
- Confirmed history now includes 33:43 and 33:44, with delivery timestamp 2026-11-02T14:40:54.387854+00:00; history sync to the active branch succeeded. The selector must continue excluding these delivered ayahs.
- This supersedes the earlier incorrect statements that no external scheduler was evidenced and that a controlled Telegram delivery/history sync was still pending. Earlier notes are retained as historical checkpoints, not current state.
- Acceptance achieved for one real external-Cron-to-Telegram cycle. Continue verifying future scheduled slots and no-repeat behavior; this single success does not prove every daily slot or the 65-second maximum across all content.
- No TikTok auto-publishing. User downloads/reviews and posts manually.


## Quran clip duration selection update (2026-11-02)
- Updated scheduled batch audio selection from the previous hard 30-40 second window to the longest contiguous whole-ayah prefix up to 65 seconds. There is no artificial 30-second minimum, so short complete surahs/passages can remain whole. No ayah is cut to fit; a single ayah longer than 65 seconds is blocked rather than trimmed.
- Regression coverage now checks a 44-second three-ayah passage is retained, a short 12-second complete passage is accepted, and a 66-second single ayah is blocked. Existing edge-silence-only trimming and MP3 stream-copy behavior remain in place.
- Full inventory workflow run 41465562249 completed successfully on commit 0cb41f749ac97e07bf93bf37aeb8f018478a2330. Quran catalog/audio regression tests, candidate preparation, draft manifest generation, and review preview rendering/background preparation all passed.
- This was a push-triggered validation run; Telegram send/history steps were skipped by design. Do not count it as a new Telegram delivery. The previously confirmed Cron-to-Telegram delivery remains run 41463758861.
- Follow-up: implement and test Friday-only Surah Al-Kahf selection across the daily slots, preserving complete ayah boundaries, 65-second cap, and history-based no-repeat. Do not alter the external cron-job.org schedule.


## Friday Al-Kahf selection implementation (2026-11-02; full workflow validation pending)
- Added Tunisia-local weekday detection using Africa/Tunis timezone in the existing workflow. On Fridays, the candidate builder is restricted to Surah Al-Kahf (18), selects the first unused contiguous ayah suffix, and bypasses the normal last-surah exclusion so the 04:10, 12:10, and 18:10 slots can continue the same surah without repeating delivered ayahs.
- On non-Fridays, Al-Kahf is excluded and the existing eight-distinct-surah selection remains; the existing Ash-Sharh (94) exclusion is preserved.
- Added a regression test proving Friday mode selects Surah 18 and continues at ayah 3 after 18:1-2 have already been delivered. Quran batch engine test run 41466300540 passed.
- Full workflow run 41466486385 is the first validation of the updated weekday-aware workflow and is still in progress at this checkpoint. Do not claim the workflow-level Friday logic is fully accepted until this run completes successfully. This push run does not send to Telegram.
- External cron-job.org settings remain unchanged. Friday sends will still be subject to the same Telegram confirmation and history-sync requirements.


## Corrected video duration policy (2026-11-03)
- User confirmed the intended hard maximum is **40 seconds**, not 65 seconds. The audio preparation constant and report maximum are 40.0 seconds; no minimum duration is imposed.
- Each distinct-surah candidate now produces exactly one video preview: the longest contiguous prefix of complete ayahs that fits within 40 seconds. Any later ayahs remain explicitly unselected for a future batch; they are not split into extra videos from the same candidate.
- A single ayah over 40 seconds is deferred intact. The concatenated MP3 duration is measured and rejected if it exceeds 40 seconds. No ayah is cut and recitation is not sped up.
- Regression expectations were corrected to 40 seconds, including the short-surah no-minimum case. Push validation runs are pending; do not mark the fix accepted until all relevant checks complete successfully. Push runs do not send Telegram.


## Saved checkpoint — 2026-11-03 01:48 UTC
- Active branch: `feature/telegram-review-notifications`; latest code/test commit: `414af9d3b7eec2069cd16a70b9bab20449a12e80`. `main` was not modified.
- Final 40-second policy is implemented: one preview per candidate, longest contiguous complete-ayah prefix at or below 40 seconds, no artificial minimum, and deferred ayahs remain unselected for later continuation. Single ayahs longer than 40 seconds are deferred intact. Measured concatenated audio is rejected above 40 seconds.
- Validation workflow run `41561966290` passed; engine validation ran 53 tests successfully, plus the six orchestrator tests. Earlier run `41561962171` also passed validation. The inventory run `41561966410` was still pending at checkpoint.
- Push validation is test-only; no Telegram send was initiated. Wait for the inventory workflow result and do not claim a scheduled delivery occurred.


## Orchestrator audit — 40-second pipeline repairs (2026-11-03)
- Active branch only: `feature/telegram-review-notifications`; `main` untouched. Current code checkpoint: `8906b44654301bb6ad2d11758e9758b79a7cfc95` (documentation-only design clarification follows).
- Fixed the scheduled renderer's incorrect requirement that selected ayahs equal the entire source candidate. It now renders only the longest selected opening contiguous prefix; deferred ayahs remain out of the preview and history.
- The renderer now rejects a final MP4 longer than 40.0 seconds. Manual Telegram surah requests and their failure notices also use the same 40-second cap. No artificial minimum is imposed.
- Fixed delivery reservation/finalization to map a selected audio-part ID back to its source candidate ID. Reservation validates the review-only preview, actual MP4/audio duration <=40 seconds, and exact selected ayah prefix; finalization verifies the same selection before recording history.
- Fixed the scheduled workflow's candidate identity check and the >40-second deferred-ayah notification. Normal days exclude Al-Kahf (18) and Ash-Sharh (94); Friday remains sequential Al-Kahf only.
- Validation evidence: Quran engine run `41562954128` passed 56 tests plus 6 orchestrator tests; isolated request workflow `41563104562` passed. Latest full inventory run `41563104763` is still in progress at audio preparation; do not claim end-to-end rendering until it completes.
- The earlier inventory run `41561966410` failed at rendering because of the full-candidate-vs-selected-prefix mismatch. This root cause has been fixed; the current inventory run is the required confirmation.
- Push validations do not send Telegram. No test send was made. External cron-job.org remains unchanged at the user-confirmed 04:10, 12:10, and 18:10 Africa/Tunis; this repository cannot independently verify the external job's live state. No new scheduler or infrastructure was added.
- Background rendering uses the four explicitly user-approved, download-verified Pexels candidates in `data/background_candidates.json`; renderer rotation and real overlay readability still require the current full workflow artifact to pass and visual inspection.
- TikTok publishing remains manual. Qur'an content remains Arabic + Saheeh International English, authentic recitation, no music, and no public reciter name.


## Project handoff checkpoint — 2026-11-04
- Active branch: `feature/telegram-review-notifications`. Latest verified branch HEAD at this checkpoint: `452cec4e462d0b10cf67909b8c2db061032db9b9`. The recent commit sequence includes the isolated background review workflow, candidate batch, tests, and unittest-discovery correction. `main` was not modified.
- An existing project continuity file, `PROJECT_STATUS.md`, was already present. This checkpoint updates that file; no duplicate status/handoff file was created.
- Background review batch 01 is prepared as a separate, manual-only workflow. Candidate metadata is in `data/background_review_candidates_batch_01.json`; the preparation script is `src/prepare_background_review_batch.py`; safeguards are in `tests/test_prepare_background_review_batch.py`; workflow is `.github/workflows/review-background-candidates.yml`.
- The batch contains six unapproved Pexels candidates: ocean sunset, waterfall at night, tropical river, desert panorama, desert mountains in rain, and mosque/river greenery. All remain `approved=false`, `user_approved=false`, `download_verified=false`, and `production_enabled=false`.
- The independent workflow is `workflow_dispatch` only. It is designed to download/probe the candidate videos, create vertical crops and a contact sheet, and upload a review artifact. It does not send Telegram, alter the production background catalog, change the Quran production workflow, or publish anything.
- Three safeguard tests were added, including checks that candidates remain unapproved and duplicate IDs or pre-approved candidates are rejected. The workflow runs unittest discovery before preparation. These tests have been added to the workflow but have NOT yet been executed in a workflow run at this checkpoint.
- The background review workflow has NOT been manually dispatched. No actual downloads, ffprobe verification, contact sheet, or artifact have been produced yet. Wait for the user's explicit approval before dispatching this review workflow.
- Next step after approval: dispatch only `review-background-candidates.yml`, inspect its test result and generated contact sheet/report, then present the real previews for user review. Do not enable any new background in production until the user explicitly approves it.
- Preserve the existing Quran Telegram delivery workflow and its successful send path. Do not change the external cron-job.org schedule, Telegram bot/secrets, production workflow, or `main` without explicit user approval. TikTok publishing remains manual.


## Background review validation fix — 2026-11-04
- After the first manual review-workflow run failed in the duplicate-ID safeguard test, the review preparation script was corrected to validate the entire candidate manifest (unique non-empty IDs, unapproved state, and trusted Pexels URL prefixes) before creating the output directory or downloading any video.
- The duplicate-ID test now asserts that the download function is never called and that no output directory is created when duplicate IDs are present.
- Commits: `9b92376b6180d97ad540e8b6fe5c870664d3dd08` (pre-download manifest validation) and `9f7f77813bd74903769e06efb4f323403245a68e` (regression test).
- These changes are on `feature/telegram-review-notifications` only. The corrected tests have not yet been executed; the failed prior workflow run is not evidence of a passing fix. The review workflow has not been re-run, and no candidate video downloads/previews have been verified yet.
- Production Telegram delivery, the production workflow, external cron schedule, production background catalog, and TikTok publishing settings remain untouched.


## Background review workflow retry — 2026-11-04
- The isolated review workflow was retried as run 41872298890 (attempt 2). The three review safeguard tests all passed, including the duplicate-ID pre-download rejection test.
- The preparation script completed successfully and reported that six unapproved candidates were prepared. The workflow log confirms no production catalog or Telegram delivery was changed.
- The run was marked failed only at the artifact-upload step: GitHub Actions artifact storage quota was exhausted. The upload step found 14 files, but GitHub rejected artifact creation; therefore no downloadable contact sheet/source-clip artifact is available from this run and visual review is still pending.
- This is a storage-capacity failure, not a test or candidate-download/preparation failure. Wait for GitHub's artifact-usage recalculation (the log says 6–12 hours) before retrying the artifact upload. Do not alter production delivery, Telegram, external cron, production backgrounds, or TikTok behavior.


## Telegram delivery reconciliation and archive outage — 2026-11-04
- Workflow run `41863220136` completed a real Telegram `sendVideo` for Surah At-Tariq (86), ayahs 1–6. Telegram returned `ok: true`, `message_id=43`; MP4 size was 29.4 MiB. The run used `workflow_dispatch` with the test-only path, so it intentionally skipped automatic delivery-history finalization.
- Reconciled the confirmed delivery into `data/quran_delivery_history.json` on the active branch, including only ayahs 86:1–86:6 and the Telegram message ID, to prevent the selector from repeating the same passage.
- Later archive inventory runs `41874874396`, `41890010470`, and connectivity check `41893063721` failed because the official King Fahd Complex archive endpoint returned repeated HTTP 503 responses. The failure occurred before inventory/audio selection; rendering and Telegram delivery were not reached in those runs.
- Existing archive retry policy is already bounded and fail-closed. Do not switch to an unverified recitation source or mix audio and timestamps. Retry production through the existing scheduled workflow when the official endpoint recovers; preserve the existing Cron and Telegram configuration.

## Maher Al-Muaiqly archive mirror failover and byte-level verification (2026-11-04)
- Active branch: `feature/telegram-review-notifications`; `main` and the separate Saad experiment were not changed.
- Added official-host-first archive selection with a pinned Quran.ws mirror fallback only when the official King Fahd Complex endpoint fails preflight. The mirror is independent, not an official Complex host; its published SHA-256 matches the checksum published by the Complex for the Maher Al-Muaiqly Ayat ZIP.
- Added a mandatory full-download SHA-256 calculation before ZIP inventory enumeration. The downloaded archive is rejected unless its computed digest equals the pinned official checksum. Temporary archive bytes are deleted after inspection.
- Relevant commits: `c6a63bb` (source failover), `2afbc8d` (selection tests), `3b2a4b9` (actual downloaded-file SHA-256 verification).
- Run `41929393545` was still in progress at the archive-inspection step when this checkpoint was recorded. Run `41929573386`, containing the SHA-256 change, was queued behind it. Neither run has validated the archive or generated a Telegram video yet.
- The inventory remains review-only. No Telegram send was initiated; delivery history was not modified by these push validations. `data/quran_delivery_pending.json` is absent at this checkpoint.
- Do not claim mirror validation, full 6,236-verse mapping, or video delivery until the corresponding workflow steps complete successfully. Keep Maher Al-Muaiqly as the production reciter.


## Maher audio manifest and ZIP-member matching checkpoint — 2026-11-04
- The manifest-based archive inventory now passes its workflow step: the 6,236-verse manifest mapping is complete, with no missing or duplicate canonical verse keys. The workflow also passed the full Saheeh International translation corpus, Uthmani Arabic candidate corpus, exact-key join, and review-only rendering-gate checks.
- The next regression suite exposed four fixture errors in `tests/test_prepare_quran_review_batch_audio.py`: its FakeArchive initially lacked `namelist()`; the subsequent fixture implementation also needed canonical KFGQPC verse basenames rather than generic test filenames. Production resolution intentionally requires a unique canonical basename match against the ZIP central directory.
- Run `41931627815` passed archive inspection, translation, Arabic corpus, exact-key join, and rendering-gate validation, then failed the audio batch regression suite. The workflow's later steps, including candidate audio preparation, rendering, and Telegram, were not executed.
- Run `41931627846` failed its parallel renderer/catalog test suite at the same audio batch fixture issue. No Telegram delivery was attempted by either run.
- Corrected the FakeArchive test fixture to enumerate canonical `10-SSSAAA-A08.mp3` basenames for the complete 6,236-verse Quran inventory and updated the small test inventories to use those canonical basenames. Commit: `5ae3e48d198e88ee6a51a8d0af78992fcf4b2e87`.
- Next: rerun the targeted audio-batch regression suite and the full Quran validation workflows. Only after they pass, inspect actual range-downloaded MP3 members, duration/probe results, review-only MP4 previews, and Telegram confirmation. Do not alter delivery history, cron schedule, `main`, or the reciter (Maher Al-Muaiqly). No new Telegram send has been confirmed at this checkpoint.


## Audio batch regression follow-up — 2026-11-04
- The next full renderer/catalog test run reached 60 tests; 59 passed. The only remaining error was one deferred-long-ayah fixture still using the old synthetic filename `2-1.mp3`, while the new archive resolver correctly requires the canonical basename `10-002001-A08.mp3`.
- Updated that final test fixture to use the canonical Maher archive filename. Commit: `ebf24f9fad4e65198a45d9787c46dffcc5d5afdb`.
- No production audio logic was weakened and no ambiguity fallback was introduced. The new commit should trigger another validation run; await its test results before proceeding to actual audio preparation/rendering.
- No Telegram send or delivery-history update occurred in these push-test runs. Preserve existing Cron, production history, Maher Al-Muaiqly recitation source, and manual TikTok publishing.


## Verified Quran review render checkpoint — 2026-11-05
- Workflow run `41932468888` completed with conclusion `success` on commit `d7e7d69f203d9c72b9e9259b63fb1b609ec021a2`.
- Confirmed successful steps: official audio inventory inspection, full Saheeh International corpus, 6,236-entry Uthmani candidate corpus, exact-key Arabic/translation/audio join, review-only gates, catalog regression tests, Tunisia Friday logic, one distinct-surah audio candidate prepared from the Maher archive, draft manifest generation, 9:16 H.264/MP3 review preview rendering, and four background crop previews with actual Quran overlay.
- The workflow's artifact upload step was configured with `continue-on-error: true`; the run artifact listing returned no artifacts. Therefore the MP4 was rendered during the job, but no downloadable artifact is available from this run. Do not claim the user received or can download the video.
- Telegram reservation, send, delivery-history update, and sync steps were all skipped for this push-triggered validation. No new Telegram message was sent and no production delivery history was changed.
- Next: resolve artifact availability/retention before relying on the generated preview as a user-deliverable file. Do not alter external Cron, `main`, experiment branch, or production delivery history.
