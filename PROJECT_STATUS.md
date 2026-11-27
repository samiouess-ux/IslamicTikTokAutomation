## Unified background library architecture review — 2026-11-23

- Confirmed the existing sources are separate: `data/background_candidates.json` (17 video records; 13 pass the strict approved + user-approved + download-verified + 9:16 filter) and `data/background_photos_manifest.json` (35 previously user-approved photos, all 35 local assets present and downloaded/image-decoded/dimension-verified by the photo download workflow).
- Confirmed the renderers are separate by design: video clips use `build_background_reel()`; still photos use `build_photo_background_reel()` with gentle zoom and crossfades. Keep these media-specific rendering paths so photos are not treated as video files and videos retain their clip-duration/probe safeguards.
- Found a flag interaction in `.github/workflows/render-manifest-video.yml`: both `use_photo_backgrounds` and `use_background_rotation` default to true, but in `render_video_scenes.py` the photo branch builds the background reel instead of the selected video sequence. Thus this workflow's default run uses the photo reel; the video sequence selected earlier is not the reel source. This is a review-workflow behavior, not evidence of a change to the scheduled production path.
- Confirmed `src/asset_rotation.py` is a generic approved-asset selector but currently does not unify the photo and video background catalogs.
- Recommended implementation: one shared background-library intake/eligibility/approval layer that normalizes photos and videos with an explicit `media_type`, while retaining separate photo/video render adapters. First integrate and test the shared library in an isolated review-only path; do not change the daily production renderer, schedule, Telegram, design, zoom, or background choice until the user reviews a rendered preview and separately approves activation.
- No renderer, workflow input defaults, production settings, schedule, Telegram, credentials, Cron, or TikTok behavior changed during this architecture review.
 
## Restore recorded approval for existing photo library — 2026-11-23

- User clarified that all 35 photos in `data/background_photos_manifest.json` had already been visually approved in earlier review. The previous commit's assumption that no approval existed was incorrect; it is superseded by this correction.
- Recorded the user's existing approval at manifest level, explicitly scoped to the 35 existing candidates. This does not pre-approve future additions.
- Updated the photo eligibility loader to honor that recorded approval and independently verify each local image file (exists, at least 50 KB, decodable image, minimum 720 px dimensions). Invalid or missing files are skipped; newly added photos are not covered by the existing approval scope.
- Added tests for previously approved photos and fail-closed behavior when approval metadata is absent.
- This changes only the optional photo eligibility gate. It does not switch photo backgrounds on in the production schedule, change video rotation, design, zoom, schedule, Telegram, credentials, Cron, or TikTok.
- The earlier render-only test run on commit `fcda6c9` passed the Quran batch engine tests; its background-review run failed at publishing preview images after the validation and render steps had passed. The subsequent background-review run for commit `25ea8a9` completed successfully but was against the earlier approval-gate implementation. This corrected approval-record change still requires exact-commit validation.
 
## Background approval safety correction — 2026-11-23

- Active branch: `feature/telegram-review-notifications`; latest known HEAD before this change: `8239b910ec595ba909176013ea956540d1da8dd4`. `main` was not changed.
- Confirmed the video catalog has 17 records, of which 13 currently pass the existing strict 9:16 + approval + download-verification filter. The two newly reviewed mosque clips were downloaded, ffprobe-verified, activated by the background-review workflow, and added to the video catalog. Workflow run `45149427845` completed successfully; its preview/test/activation/publish steps all passed.
- Found a safety gap in the separate photo path: `build_photo_background_reel()` previously treated any sufficiently large local file as eligible, without checking explicit approval or download-verification flags. The 35-entry photo manifest currently has no such flags, so none of those photos has machine-recorded approval status.
- Added a fail-closed photo eligibility loader requiring `approved=true`, `user_approved=true`, `download_verified=true`, a unique ID, and an existing local file of at least 50 KB. The optional photo-render path now uses this loader. Existing photo entries remain pending and are not auto-approved.
- Added regression tests for explicit photo approval and for keeping the existing unreviewed photo manifest out of eligibility.
- This is a safety-gate correction only. It does not enable photo backgrounds, change the default video rotation, alter visual design/zoom, schedule, Telegram, credentials, Cron, or TikTok behavior. No production render, Cron run, Telegram send, or TikTok publish was triggered.
- Validation of this exact change is pending. Next: run the branch's render-only background tests, then build a unified photo/video asset intake and review process while keeping all unapproved assets excluded.
 
## Opening fade and moving-background render verified — 2026-11-21

- Latest active branch HEAD before this status update: `e7c1782584f06b733063caf4cf8bc22bfe27be77` on `feature/telegram-review-notifications`; `main` was not changed.
- Corrected the ayah-frame renderer so the surah title/ornament are not baked into every ayah layer; they exist only in the transparent opening overlay and can fade away cleanly. The first ayah's opening background is now required to be an approved moving-video asset; later ayahs continue using the approved mixed photo/video catalog.
- Added regression coverage for omitting the surah header from ayah layers and for requiring a moving-video background in the opening scene.
- Exact-commit validation passed: Quran batch engine run `44955476007`, isolated Quran request pipeline run `44955476003`, and full inventory/render run `44955475999`.
- Downloaded and inspected artifact `quran-visual-review-samples` (artifact ID `14727009338`) from run `44955475999`. The review-only MP4 is 1080x1920, 47.921 seconds, H.264 video + original MP3 audio. It contains Surah Al-Hijr, ayahs 1–4. The first frame shows the first ayah and Saheeh International translation underneath the opening title/range overlay; sampled frames show the title/ornament fading away by about 3 seconds, while the first ayah remains visible. Extracted frames at different times show the first-scene Mostar river background is moving video, not a still image. The report records the opening overlay as transparent, 1.2 seconds total with a 0.8-second fade beginning at 0.4 seconds; audio and ayah scene begin at t=0.
- Workflow reserve/send/history/sync/notify Telegram steps were all skipped because this was a push-triggered render-only validation. No Telegram message/video was sent, no Cron job was triggered, no delivery history was mutated, and no TikTok publishing occurred. Artifact report explicitly marks production approval, Telegram delivery, and auto-publishing false.
- This verifies the opening behavior for this render sample; it does not by itself establish production approval or confirm the next scheduled Telegram delivery. Keep delivery review-only until the user explicitly approves.
- Next: retain this render as the verified technical checkpoint and await the user's decision before any production send. Do not trigger Cron or manually dispatch Telegram delivery.

## Opening overlay regression fix and validation — 2026-11-21

- Root cause found from the full inventory/render workflow log: `make_intro_frame()` still required a separate still-background image, although the opening layer is transparent and FFmpeg composites it over the live first ayah scene. This stale guard caused the production render stage to stop before generating a preview.
- Removed only that obsolete background-file requirement; retained the optional parameter for caller compatibility. The moving background, first ayah, and original audio remain on the underlying scene from frame 0.
- Updated the intro-frame regression test to call `make_intro_frame()` without a still background image, while checking the output remains a transparent RGBA title overlay.
- Source commit: `9ea4a620e1f3fd331958b7a158a9eea4942770e2`; test commit / current branch HEAD at this checkpoint: `d9eef22107134287ae2d7547fd3b3f4dd76131d0`.
- Validation on the exact test commit: Quran batch engine run `44954479484` passed, including compilation, full catalog/batch/visual tests, reference-driven sample render, and daily orchestrator test. Isolated Quran request pipeline run `44954479409` passed.
- Full inventory/render workflow `44954479429` was still running at the time of this note. It is a push-triggered render-only workflow; the workflow explicitly disables Telegram reservation/send on push. Do not claim a full MP4 render or visual artifact passed until that run completes and its artifact is inspected.
- No Telegram message/video was sent, no Cron job was triggered, no TikTok publishing occurred, and `main` was not changed. All commits remain on `feature/telegram-review-notifications`.
- Next: check completion of run `44954479429`; if it succeeds, inspect the generated preview's first frame and verify the title/ornament remains over the first ayah without a still cover.

## First ayah visible from the opening frame — 2026-11-21

- User reviewed the actual Telegram MP4 and confirmed the requested adjustment: keep the approved surah title/ornament and ayah-range intro, but make the first Arabic ayah and its English Saheeh International translation visible immediately from frame 0.
- Updated `src/render_quran_review_previews.py` so the opening title/range is rendered as a transparent overlay instead of an opaque full-screen image of the background. The first ayah scene and original audio therefore remain visible/playing underneath from the first frame; only the transparent title/range layer fades out using the existing timing.
- Preserved the approved background, ornament pixels, Amiri Bold title, Arabic/English ayah layout, medallion, audio stream, scene cuts, duration policy, review-only behavior, and delivery/scheduling configuration.
- Added regression assertions in `tests/test_render_quran_review_previews.py` for transparent intro pixels, first-ayah visibility from time zero, and the existing overlay fade.
- Source commit: `55b81aad77487fc631a97731d0504342f63a7dab`; test commit: `5908275dc6f536f5315d0272593beef89b11aa08`.
- Validation runs for the exact test commit are in progress: Quran batch engine `44954137105`, isolated request pipeline `44954137203`, and full inventory/render `44954137121`. Do not claim validation passed until these finish.
- No Cron run, production workflow dispatch, Telegram send, TikTok publishing, or change to `main` was performed. All changes are on `feature/telegram-review-notifications`.
- Next: verify the exact-commit workflow results and inspect the generated render artifact before asking the user to test the next normal delivery.

## Reference-renderer verification checkpoint — 2026-11-20

- Active branch HEAD for the renderer change: `1fc2653e959127dcb662fe5da21800a52f761bd3`; `main` was not touched.
- Latest change mirrors the original left title ornament pixels horizontally to form the right ornament, avoiding the previous right-side color-key contamination from the reference sunset background.
- Quran batch engine tests run `44767324280` completed successfully; its artifact `quran-reference-layout-preview` (artifact ID `14646337091`) was downloaded and visually inspected. Isolated request pipeline run `44767324293` passed. Background review run `44767324368` passed.
- The new preview shows both title ornaments complete and symmetrical, the original floral divider, dynamic gold ayah medallion, white Arabic, and English Saheeh International translation. The artifact uses a neutral dark test background; it is not a final moving-background MP4 and does not prove pixel-identical typography for every surah. Human approval of the exact reference match remains pending.
- Full inventory workflow run `44767324340` stopped safely before rendering: the first candidate, Al-Kahf 18:19, measured `66.116` seconds as one complete ayah, exceeding the hard 60-second single-ayah ceiling. Rendering, Telegram delivery, history update, and TikTok publishing were skipped. No Quran text/audio was cut or sped up.
- No Cron execution, production Telegram send, TikTok publishing, schedule/credential change, or modification to `main` occurred.
- Next: inspect the candidate-selection handling for a whole ayah that exceeds 60 seconds so one exceptional ayah cannot block the entire daily candidate, while preserving the complete-ayah rule, 60-second ceiling, no-repeat history, and explicit deferred tracking. Do not relax the duration guard or trigger production delivery. Keep visual approval pending until the user confirms the preview matches the reference.
 
## Reference-renderer follow-up — 2026-11-20

- Refined the reference ornament extraction to reject smooth background glow using local edge detail plus gold-color masking.
- Cleared only the central digit area of the reference ayah medallion before drawing the dynamic Arabic-Indic ayah number.
- Adjusted Arabic title/ayah font sizing and increased spacing from the medallion; narrowed the English translation line width to reduce crowding.
- Render-only validation run `44738115227` completed successfully, including module compilation, Quran catalog/batch/visual tests, sample still rendering, artifact upload, orchestrator test, and test-only safety check. Its artifact was `quran-reference-layout-preview`.
- A subsequent renderer refinement is on branch head `0741c38ea1231b92ec93b857cc17b573185b3a52`; a fresh CI run for that exact head has not yet been confirmed. The sample artifact from the earlier successful run is not proof that this latest refinement is visually correct.
- No Telegram delivery, Cron execution, TikTok publishing, or production scheduling was performed. `main` remains untouched.
- Next: run/verify tests against the latest branch head and inspect the resulting sample against `references/approved_quran_design.png` before calling the design approved.

## Approved reference renderer — visual sample and validation update (2026-11-20)

- Source image: `references/approved_quran_design.png`; original PNG remains unchanged.
- Renderer now extracts the reference's title brackets, floral divider, and ornate ayah medallion directly from the image using a gold/detail mask. The former hand-drawn bracket/divider implementation has been removed.
- The Arabic text zone is centered below the divider, the verse marker is placed at the reference's left position, and the English translation is constrained to the four-line reference width for the Al-Kahf 18:7 sample. Text fitting still preserves complete Arabic/English content.
- A dedicated test-only workflow step renders still previews and uploads artifact `quran-reference-layout-preview`. Artifact from run `44739340182` (artifact ID `14630530123`) was downloaded and visually inspected. It is a still-layout sample composited over a neutral gradient, not a final moving-background MP4.
- Validation: Quran batch engine tests run `44739340182` passed; isolated Quran request pipeline run `44739340187` passed. The test workflow also verified it does not send Telegram or publish to TikTok. Earlier failures were corrected: the old-font-size assertion and the four-line width expectation were updated to the reference layout.
- The separate full inventory/render workflow run `44739340225` failed before rendering because Friday Al-Kahf ayah 18:19 measured 66.116 seconds, above the existing 60-second single-ayah ceiling. It was correctly deferred; this is an audio-duration/candidate-selection blocker, not a visual renderer failure. No Telegram send occurred.
- Visual review confirms the reference-derived ornament shapes are now used, but this sample is not yet final human approval of every surah title/verse layout. The dynamic title text remains typeset with Amiri Bold; do not claim pixel-identical calligraphy for every surah.
- No Cron, Telegram, or TikTok action was triggered. `main` remains untouched. All work is on `feature/telegram-review-notifications`.
- Next: continue visual refinement against the same reference and separately investigate the existing Friday long-ayah candidate-selection blocker without relaxing the duration guard.

## Approved reference implementation — 2026-11-20

- The user-confirmed source image is stored at `references/approved_quran_design.png` (the original uploaded PNG, unchanged).
- The image was retrieved and visually inspected from the conversation file library. It is the binding visual reference; no substitute ornament or redesigned layout is approved.
- Replaced the hand-drawn title brackets/divider in `src/render_quran_review_previews.py` with gold-pixel extraction from the original reference image. The renderer now fails closed if the reference PNG is missing.
- Replaced the simple circular ayah marker with the ornament pixels extracted from the reference medallion; the ayah number remains dynamic.
- Repositioned the Arabic and English text zones toward the reference composition while preserving full-ayah/full-translation fitting safeguards.
- Updated `tests/test_render_quran_review_previews.py` to assert that both title brackets, divider, and medallion are sourced from the checked-in reference. Added the reference image to the inventory workflow's push path filters.
- Validation: Quran batch engine tests run `44737796585` passed; isolated Quran request pipeline run `44737796430` passed. Full inventory/render/artifact workflow run `44737801914` was still in progress at the last check. A prior run on the renderer-only commit failed because tests still asserted the old hand-drawn ornament pixels; those assertions were updated in the next commit and the two test workflows then passed.
- Human visual inspection of a newly rendered preview is still pending; automated tests do not prove pixel-perfect visual match. Do not call the final video design approved until the actual preview artifact is inspected against the reference.
- No Cron job was triggered or changed. No Telegram send was performed. TikTok publishing remains manual. All changes are confined to `feature/telegram-review-notifications`; `main` is untouched.
- Next action: inspect the new render-only artifact from run `44737801914`, compare it with the reference, and correct any mismatch before approval.

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


## Compact video artifact recovery — 2026-11-05
- Retrieved the full log for run `41932468888`. The preview render itself succeeded: candidate `quran_s045_001_037_part_001`, Surah Al-Jathiyah 45, ayahs 1–3, duration 24.194 seconds, 1080x1920, H.264 video with MP3 audio. It is explicitly review-only; audio/render approval, Telegram delivery, and auto-publish are false.
- Confirmed why no downloadable file appeared: `actions/upload-artifact@v4` failed with `Artifact storage quota has been hit`; GitHub reports recalculation every 6–12 hours. The upload listed 96 files, including the full review package.
- Reduced the artifact payload to only the rendered MP4(s) and `preview_report.json`, retaining a 3-day expiry and non-blocking upload behavior. Commit: `83abafbedf36e4678d9f4222c781dec72589102b`.
- New push validation run `41932915149` is queued/in progress on that commit. Await its render and compact artifact result. Push validation does not trigger Telegram send; delivery/history steps remain governed by the scheduled/manual workflow conditions.


## Cover timing correction checkpoint — 2026-11-05
- Recorded the user's visual requirement: the opening cover must appear alone only briefly at the very start, then disappear completely before the Quran verse text appears; it must never remain behind or overlap the verse text.
- Renderer update on `feature/telegram-review-notifications`, commit `49646b9a1e7ec8d5d45a07cb02373ce6804172b6`: cover visibility limited to the first 0.6 seconds with no fade; verse overlay enabled from 0.6 seconds onward. Updated renderer regression assertions accordingly.
- Validation runs #107 (Quran batch engine tests) and #100 (isolated Quran request pipeline) completed successfully.
- Review-generation run #342 (`42006714832`) status at checkpoint: in_progress; artifacts listed: 0. Current job/step snapshot: [{"name":"inventory","status":"in_progress","conclusion":null,"steps":[{"name":"Block automatic sends when a previous Telegram outcome is unresolved","status":"completed","conclusion":"skipped"},{"name":"Render distinct-surah 9:16 review-only video previews","status":"in_progress","conclusion":null},{"name":"Upload review-only Quran video preview artifacts (best effort)","status":"pending","conclusion":null},{"name":"Reserve Telegram delivery attempt before sending","status":"pending","conclusion":null},{"name":"Send one review-only video to Telegram for manual approval","status":"pending","conclusion":null},{"name":"Record Telegram-confirmed Quran delivery history","status":"pending","conclusion":null},{"name":"Notify Telegram if video preparation or delivery fails","status":"pending","conclusion":null}]}].
- Do not claim the visual correction is accepted until a rendered preview is inspected. Do not claim a Telegram delivery unless the run records a confirmed Telegram message.

## Review render run #342 result — 2026-11-05
- Run `42006714832` completed successfully. It rendered one review-only 9:16 MP4: `quran_s096_001_019_part_001_REVIEW_ONLY.mp4`, duration 35.672 seconds, 1080x1920, Surah Al-Alaq (96), ayahs 1–19.
- The generated `preview_report.json` confirms the opening cover duration is 0.6 seconds, fade 0.0, `visible_only_at_start: true`; its note says the cover disappears before the ayah overlay. This is metadata/log evidence, not an independent visual inspection of the MP4.
- Artifact upload failed because the GitHub Actions artifact storage quota was hit. The workflow is green because upload is best-effort, but no artifact was created; no downloadable MP4 is available from this run.
- Telegram reservation/send/history steps were skipped; no Telegram delivery was made. Preserve manual review and production gates.

## 2026-11-06 — Quran overlay frame path fix

- Workflow run 42209101901 completed with failure after successfully rendering the review-only 9:16 Quran video and downloading/probing/cropping the four original background candidates.
- Root cause: the background-additions overlay step searched only the top level with `glob("ayah_*.png")`, while the earlier workflow step found the actual overlay recursively. This caused the second step to report that the actual Quran overlay frame was missing.
- Fixed the overlay lookup to use `rglob("ayah_*.png")` so both steps locate the same nested frame.
- No background was activated; the four original candidates remain unchanged, and the seven staged additions remain unapproved. No Telegram delivery was attempted on this push run.
- Fix commit: `ae374fa666ff736cdf74e08fbb0959196d0a9ac4`.


## Telegram caption sample review — 2026-11-19
- Reviewed the user-shared Telegram message for Surah Al-Humazah 1–8.
- Arabic and English caption sections are both present.
- Confirmed hashtag format: exactly **5 per video**, split into **3 Arabic + 2 English**. The user confirmed this is the intended rule.
- Sample passes the caption-language and hashtag-count check. Cross-video diversity still requires comparison across later delivered videos and the persistent social-content history.
- No code or production configuration was changed during this review.
- Detailed observation recorded in `PROJECT_MASTER_LOG.md`.

## TikTok Growth roadmap — authoritative next-step order (2026-11-19)
Follow this sequence. The user should not need to repeat these decisions.

1. **Completed — captions and hashtags (do not redo without a demonstrated defect):** bilingual captions and hooks/CTAs; exactly five hashtags per post (3 Arabic + 2 English); expanded rotating Arabic/English pools; persistent social-content rotation/history; phase 1 Arabic hashtag classification fix; phase 2 implementation and validation. GitHub Actions run #522 (`44601960747`) passed: 7 caption/rotation tests, 8 Telegram sender tests, 9 workflow-safety tests.
2. **NEXT — video-level growth and retention:** read-only audit of the opening, especially the first two seconds, visual hook, pacing, and viewer retention; then propose the smallest evidence-based improvements. Preserve Quran correctness, approved visual rules, recitation-only audio, and Telegram manual review.
3. **AFTER THAT — visual variety / anti-repetition:** audit and improve scene, background, layout, and transition rotation/history only where a verified gap exists. Do not activate unapproved assets.
4. **LATER — TikTok analytics:** explicitly deferred; not the next phase. Start only after the preceding video-level and visual-variety work.

### Continuity and safety rules
- Repository: samiouess-ux/IslamicTikTokAutomation; work only on feature/telegram-review-notifications; never touch main.
- Do not repeat completed caption/hashtag work without a specific demonstrated regression.
- Keep external Cron unchanged at the user-confirmed 04:10, 12:10, 18:10 Africa/Tunis. Do not change Telegram bot/settings. TikTok publishing stays manual.
- Inspect existing code and records before each phase. Report the concrete gap before making the smallest scoped implementation. Run only relevant safe tests and document actual evidence; never claim unverified work.
- No production test sends or schedule changes for growth validation.

**Current next action:** read-only audit of the first two seconds/opening and renderer implementation. No source code or production behavior is changed by recording this roadmap.

## TikTok Growth — opening hook implementation (2026-11-19)
- On `feature/telegram-review-notifications`, changed the opening cover from a 0.6s hard cut to a 1.2s opening that fades out from 0.4s to 1.2s.
- First ayah is composited from video time 0 beneath the cover; original recitation still starts at time 0. Quran text/audio and the approved cover artwork are not rewritten.
- Focused regression assertions updated. CI/render validation is pending; no success is claimed yet.
- No Telegram send, Cron change, TikTok auto-publishing, or production workflow dispatch was performed.
- Next: verify the push-triggered CI result, then review the generated review-only preview.


## 2026-11-19 — TikTok Growth phase 2: opening transition verified
- Active branch: `feature/telegram-review-notifications`; HEAD before this status update: `57aa4f178e629e4d60281ee0d5be272d68f7b658`.
- Opening transition change is now validated end-to-end. First ayah is present from t=0 beneath the cover; the 1.2-second cover fades out from 0.4s to 1.2s; recitation still starts at t=0.
- Regression-test correction commit: `0a0fe1c0337a67febf0985c64bd12b316db63667`. All three related push-triggered workflows passed: `44612696387`, `44612696062`, and `44612696031`.
- Cron-triggered production workflow run #527 (`44613610568`) completed successfully. It rendered the review video, prepared/composited the background previews, sent one review-only video to the original Telegram bot, recorded confirmed delivery history, and synced the history to this branch.
- User reviewed the delivered video and confirmed it was very good. This closes the visual acceptance check for the opening-transition phase.
- No Cron schedule, bot, credentials, TikTok publishing policy, or `main` changes. TikTok upload remains manual.
- **Current next action:** begin the next approved roadmap phase with a read-only audit of background/scene/layout/transition variety and anti-repetition. Do not modify production assets or workflow until a concrete gap is demonstrated and separately scoped.


## 2026-11-19 — TikTok Growth phase 3: visual variety audit
- Read-only audit completed on `feature/telegram-review-notifications`; HEAD before this status update: `a2b1648e9b3f79637c9910c9f0c85e4314752a3c`.
- Active renderer currently has 50 verified/available backgrounds in the latest Cron run: 15 moving videos + 35 photos. The actual delivered preview used a mountain-sunset photo followed by a moving mosque-waterfront clip; user approved the video as very good.
- Within one video, used background IDs are tracked so the same asset is avoided until the pool is exhausted. Four cover templates also rotate.
- Concrete gaps: no persistent cross-video background/cover usage ledger; current index is based on GitHub workflow run number, so unrelated runs can advance rotation; active renderer concatenates per-ayah segments without a dedicated transition effect between scenes. Opening cover fade is already implemented and approved; it is not a scene transition.
- The xfade function in `src/render_video_scenes.py` belongs to a separate renderer path and is not used by the active scheduled workflow. Do not assume it solves transitions in the active path.
- No source, workflow, catalog, asset, Cron, Telegram, or production settings changed during this audit.
- **Next:** propose the smallest isolated implementation for a separate, delivery-confirmed visual history plus controlled scene-transition rotation. Wait for explicit user approval before changing code.


## 2026-11-19 — TikTok Growth phase 3 implementation status
- Implemented persistent, delivery-confirmed visual history, recent background/category avoidance, recent cover rotation, and 0.35-second video-only scene crossfades on `feature/telegram-review-notifications`.
- MP3 audio is concatenated and muxed using stream copy; no audio re-encoding. The video crossfade overlap is padded/trimmed to retain the total segment duration. Existing 50 approved backgrounds, captions, opening cover fade, Telegram bot, schedule, and manual TikTok publishing remain unchanged.
- History writes are gated to successful Telegram delivery and are idempotent by candidate ID. History-only data commits are excluded from push triggers.
- Passed: Quran batch engine tests run #200 (`44618085196`) and isolated Quran request pipeline run #134 (`44618085318`).
- Pending: full actual FFmpeg render verification in inventory run #532 (`44618085215`); this is a push-triggered non-delivery run. Do not claim phase 3 complete until it passes. Next scheduled Telegram video still needs user visual review.

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
- On `feature/telegram-review-notifications`, refined only the active renderer's surah-title cartouche: a symmetrical pointed manuscript-style outline, fine inner contour, paired eight-point rosette terminals, and small mirrored arabesque leaf details.
- Preserved the Arabic surah title text, gold palette, title position, and the separate gold divider/diamond beneath the title. No Quran text, translation, audio, cover intro, verse-number medallion, background selection, duration policy, transition, Telegram, Cron, or TikTok publishing behavior was changed.
- Added renderer regression assertions for both side rosettes and the title outline. Validation is pending GitHub Actions; this visual change is not considered accepted until a rendered preview is inspected.


### 2026-11-20 — Telegram send-gate duration mismatch fixed
- Investigated scheduled/manual workflow run #540 (`44719548618`) on `feature/telegram-review-notifications`. Rendering completed for Surah Al-Kahf 18:17 as a complete single-ayah preview at 46.733 seconds. The send step then failed before invoking `src/send_telegram.py` because its inline guard still imposed a blanket 45-second cap.
- The log proves Telegram video send was not attempted: the failure occurred at the duration guard before the subprocess call. The failure-notification message was accepted by Telegram.
- Fixed the mismatch by centralizing the delivery duration rule in `src/quran_delivery_attempt.py`: 60 seconds for exactly one selected ayah, 45 seconds for multiple ayahs. The workflow send step now loads the matching prepared audio report and applies that same tested helper instead of a separate hard-coded 45-second check.
- Added unit tests for the shared 60/45-second policy and empty selections; existing reservation integration tests continue to cover acceptance of a 46.733-second single ayah and rejection of multi-ayah content over 45 seconds.
- Cleared `data/quran_delivery_pending.json` only after confirming from run #540 logs that the send subprocess was never called. No Quran delivery history was recorded and no video was sent.
- Commits: shared policy `eb78d36b71869acf60c3fb88cd92f66cdf102041`; tests `f5604c1788f3565f34505bef36f0810fb7379b34`; workflow guard `6dfbc396cd2330b2288e49320ab47917e8cf01c1`; failed pre-send reservation cleanup `20c077653b949c535b43996938145bc0b657d0a8`.
- Validation is pending for the push-triggered, non-delivery CI run. Do not rerun Cron or manually dispatch a Telegram send until the automated checks pass and the user explicitly requests the next test.


### 2026-11-20 — User-approved visual reference applied to active Quran frame
- User explicitly approved the generated full-bleed cinematic reference and requested the same composition without substitutions.
- Active ayah overlay updated to remove the dark translucent reading panel, its borders, and the full-frame tint. The live approved background remains visible edge-to-edge.
- Replaced the closed surah-title cartouche with mirrored open gold arabesque brackets; retained the title and added the fine gold floral divider beneath it. Repositioned the white Arabic ayah, left-side gold circular ayah number, and centered English Saheeh International translation to follow the reference composition.
- Text uses only a restrained dark stroke for legibility; no filled backing or panel is drawn. Quran text, translation source, audio, recitation, duration policy, background assets/rotation, transitions, Telegram delivery, Cron, and manual-only TikTok publishing are unchanged.
- Automated regression tests now assert transparent areas where panels previously appeared and the new open-bracket/divider/ayah-marker geometry. Await CI before any new Cron test; this push itself does not send Telegram.

- CI follow-up: the initial isolated renderer suite passed all rendering/layout cases except one assertion that sampled a pixel beside (rather than on) the new bracket stroke. Corrected the test sample to the stroke coordinate `(178, 438)` in commit `ed54333992f6c678f58b00894c40807de9c5d87e`; rerun workflows are pending. No production send was triggered by these push events.


### 2026-11-20 — Opening-cover mismatch found and corrected
- Reviewed the actual render-only artifact from workflow run #548 (44725233631): the ayah frame used the approved open gold brackets and transparent text overlay, but the 1.2-second opening cover still used an old user-supplied closed-frame design. During the 0.8-second fade, both title treatments were visible together.
- Confirmed the preview duration was 33.332 seconds at 1080x1920 with MP3 audio. Telegram reservation, send, history, and sync steps were skipped; no video was sent and no Cron was run.
- Updated the opening-cover renderer to use the same first-scene full-bleed background, open gold brackets, title position, and divider as the ayah frame. The existing intro/fade timing and audio timing are preserved. Added a regression test for the new intro composition.
- Changes are on feature/telegram-review-notifications only. CI and a fresh render-only visual review are still pending; do not run Cron or send to Telegram before the sample is checked.


- CI follow-up: the first run after the intro-cover change failed only because the regression test compared a JPEG-resampled background pixel for exact RGB equality; observed rounding was one level per channel (19,45,94 vs. (20,45,95)). Updated the assertion to allow a maximum two-level JPEG rounding tolerance. Renderer tests had otherwise passed. A fresh push-triggered validation/render-only run is pending.


### 2026-11-20 — User rejected current ornament and text spacing; reference match is on hold
- User reported that Arabic/English text appeared crowded/touching and the gold ornament did not match the approved reference. Treat this feedback as authoritative: the current hand-drawn ornament is NOT approved and must not be described as an exact match.
- Applied a narrow spacing correction only: moved the Arabic ayah block and its gold number medallion lower to a dedicated middle zone (center y=990), and moved the English translation to a separate lower zone (center y=1450). Updated the medallion regression probe accordingly. This is a candidate fix pending CI and visual inspection, not yet verified.
- Do not further improvise or redesign the gold ornament. Exact reconstruction requires the original approved reference image to be available to the implementation/review step. Keep the current ornament marked as a placeholder until it can be directly compared and reproduced.
- No Telegram delivery, Cron run, or TikTok publishing. Work remains on feature/telegram-review-notifications only.


## Deferred-ayah continuation implementation — 2026-11-20 (validation pending)

- User approved explicitly deferring Al-Kahf 18:19 and continuing with the next ayah, without cutting or speeding up recitation.
- Added `data/quran_deferred_ayahs.json` with exact reference `18:19`, measured processed duration `66.116s`, hard single-ayah ceiling `60s`, and the reason/status. This reference is not added to confirmed delivery history.
- Updated `src/build_quran_review_batch.py` to accept a separate deferred-reference ledger and exclude deferred ayahs when selecting the first unused contiguous suffix. Delivery history remains separate and unchanged.
- Updated Friday workflow invocation and its first-unused-ayah assertion to honor the deferred ledger; regular selection also receives the ledger. Added the data file to workflow path filters.
- Added regression coverage that a deferred Al-Kahf 18:19 is skipped and candidate selection resumes at 18:20. Existing Friday-selection expectations were updated to the new explicit selection-policy label.
- Relevant commits: builder `33d3a086e3bcfe79b28d2a768ea481adf1f73f27`; test `3b14d5694baae565692770eab615925761afe47a`; workflow `eae10c8161be4df3809a5270a35aa2ecc743700a`; ledger `5b5f2481ac23d7638a40ad583732ad31ae556066`. All on `feature/telegram-review-notifications`; `main` untouched.
- CI runs for the new changes were still in progress at the time of this update: Quran batch tests run `44770357208` (latest test commit) and inventory/render validation run `44770351393` (workflow change). No passing result is claimed yet.
- No Cron run, production Telegram send, delivery-history mutation, or TikTok publishing was triggered. Push-triggered validation is test-only; keep production scheduling untouched.
- Next: wait for the focused test run, inspect its result, then inspect the render-only inventory workflow to confirm it starts Al-Kahf at 18:20 and still respects the duration guard before any production execution.


### 2026-11-20 — Deferred Al-Kahf ayah regression fix verified in CI
- Inspected failed inventory workflow run `44780635541` (checked out older commit `26c83222b9a9f3a005da58d800dc4de3e6f89046`). The immediate blocker was two stale expected `passage_selection` labels in `test_build_quran_review_batch.py`; both expected the old non-deferred label while the implementation returned `first_unused_contiguous_suffix_then_40_second_duration_limit`. The catalog regression step stopped the workflow, so candidate selection, audio preparation, rendering, and Telegram delivery were all skipped. This is why no video arrived; it was not a Telegram delivery failure.
- Corrected both test expectations in commit `c75a0c5e4258bcc6b0c695b141aa22f0f9b68840` on `feature/telegram-review-notifications`. The dedicated Quran batch engine test workflow run `44781033154` on that exact commit completed successfully. Its test job is green.
- Re-inspected the active inventory workflow: push events render and upload review-only previews; Telegram reservation/send steps are gated to scheduled events or explicit workflow-dispatch send options. No production Telegram send was triggered during this investigation.
- The deferred ledger still contains `18:19` (66.116s, hard limit 60s), and the builder excludes deferred references from the first-unused contiguous suffix. The workflow's Friday assertion also excludes deferred references, so the expected next Al-Kahf start is `18:20` when no later delivery-history entry changes that sequence.
- Remaining validation: the inventory/render workflow has not yet been confirmed green on the latest commit, so do not claim a fresh MP4 was rendered or delivered. No Cron run, Telegram send, delivery-history mutation, schedule change, or `main` change was made.


### 2026-11-20 — Moving-background and review-render verification
- Fixed background selection in `src/render_quran_review_previews.py`: suitable moving clips now take priority over still photos; stills remain a fallback only when no moving clip can cover the complete original recitation. Added focused regression tests. Also narrowed the Arabic text layout width to preserve more clearance from the gold ayah medallion. Commits: renderer `22906552de74b79bc8859335f6586f397d4c05be`; tests `f8104ffa095eb2a8d29b02eec6a168cd9f8d9009`.
- Verified all three push-triggered workflows on the active branch completed successfully: inventory/render run `44786163039`; Quran engine validation run `44786158616`; background review run `44786158563`. All job steps completed without failed steps.
- Inventory artifact `quran-visual-review-samples` contains one real 1080x1920 H.264 review-only MP4 for Al-Kahf 18:20, duration 16.98s, with original MP3 audio. The preview report confirms moving-video background `pexels-mosque-waterfront-12536108` (40.725s source), the approved gold open-bracket title ornament and floral divider, cover fade settings (1.2s cover; 0.8s fade from 0.4s), and ayah visible/audio from t=0. The previously deferred 18:19 was skipped as intended.
- Visually inspected an extracted frame and the new-background Quran-overlay contact sheet. The moving-video background is used; the Arabic text and gold number medallion are separated in the inspected frame. Four newly integrated background sources were downloaded, cropped, and rendered as overlay review images; none was activated in production.
- Reference-driven layout preview artifact was also uploaded successfully. The focused engine validation and background review jobs passed.
- All artifacts are review-only: `production_approved=false`, `telegram_delivery=false`, and `auto_publish=false`. No Telegram send, delivery-history mutation, Cron run, or TikTok publishing was triggered. All work remained on `feature/telegram-review-notifications`; `main` was not touched.
- Next: continue visual review of the preview artifact and make any requested adjustments before enabling any production delivery. Do not treat this render as a Telegram-delivered or TikTok-published video.


### 2026-11-21 — Surah-title ornament balance adjustment
- Reduced the two open gold surah-title brackets to 82% of their previous size and reduced the matching horizontal divider to 82%, keeping each ornament centered in its original reference area. The original approved gold artwork, title text, ayah layout, medallion, and background treatment remain unchanged.
- Added a focused regression test for the bracket dimensions/centering and divider size in `tests/test_render_quran_review_previews.py`.
- Verified the final commit `8b48bc213c31fb5da88787faf25690e896750d4e` on `feature/telegram-review-notifications`: Quran batch engine workflow run `44873693600` passed, including visual-template tests and reference-layout rendering; isolated request pipeline run `44873693574` also passed.
- Review-only preview artifact `quran-reference-layout-preview` (artifact `14694777000`) was generated and visually inspected. It is awaiting user approval; this is not a production design approval.
- No Telegram delivery, Cron execution, publishing, delivery-history mutation, or `main` branch change was made.


### 2026-11-21 — Surah-title spacing refinement (validated preview ready)
- On `feature/telegram-review-notifications` only, reduced the extracted open gold brackets and matching floral divider from 82% to 77% of their original crop dimensions (about 6.1% smaller relative to the previous preview).
- Moved the two brackets inward by 10px each to reduce the empty space around the surah title. Kept the original reference pixels, title wording/font/center, ayah text, medallion, and background unchanged.
- Source commit: `aa189e82f0b4880749246bd083b320bbd5a83396`; focused test commit: `675046873209fa9144e0e94e811b841961e5013e`.
- Verified on that exact test commit: Quran batch engine workflow run `44874040016` completed successfully; all compile, visual regression, Quran batch/catalog, renderer, and orchestrator test steps passed. Isolated request pipeline run `44874040033` also passed.
- Fresh reference-driven preview artifact `quran-reference-layout-preview` (artifact `14695096809`) was generated successfully from the updated code. Both the composited ayah preview and intro preview were downloaded and visually inspected.
- This remains a review-only preview. No Telegram delivery, Cron execution, production workflow dispatch, TikTok publishing, or delivery-history mutation was performed. All work stayed on `feature/telegram-review-notifications`; `main` was not touched.
- Next: wait for the user's visual approval before making any further design change or treating this layout as production-approved.


## Background rotation and ayah-transition synchronization fix (2026-11-21)

- Updated `src/render_quran_review_previews.py` on `feature/telegram-review-notifications` only.
- Background selection now rotates the full approved mixed photo/video catalog in its supplied catalog order; it no longer silently prefers moving videos only or sorts the remaining video pool by duration.
- Every ayah-level selection now excludes background IDs present in the persistent recent-delivery history as well as assets already used earlier in the same video. If the recent-history window covers the entire eligible pool, the selector safely relaxes historical avoidance while preserving within-video uniqueness.
- Approved still photos and moving clips both participate in rotation. A moving clip is eligible only when its verified duration covers the complete ayah; a still photo can cover any complete ayah.
- Removed the scene crossfade that blended the outgoing and incoming ayah text and caused the next text to appear before its matching recitation. Scene video is now concatenated with hard cuts at the exact per-ayah segment boundaries; the original MP3 ayah files are concatenated and stream-copied without audio re-encoding. This intentionally prioritizes exact text/audio synchronization over a visual crossfade.
- Added regression coverage for mixed photo/video rotation, recent-ID avoidance, catalog-order preservation, and hard-cut scene assembly with original audio stream copy.
- No Cron configuration, Telegram send, workflow dispatch, TikTok publishing, credentials, or `main` branch changes were made by this code edit. CI validation is pending; do not treat the fixes as production-verified until the push-triggered test/render workflow completes successfully.

- First push-triggered CI exposed two test-fixture issues in the new rotation path: the mocked ffprobe response omitted a valid duration for a newly eligible catalog item, and the concat-list fixture used a literal escaped newline. Corrected the fixture to provide verified media duration, isolated the renderer test from the repository's persistent production history, and corrected concat-list newline encoding. The first CI attempt is recorded as failed; rerun validation is required before declaring the change verified.

- Corrected the concat manifest writer to emit real line breaks between FFmpeg concat entries; the prior version emitted literal backslash-n characters, which the regression test caught. Re-run CI is pending.


## Duration policy refinement — 2026-11-21 (CI validation pending)

- User approved changing the active Quran video duration behavior while keeping the existing 45-second normal target and 60-second hard ceiling.
- Updated `src/quran_audio_parts.py`: parts are filled toward 45 seconds; when the next complete contiguous ayah would cross 45 seconds but the combined duration remains at or below 60 seconds, that complete ayah is included and the part is closed immediately. No further ayah is added to that extended part. A single ayah between 45 and 60 seconds remains a standalone complete part. Any ayah or combination exceeding 60 seconds is not included in that part; no ayah is cut or sped up.
- Updated `src/quran_delivery_attempt.py` so the reservation/send safety gate accepts any complete-ayah part up to 60 seconds, regardless of whether it contains one or multiple ayahs. The audio partitioner remains responsible for the 45-second target and one-ayah extension rule.
- Added regression tests for the two observed examples: 26.2 + 22.465 = 48.665 seconds, and 43.4 + 11.729 = 55.129 seconds. Added tests for refusing a combined part above 60 seconds and preserving a standalone 46.733-second ayah. Updated reservation tests to accept multi-ayah previews up to 60 seconds and reject 60.001 seconds.
- Code/test commits on `feature/telegram-review-notifications`: `e8beab6639428928365fb646c957b157a1ad6c89`, `63ea2eda25192e33b8b7bbd809fe01c877431568`, `d8f463d370777383a7d07f81ae053bf9aad4c1ef`, `a9620da5e73f91c28c9739457c25691785d0cdf5`, `5e25e1026ab27ebb6848385e19e8697242323544`.
- No Telegram send, Cron run, manual workflow dispatch, TikTok publishing, schedule/credential change, or `main` branch modification was performed. CI validation is pending; do not treat the change as verified until the relevant push-triggered checks pass.


## Duration policy renderer guard completion — 2026-11-21 (verified)

- Completed the renderer-side duration checks for the approved policy: the 45-second target with at most one additional complete contiguous ayah extending a part to a hard maximum of 60 seconds. Both the initial selected-ayah validation and final rendered-MP4 duration guard now permit validated complete-ayah parts up to 60 seconds; the audio partitioner remains responsible for the 45-second target and single-next-ayah extension rule.
- Added/updated regression coverage for a multi-ayah part at 49.737 seconds, and repaired the final-output guard that had still rejected multi-ayah parts above 45 seconds.
- Latest renderer-fix commits: `c78daf930093f777720633d277d342baa6aca7f8`, `8aa7e444a7baa44319fd4dd7ff9f5ad0b65f1aa6`, `c42d3d69aad686eae3cce31559d0ef6a6081a0c6`, `51813e6b01fddfe648992f53f198907c591a7c3d`, `6ec43f2422cdb150177fb4060acabea893c9c070`.
- Push-triggered validation at final code commit `6ec43f2422cdb150177fb4060acabea893c9c070` passed: Quran batch engine tests run `44951564144`, isolated Quran request pipeline run `44951564208`, staged-background review run `44951564173`, and Quran-wide official verse audio inventory/render run `44951564467`.
- These are code/test and render-validation checks only. No Telegram send, Cron execution, manual production workflow dispatch, TikTok publishing, schedule/credential change, or `main` branch modification was performed. All changes remain on `feature/telegram-review-notifications`.



## Smooth zoom jitter correction — 2026-11-21

- User reported a slight visible shake during the background zoom in the latest Cron-delivered video and explicitly asked to remove the shake while preserving the zoom.
- Root cause targeted: the existing FFmpeg `zoompan` calculated centered crop positions at the final 1080x1920 working resolution, where integer crop-coordinate stepping can appear as micro-jitter during smooth zoom.
- Updated `photo_motion_filter()` to preserve the exact existing centered zoom curve (`1.15-0.15*cos(2*PI*on/360)`, same 12-second cycle, same 0–30% zoom range, same 30 fps) but render the zoom/pan at 2160x3840 (2x supersampling) and downsample to 1080x1920 with Lanczos. The zoom is retained; only sampling precision is improved.
- Added a regression assertion that verifies the 2x zoom render and Lanczos downsample while retaining the existing zoom curve and centered pan.
- Code commit: `912e40a92b74c8264694831918e77384c9060022`; focused test commit: `769067aadb2d84220241091bd6e0d8a8cf9ba268`.
- Changes are on `feature/telegram-review-notifications` only. No Cron settings, schedule, Telegram credentials, delivery history, bot, or TikTok publishing behavior was intentionally changed. `main` was not touched.
- Validation is pending. Do not claim the jitter is fixed in a delivered video until the relevant tests pass and a new video is visually checked by the user. The next scheduled/Cron delivery should be used to evaluate the motion; do not trigger an extra production send without the user's explicit approval.


## Basmala separation investigation — 2026-11-22

- User approved the target behavior: show the Basmala on its own first, then show the first ayah when its recitation begins; Arabic/English text and the original Maher Al-Muaiqly Hafs recitation must remain synchronized.
- Inspected the active branch `feature/telegram-review-notifications` at HEAD `8a8574d7e0e72dd5098a8fbb4224d5301b58369f`. `main` was not touched.
- Identified the exact recent Cron-triggered workflow run `44956955912`: it rendered Surah Al-Qadr (97), ayahs 1–5; first ayah scene duration was 6.74 seconds and final MP4 duration was 38.234 seconds. Telegram confirmed the delivery. This is the run corresponding to the user's latest approved video.
- The Arabic catalog builder currently removes the Basmala prefix only when it exactly matches one hard-coded Uthmani string followed by a regular space, and only when the surah is not Al-Fatihah or At-Tawbah. The existing unit test uses that exact same synthetic string, so it does not cover alternate Unicode/diacritic/spacing forms that may occur in the fetched Arabic source. This is a plausible text-layer failure mode, but the exact text emitted in the delivered MP4 has not yet been recovered; do not state this as the confirmed root cause.
- The renderer displays the selected first-ayah Arabic text from the catalog from time zero. The audio preparation stage preserves each complete official ayah MP3 and only trims detected edge silence; it has no Basmala/ayah word-boundary timing. The renderer's 6.74-second first scene duration is not a verified Basmala boundary.
- Do not split the official MP3 at a guessed timestamp, add a fixed-duration Basmala card, or substitute another recording. Before implementation, verify whether the exact KFGQPC per-ayah recording contains the Basmala and obtain timing that is demonstrably valid for that same recording (or another explicitly approved, source-verified approach). Then add regression tests for the separate Basmala scene and exact audio/text boundary.
- No source code, Arabic text, audio, visual design, zoom, background, duration policy, scheduler, Telegram configuration, or delivery history was changed during this investigation. No new Telegram send or Cron run was triggered. The current user-approved video remains intact.


## Basmala source/timing follow-up — 2026-11-22

- Investigated a possible alternate Maher Al-Muaiqly Hafs verse-by-verse archive (Maqra/everyayah mirror). Its dataset documentation confirms standalone Basmala/isti'adhah files may exist, but explicitly records the recitation license as UNKNOWN and says the mirror has no rights to grant; do not introduce this audio into the production pipeline without permission/source approval. It is also not yet proven to be the same recording as the existing King Fahd Complex audio.
- Investigated Tarteel QUL's Maher Al-Mu'aiqly Hafs ayah-by-ayah resource. Its documentation describes per-word timestamps, but no evidence yet establishes that its audio is byte-identical or otherwise the same recording as the current KFGQPC archive. Its timing data must not be applied to the current KFGQPC audio unless an exact recording match is independently verified.
- A separate full-surah stream page for Surah Al-Qadr explicitly says verse timestamps are not published, so it cannot supply a reliable Basmala boundary for the delivered recording.
- Current conclusion: no alternate recording or timing source has been approved. Keep the existing KFGQPC MP3 and current rendering unchanged. Do not splice a standalone Basmala from an unverified recording or infer a timestamp. Continue seeking a boundary tied to the exact existing audio or a permission-cleared, user-approved matched source.
- No code, production audio, renderer, schedule, Telegram settings, delivery history, or visual design changed. No Telegram delivery or Cron test was triggered.


## Final user decision: keep current Basmala presentation unchanged — 2026-11-22

- User explicitly decided to leave the current Basmala/first-ayah presentation as it is because a reliable separation that preserves exact audio/text synchronization has not been established.
- Treat Basmala separation as deferred indefinitely. Do not continue investigating, implement a guessed timestamp, change Quran text/audio sources, or alter the first-ayah presentation unless the user explicitly reopens this request.
- Preserve the currently approved video quality, design, zoom/motion, backgrounds, audio, duration policy, scheduler, Telegram bot/configuration, and manual TikTok review/publishing flow.
- This is a documentation-only record of the user's final decision. No source code, media, workflow, Cron schedule, credentials, delivery history, or Telegram settings are changed. No test workflow, Cron run, Telegram send, or TikTok publishing is triggered. Work remains on `feature/telegram-review-notifications`; do not touch `main`.


## External daily scheduler — cron-job.org — 2026-11-22

- The daily Quran video workflow is triggered by the user's existing external cron-job.org job; the user confirms that the daily sending is working reliably. Do not replace it with a GitHub schedule, Cloudflare Worker, second cron job, or another bot.
- Job name: `Quran Video Scheduler`.
- Last previously recorded account check: 2026-11-02, when the job was confirmed enabled/active.
- Configured timezone: `Africa/Tunis`.
- Configured run times: `04:10`, `12:10`, and `18:10` local Tunisia time.
- Previously checked request configuration: HTTP `POST`; timeout `30 seconds`; request targets the GitHub Actions workflow using branch/ref `feature/telegram-review-notifications`.
- Important verification boundary: the prior check did not establish the exact request URL or verify the authorization/header values. Do not copy or reconstruct credentials, tokens, or endpoint details from assumptions. The current conversation confirms successful daily operation, but no live cron-job.org account inspection was performed during this documentation update.
- Operational rule: preserve the existing external job and its settings. Do not trigger a test, manually dispatch the production workflow, or send an extra Telegram video unless the user explicitly asks.
- This entry records previously checked settings and the user's current confirmation of reliable operation. Documentation only; no cron configuration, workflow, code, credentials, Telegram settings, or delivery history changed. No Cron run or Telegram send was triggered. Work remains on `feature/telegram-review-notifications`; do not touch `main`.


## Background library expansion — two candidates staged (2026-11-23)

- User approved adding two new Pexels video candidates to the background library.
- Added metadata to `data/background_candidates.json` on `feature/telegram-review-notifications` only:
  - `pexels-mosque-architecture-28899957`: Pexels page confirms Free, 1080x1920, 9:16, 26 seconds.
  - `pexels-ancient-mosque-architecture-36628576`: Pexels page confirms Free, 2160x3840, 9:16, 11 seconds.
- Their Pexels pages and direct MP4 URLs were identified, but the MP4 files could not be downloaded in this session, so `download_verified=false` is deliberately retained for both. They therefore remain ineligible for the production background rotation under the existing verified-download gate.
- A third previously suggested candidate (video ID 30963441) could not be verified as a matching Pexels page and was not added.
- No renderer, selection logic, active background catalog, workflow, scheduler, Telegram settings, credentials, or delivery history was changed. No workflow activation, Cron run, Telegram send, or TikTok publishing was triggered. `main` was not touched.
- Next safe step: verify/download the two MP4 files and run ffprobe checks, then prepare overlay previews for user review before any production activation.


## Two approved Pexels backgrounds — media verification and review previews (2026-11-23)

- Supersedes the earlier note that the two new MP4 files were still awaiting download. Both files were successfully resolved from their official Pexels download pages, downloaded in an isolated review-only GitHub Actions run, and passed ffprobe.
- Review-only workflow: `.github/workflows/verify-two-approved-backgrounds.yml`, commit `e2c17bccc2c95b99aaab7479aefa3fd8b6117c38`; run `45147837063` completed successfully. It processes only the two explicitly approved IDs, uses a temporary manifest with direct URLs blanked so the official Pexels download redirect is resolved, and uploads previews/source MP4s as artifact `two-approved-pexels-backgrounds-review` (artifact ID `14805381033`).
- Verified media:
  - `pexels-mosque-architecture-28899957`: H.264, 1080x1920, 26.067 seconds, 42,182,162 bytes.
  - `pexels-ancient-mosque-architecture-36628576`: H.264, 2160x3840, 11.967 seconds, 32,633,757 bytes.
- The workflow generated center-cropped 9:16 images and composited the current Quran overlay for visual review. The first background's Arabic/English text is legible in the still preview. The second background has a bright sky behind the surah title area; check its legibility against the moving clip before production use. These are still-frame checks, not a complete motion review.
- Both entries deliberately retain `download_verified=false` in the production candidate manifest for now. Although the media files passed technical verification, the overlay/legibility review has not been approved; therefore neither candidate is eligible for the existing production rotation. Do not set the flag true until the user confirms the preview.
- A separate pre-existing candidate test suite failed in run `45147249697` because it hard-coded 15 total entries and required every entry to be download-verified. That expectation became stale when two intentionally pending entries were added. Updated `tests/test_background_candidates.py` to assert 17 total entries, 15 technically verified existing entries, and exactly these two staged entries excluded from rotation. Validation after this test correction is pending.
- No production renderer, active rotation settings, background history, scheduler, Telegram configuration, credentials, delivery history, or TikTok publishing behavior was changed. No Telegram send, Cron execution, or production workflow dispatch occurred. All changes remain on `feature/telegram-review-notifications`; `main` was not touched.
- Next: obtain the user's visual/legibility approval for these two previewed backgrounds. Keep both staged and inactive until that approval; then separately decide whether to enable them in the existing rotation.


## Two new Quran backgrounds visually approved and enabled for rotation — 2026-11-23

- User explicitly approved both actual Quran-overlay review previews, including the bright-sky mosque clip.
- Both source MP4s had already passed isolated download and ffprobe verification in review run `45147837063`: `pexels-mosque-architecture-28899957` (1080x1920, 26.067s) and `pexels-ancient-mosque-architecture-36628576` (2160x3840, 11.967s).
- Updated only these two entries in `data/background_candidates.json` to `download_verified=true`, preserving their existing approval flags, direct Pexels source URLs, and metadata.
- Restricted the background review/activation workflow to exactly these two user-approved IDs. It re-downloads/probes them, renders the real Quran overlay, validates 9:16 media and approval, then makes only these two eligible in the existing background rotation. It does not send Telegram, invoke Cron, publish to TikTok, or alter renderer/zoom/audio/scheduling configuration.
- Updated background candidate tests to reflect 17 total verified candidates and explicitly assert the two new IDs are eligible. Updated the staged-additions count assertion from 15 to 17.
- All changes remain on `feature/telegram-review-notifications`; `main` is untouched. Await the exact-commit CI result before claiming the workflow activation is complete.


## Shared background library loader — isolated implementation — 2026-11-23

- Added `src/background_library.py` with a single typed intake function that combines the existing strict video eligibility loader and the previously approved/locally verified photo loader.
- The normalized records carry an explicit `media_type` (`photo` or `video`), common `asset_id` / `source_url` fields, and media-appropriate `asset_url` / `asset_path` fields. Duplicate IDs across the two catalogs fail closed.
- Added `tests/test_background_library.py` for combining only eligible assets, retaining the media type and source fields, excluding pending/missing assets, and rejecting cross-catalog ID collisions.
- This is an isolated management/intake layer only. It does not change either catalog, photo/video renderer, production selection, render workflow defaults, daily schedule, Telegram, credentials, Cron, or TikTok publishing. No production render or Telegram send was triggered.
- Next validation: run the new tests together with existing background rotation tests. Only after that passes, consider a separate review-only adapter integration; production renderer activation remains deferred pending a user-reviewed preview.


## Shared background library validation — 2026-11-23

- Added a dedicated, read-only CI workflow at `.github/workflows/test-background-library.yml`. It runs only the shared library tests, existing video background rotation tests, and Python compilation; it does not render or send videos, modify catalogs, or touch Telegram/Cron/TikTok.
- The first combined review-workflow run exposed a test-fixture issue: the duplicate-ID photo fixture omitted its required source-page metadata, so normalization raised `KeyError` before the duplicate-ID assertion. The production loader was not the cause.
- Corrected the duplicate-ID test fixture by supplying the same source-page and image URL metadata used by valid photo records. No production source code was changed for this test failure.
- Dedicated CI run `45153955127` on commit `1b8c60e3ad80a46c766b558e088634645b6a4c00` completed successfully: shared photo/video library tests passed, all existing background-rotation tests passed, and both isolated modules compiled successfully.
- The parallel review workflow run `45153955164` was still in progress at the time of this update. Its outcome must be checked separately before treating its preview/activation sequence as complete.
- All work remains on `feature/telegram-review-notifications`; `main` is untouched. Production renderer behavior, schedule, credentials, Telegram delivery, Cron, audio, zoom, and TikTok publishing remain unchanged.
- Next: verify the parallel review workflow result; then build a separate review-only adapter/preview using the shared library, keeping photo and video renderers distinct. Do not activate photos in scheduled production without a user-reviewed preview and explicit approval.


## Isolated background review workflow — successful preview validation — 2026-11-23

- Review workflow run `45153955164` completed successfully on commit `1b8c60e3ad80a46c766b558e088634645b6a4c00`. Existing catalog/preview safeguards passed, the genuine Quran overlay frame rendered, both explicitly approved mosque clips downloaded and passed ffprobe, and the review images/artifact were published.
- Artifact `quran-islamic-background-review` (ID `14806933752`) contains the two verified MP4 sources, center-cropped 9:16 stills, Quran-overlay composites, contact sheets, the overlay PNG, and `background_review_report.json`.
- Report confirms both clips are H.264 portrait media (1080x1920 / 26.067s and 2160x3840 / 11.967s), with no unresolved downloads. It explicitly records `production_enabled: false` and `overlay_legibility_review_required: true`; these are review assets, not permission to change scheduled production.
- The separate shared-library CI run `45153955127` also passed all shared-library tests, all 9 existing background-rotation tests, and module compilation.
- Next implementation remains review-only: connect the common typed library to a separate preview adapter while keeping photo and video rendering paths distinct. No scheduled renderer, production defaults, daily schedule, Telegram, credentials, Cron, audio, zoom, or TikTok publishing changes.


## Review-only adapter for the shared photo/video background library — 2026-11-23

- Added `src/background_review_adapter.py`: it loads the common verified inventory, keeps video and photo records in separate groups, and creates a center-cropped 9:16 contact sheet for all approved photos with the actual transparent Quran overlay. The output explicitly remains review-only and marks overlay legibility review as required.
- The existing video preview pipeline remains the video-specific adapter; the new photo contact-sheet adapter does not replace or modify it. No scheduled production renderer or media-selection logic is imported or changed.
- Added `tests/test_background_review_adapter.py` for typed inventory grouping, photo crop/overlay contact sheet creation, and fail-closed behavior for an empty photo inventory.
- First adapter CI run exposed a test-fixture issue: the synthetic solid-color JPEG was smaller than the photo loader's existing 50 KB verification threshold. Replaced it with a deterministic noise image so the fixture represents a valid locally verified photo; no production validation threshold was changed.
- Dedicated CI run `45154506664` on commit `2a9ff1ed4675e38e85a28a14ce1bcfbe43183489` passed: 2 shared-library tests, 3 review-adapter tests, 9 existing background-rotation tests, and Python compilation.
- Updated the review workflow to generate the unified inventory and photo Quran-overlay contact sheet, include photo catalog/assets in its path filters, and run the new adapter tests. The parallel review workflow run `45154506678` was still in progress at the time of this update; verify it before claiming the photo contact sheet artifact is ready.
- The dedicated test workflow now also runs the new review-adapter tests. All changes remain on `feature/telegram-review-notifications`; `main` is untouched. Production rendering, schedule, Telegram, credentials, Cron, audio, zoom, and TikTok publishing remain unchanged.


## Review artifact publishing race fix — 2026-11-23

- In review run `45154506678`, all tests, the unified 35-photo contact sheet, and the two video overlay previews completed successfully. The only failed step was the final Git push: the branch advanced concurrently when the status log was committed, so the workflow's generated-image commit was rejected as non-fast-forward. No source changes were lost and no production action occurred.
- Removed generated preview commits/pushes from the review workflow. Review images and verified source clips are now retained as workflow artifacts only; artifact upload uses `if: always()` so it still runs if a later optional step fails. This avoids branch races and unnecessary generated-image commits.
- Replacement review run `45154716270` was triggered on commit `def1058053f78717a365f66188c23a55cce6224a`; at the time of this status entry it was still running the environment-install step. Its final status and artifact availability remain to be verified.
- Production rendering, background selection defaults, daily schedule, Telegram, credentials, Cron, audio, zoom, and TikTok publishing remain unchanged. All work stays on `feature/telegram-review-notifications`; `main` is untouched.


## Unified photo/video review preview — completed — 2026-11-23

- Replacement review workflow run `45154716270` completed successfully on commit `def1058053f78717a365f66188c23a55cce6224a`. The full sequence passed: catalog/preview safeguards, Quran overlay render, unified inventory, photo contact sheet, both approved video downloads/probes/overlay previews, and artifact upload.
- Final artifact: `quran-islamic-background-review`, artifact ID `14807444011`, approximately 80.5 MB. It includes `photo_backgrounds_quran_overlay_contact_sheet.jpg`, video overlay/contact sheets, both verified MP4 source clips, crops, overlay PNG, and both review JSON reports. Artifact retention is until 2026-11-26.
- Unified inventory report confirms 35 previously approved local photos and 13 eligible approved portrait video backgrounds. The 35-photo sheet uses center-cropped 9:16 thumbnails with the real transparent Quran overlay.
- Both reports preserve the review boundary: photo overlay report has `production_enabled: false` and `overlay_legibility_review_required: true`; the video report likewise has production disabled and overlay legibility review required. Existing user approval of the photo/video assets is preserved; this preview does not create new approval for any future asset or automatically authorize production photo rendering.
- The final workflow no longer pushes generated previews to the source branch. They are stored as workflow artifacts to avoid non-fast-forward races and unnecessary generated-image commits.
- Next: user visual review of the contact sheets, especially text legibility on bright/dark photo backgrounds. Do not enable photo backgrounds in scheduled production until this preview is reviewed and the user explicitly approves the production behavior. All production renderer settings, daily schedule, Telegram, credentials, Cron, audio, zoom, and TikTok publishing remain unchanged.


## User-approved mixed photo/video backgrounds integrated — 2026-11-23

- User explicitly approved integrating the previously reviewed 35 photos together with the approved video backgrounds in the daily Quran background rotation.
- Added `src/background_mixed_renderer.py`: deterministically selects one approved asset per verse scene, prefers alternating photo/video media types where possible, avoids recent IDs when alternatives exist, renders photos with the existing gentle centered zoom and videos with their original motion, normalizes every scene to 1080x1920/30fps, then crossfades scene boundaries.
- Updated `src/render_video_scenes.py`: when the existing `--use-photo-backgrounds` option is enabled, it now loads the shared fail-closed photo/video library and uses the mixed renderer. This makes the existing `render-manifest-video.yml` workflow's current default (`use_photo_backgrounds: true`) use both media types. When the option is false, the existing video-only background path remains unchanged.
- Photo eligibility is enforced through the shared loader: manifest-level recorded user approval plus local image decode and dimension/size checks. Video eligibility retains explicit approval, user approval, verified download, portrait aspect ratio, HTTPS URLs, and unique IDs. The mixed renderer also verifies downloaded video files with ffprobe and validates each normalized output segment.
- Added `tests/test_background_mixed_renderer.py`: deterministic/alternating selection, fail-closed empty/duplicate inventory, and an FFmpeg integration test that renders one synthetic photo scene and one synthetic portrait-video scene into a 1080x1920 reel.
- Dedicated CI run `45155633254` completed successfully: shared library tests, review adapter tests, mixed FFmpeg renderer integration tests, existing video rotation tests, and Python compilation all passed.
- Review workflow run `45155645483` completed successfully after adding the mixed-renderer tests to its test gate; its real-asset contact-sheet/overlay preview pipeline also passed.
- Broader Quran batch engine regression run `45155582965` was still in progress at the time of this entry; check its final status before claiming the full engine suite passed.
- No production workflow was manually dispatched, no Cron job was run, and no Telegram video was sent during this change. The existing render workflow input default is already `use_photo_backgrounds: true`, so future normal dispatches of that workflow will select from the unified library. The user's external Cron schedule, Telegram bot/configuration, credentials, audio, approved overlay design, zoom parameters, TikTok manual publishing, and all unrelated production settings remain unchanged.
- All code and documentation changes remain on `feature/telegram-review-notifications`; `main` is untouched.


## Full Quran engine regression completed after mixed-background integration — 2026-11-23

- Broader Quran batch engine regression run `45155582965` completed successfully. All steps passed: module compilation, Quran catalog/batch/visual-template tests, a reference-driven Quran layout render and preview artifact upload (no delivery), Quran-only daily orchestrator tests, and the test-only safety check.
- This supplements the dedicated mixed-background CI run `45155633254` and successful review workflow run `45155645483`. No production render, Cron execution, Telegram send, or TikTok publishing was triggered by these checks.
- The mixed photo/video renderer is integrated on `feature/telegram-review-notifications`; the existing `render-manifest-video.yml` option default enables the unified library. First naturally scheduled delivery should be monitored for correct media rotation and output quality. Do not manually trigger an extra production video just to test it.


## Six new Pexels photo candidates staged for isolated review — 2026-11-27

- Added `data/background_photos_pending_review.json` with six new Pexels photo candidates: two mosque exterior/minaret scenes, one mosque at dusk, one mosque interior, and two waterfall/forest scenes. Source pages and image URLs are retained per candidate.
- All six are explicitly marked `pending` / `user_approved: false`. They are not in the production photo manifest, are not eligible for the daily renderer, and do not alter the 35 previously approved photos or the 13 approved portrait videos.
- Added `src/prepare_pending_photo_background_review.py` and the isolated workflow `.github/workflows/review-pending-photo-backgrounds.yml`. The workflow downloads each image only into a temporary runner, validates it, creates compact 540x960 previews with the real approved Quran overlay, and uploads a seven-day review artifact. Source images are not committed to Git, preserving repository storage.
- Dedicated review workflow run `45976828780` completed successfully. All six images downloaded, passed image validation, were resized into temporary previews, and received the real Quran overlay; zero candidates failed. Artifact `quran-pending-photo-background-review` (ID `15187801018`, about 1.9 MB) contains the contact sheet, six individual previews, and a valid JSON report. The artifact expires after seven days.
- No production workflow, Cron job, Telegram delivery, existing background catalog, production manifest, or main branch was changed. New photos must remain excluded from production until the user visually reviews and explicitly approves them.


## Six additional Quran photo backgrounds approved and imported — 2026-11-27

- User explicitly approved all six previewed candidates after reviewing the Quran-overlay contact sheet.
- Added the six photos to `data/background_photos_manifest.json`; the production photo inventory now records 41 approved photo IDs (the original 35 plus these six).
- Strengthened photo approval safety: production eligibility now requires membership in the explicit `approved_photo_ids` allowlist. A local image file or a manifest-level approval note alone cannot approve a new photo. Updated rotation, shared-library, and review-adapter test fixtures to use the explicit allowlist and verify unapproved files are excluded.
- Downloaded all six approved images in GitHub Actions, validated them, resized them to fit within 1080x1920 while preserving aspect ratio, and saved optimized JPEGs under `assets/background_photos/`. The six new files total 2,370,468 bytes (~2.26 MiB); no original large video files were added.
- Import workflow run `45977421605` completed successfully: download/optimization, photo-approval tests, shared-library tests, mixed photo/video renderer integration test, and commit of the compact image assets all passed.
- All work remains on `feature/telegram-review-notifications`; the 13 approved portrait videos are unchanged. No production render, Cron run, Telegram send, or TikTok publish was triggered.
- Follow-up full shared-library CI run `45977554283` completed successfully. Shared photo/video library tests, review-adapter tests, mixed photo/video FFmpeg integration tests, existing video rotation tests, and module compilation all passed.


## Duration policy correction — contiguous whole-ayah packing to 60 seconds — 2026-11-27

- User clarified the final rule: 45 seconds is the preferred target, not a stopping threshold. Continue adding the next complete contiguous ayah(s) whenever the full combined sequence remains at or below the 60-second hard cap. This applies to one or multiple long ayahs; never split, skip, reorder, or speed up an ayah.
- Corrected src/quran_audio_parts.py to pack contiguous whole ayahs until the next one would exceed 60 seconds. Corrected audio preparation metadata and final audio validation to apply the same 60-second hard cap to single- and multi-ayah parts. The review renderer already had a 60-second MP4 guard; its policy comments are now aligned. The legacy renderer and its tests were also aligned from the obsolete 40-second guard to 60 seconds.
- Updated the duration specification, scheduled failure notification, deferred-ledger description, and regression tests. Added an integration regression where the sequence passes 45 seconds and then includes another complete ayah because the total remains 56 seconds.
- Al-Kahf duration facts verified from the existing status history: 18:19 is 66.116 seconds and remains deferred intact; 18:20 is 16.98 seconds after edge-silence handling; 18:21 is 56.111 seconds, so 18:20 + 18:21 exceeds 60 seconds and cannot be combined. The 46.733-second figure belongs to Al-Kahf 18:17, not 18:20.
- Scope: samiouess-ux/IslamicTikTokAutomation, branch feature/telegram-review-notifications only. main, external Cron schedule, Telegram credentials/bot, production delivery settings, approved design, backgrounds, and manual-only TikTok publishing are unchanged. No production workflow dispatch, Cron run, Telegram send, or TikTok publication was initiated.
- Validation: push-triggered Quran engine test run #313 (45979770351), on corrected test commit a55c2e8bbdfd8f6d24a65a6dc5496c69bc12d390, passed all 122 tests, including the new multi-ayah-after-45s integration test and the 60-second renderer/delivery guards. The separate push-triggered full inventory workflow run #666 (45979692904) completed successfully. Its review-only Al-Kahf preview selected complete ayah 18:21 and measured 56.000 seconds (1080x1920, H.264 + original MP3). The artifact report explicitly keeps production approval, Telegram delivery, and auto-publishing disabled. Telegram reservation/send/history steps were skipped because this was a push event; no Cron run or production delivery occurred.


## Automatic on-screen segmentation for long Quran ayahs — 2026-11-27

- User approved a narrowly scoped visual improvement: long ayahs may appear in successive text screens so they are not crowded into one dense block. All other visual and production behavior must remain unchanged.
- Updated the scheduled review renderer `src/render_quran_review_previews.py`, which is the renderer invoked by the existing Quran inventory workflow. Short ayahs retain one unchanged display frame. Dense long ayahs are divided into complete sequential Arabic display phrases; existing Quran pause marks are preferred as break points. The complete ayah remains intact in the source and audio, and no word is removed, reordered, or repeated.
- The Saheeh International translation is divided into corresponding successive display portions. Since the source audio inventory provides ayah-level timing rather than word-level timestamps, each display portion is timed proportionally to its Arabic word count; this is approximate phrase-level synchronization, not claimed word-perfect synchronization.
- Each display frame reuses the existing approved overlay renderer, including the same transparent full-bleed treatment, white Arabic text, gold ayah medallion, and translation styling. Background selection/motion, opening title, original MP3 audio stream copy, ayah order, transitions, duration policy, Telegram gates, and manual TikTok publishing are not intentionally changed.
- Added regression tests for complete Arabic/English text preservation across display chunks and for short ayahs remaining a single display. Updated the review-render filter assertions for timed overlay frames.
- Commits: renderer implementation `32d6083f2d8038f1cd01eafb6813784de4966893`; safe fallback `57b7104ab22e6575f47afde8202a43c2e38d6cab`; regression tests `1284ba0b597de4d9161b4b5cee53569a86545ef6`.
- Validation is pending; do not treat this feature as production-verified until the push-triggered test/review workflow completes and its rendered preview is inspected. No manual production dispatch, Cron run, Telegram send, or TikTok publication was initiated. All changes are on `feature/telegram-review-notifications`; `main` remains untouched.


- Follow-up code review found and fixed a missing `math` import required by the new finite-duration guard. The chunk planner now also treats a layout-fit failure as a reason to attempt phrase segmentation rather than failing before segmentation. Fix commit: `2b0a333c6ebcb9599bb76e07c3cc3923c8d01aec`.
- The existing push-triggered review workflow explicitly includes both the renderer and its test file in its path filters. GitHub combined commit status currently exposes no status contexts for the latest commit; therefore automated validation and rendered-preview inspection are still unconfirmed. Do not enable production use until the workflow result and preview are inspected.
