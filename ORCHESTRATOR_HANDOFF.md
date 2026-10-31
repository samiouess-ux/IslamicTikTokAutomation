# Orchestrator handoff — Islamic video engine

Active repository: `samiouess-ux/IslamicTikTokAutomation`
Active branch: `feature/telegram-review-notifications`
Do not modify `main`.

## User's required outcome
Build a reliable engine that prepares three varied Islamic vertical videos per day, each as a separate 9:16 MP4 with a ready-to-use caption, then delivers the files to the user's Telegram. The user downloads them and publishes manually on TikTok. TikTok auto-publishing is forbidden and must remain disabled.

Quran content must use exact Arabic text and verified translation, authentic user-reviewed recitation, no music, and recorded provenance/rights. Duas/dhikr must be exact, sourced, and checked. Never invent sacred wording. Do not display the reciter's name publicly. Vary calm backgrounds/layouts without immediate repeats. Simplicity and no upfront paid services are preferred.

## Read before every task
Read `PROJECT_STATUS.md`, `DESIGN_SPEC.md`, this file, the active workflow(s), and relevant tests before editing. Inspect actual branch state and recent Actions runs. Make small commits, run tests, and update both status documents after meaningful work. Never claim a test, delivery, or approval without evidence.

## Confirmed current engineering state
- The user-approved visual design is the ornate gold surah cartouche, separate gold verse medallions, unchanged white Quran Arabic, and smaller English translation.
- `src/render_video_scenes.py` renders a Quran manifest as a scene-based MP4 and writes a sibling `.caption.json`.
- `src/content_rotation.py` and `src/asset_rotation.py` implement deterministic selection with recent-repeat protection, but only already reviewed/approved manifests/assets are eligible.
- `src/validate_content_manifest.py` has strict gates. The current scene renderer explicitly rejects non-Quran content; do not claim dua/dhikr rendering is ready.
- `src/send_telegram.py` sends an MP4 to Telegram using `TG_BOT_TOKEN` and `TELEGRAM_CHAT_ID` environment variables. It refuses missing credentials, empty/missing MP4s, files above 50 MiB, and captions above Telegram's 1024-character limit. It has no TikTok publishing function.
- `tests/test_send_telegram.py` covers bilingual review caption, caption limit, missing secrets, >50 MiB rejection, and a mocked successful API response/request body.
- `.github/workflows/render-manifest-video.yml` has a manual `send_to_telegram` boolean input (default true for manual dispatch) and invokes the sender after render validation/artifact upload. On push events, the input is absent and the Telegram step should be skipped.
- The dedicated Ash-Sharh 94:1–8 workflow `.github/workflows/render-second-ash-sharh-review.yml` still has its Telegram step disabled with `if: false`. Do not treat its successful render as Telegram delivery.
- TikTok publishing remains disabled/manual.

## Recent implementation commits
- `dc10611606f780ccff8859d6248aeafcad93793c` — add Telegram sender.
- `769022e817cc68fe6624e019a0b2ed02e5eca00a` — initial sender safeguards tests.
- `3061a31a39177f69cd4482d4f68acbb2f94c6d9c` — add manual workflow dispatch Telegram option.
- `25f0f753d18634de298463d32245dda650a5fa` — update project status checkpoint.
- `177be619d997da42ca353ecb943e08296d383136` — test successful mocked Telegram upload.

## Evidence and outstanding checks
- Run `41235405617` succeeded and produced artifact `ash-sharh-94-1-8-video-review`, artifact ID `13055730388`, size 34,101,084 bytes. Its Telegram step was skipped (explicit `if: false`).
- Run `41235407692` completed successfully: all render/validation/artifact steps passed and produced `islamic-video-review` artifact `13055525766` (48,363,815 bytes). Telegram step was skipped as expected for a push-triggered run. Run `41235405611` remained in progress at last check.
- Latest sender-test push runs: `41235591309` (manifest workflow) and `41235591321` (Ash-Sharh review workflow); check final conclusions and job steps before asserting success.
- No actual Telegram delivery has yet been confirmed in this implementation checkpoint. Confirm both repository secrets exist through a deliberate manual dispatch of the manifest workflow with an approved manifest and `send_to_telegram=true`. If secrets are absent, do not request tokens in chat; tell the user to add them as GitHub Actions repository secrets.
- The manual dispatch may not be executable through the currently available GitHub action tools; if unavailable, give the user a concise phone-friendly path to run it only after all CI checks pass.
- Do not start daily/Friday scheduling until reusable Quran/dua/dhikr production and a real MP4-to-Telegram delivery are proven.

## Immediate next actions
1. Check Actions runs `41235591309`, `41235591321`, `41235405611`, and `41235407692`. Fix failures and re-run relevant checks.
2. Review the new sender test and ensure all tests pass.
3. Verify the manifest workflow's Telegram step condition and output paths exactly match `output/review.mp4` and `output/review.caption.json`.
4. Perform one controlled Telegram delivery of a reviewed/approved video. Require Telegram API success and user confirmation of receipt.
5. Then implement and test a queue/batch of three distinct approved items. Add dua/dhikr render support only after exact content/source and asset approvals; do not weaken validation gates.
6. Keep the status and handoff documents synchronized.

## Latest follow-up
- Run `41235405611` completed successfully.
- Sender-test runs `41235591309` and `41235591321` were still in progress at the latest API check; no failures were reported, but do not mark them passed until their conclusions are completed/success.
- The connected GitHub tools currently available can inspect runs/artifacts/logs but do not provide workflow dispatch. A real Telegram send requires a one-time manual dispatch; do not enable send-on-push as a workaround.
- Manual dispatch from phone: repository > Actions > “Render manifest video for review” > Run workflow; branch `feature/telegram-review-notifications`; manifest `content/second_video_ash_sharh_94_1_8_draft.json`; `use_rotation=false`; `send_to_telegram=true`. This requires GitHub Actions secrets `TG_BOT_TOKEN` and `TELEGRAM_CHAT_ID`; never paste secrets into chat.


## Verified CI follow-up (2026-10-31)
- Runs `41235591309` (manifest workflow) and `41235591321` (Ash-Sharh workflow), both on commit `177be619d997da42ca353ecb943e08296d383136`, completed with conclusion `success`.
- In run `41235591309`, all steps including the full unit-test suite, Quran checks, render, MP4 technical validation and artifact upload succeeded. `Send review MP4 to Telegram` was skipped because this was a push event.
- In run `41235591321`, all steps including tests, approved audio/background preparation, render and artifact upload succeeded. Its Telegram step was skipped because that dedicated workflow is intentionally disabled for sending.
- The successful mocked Telegram sender test confirms request construction and handling of a positive API response only. It does not confirm real delivery.
- A new follow-up commit `3339853714fda6da77b8394ad8567130aa21bb3d` adds tests for three distinct approved manifest selection and fail-closed behavior when a full batch cannot be selected. The manifest workflow run `41236627114` has passed the full unit-test step including both new batch tests; final rendering and technical MP4 validation are still in progress. The paired Ash-Sharh workflow `41236627093` has also passed automated tests and is still rendering.
- Current content inventory is not ready for a three-video rotation: Al-Ikhlas is unapproved, the first Ash-Sharh prototype is not marked rotation-approved, and the Ash-Sharh 94:1–8 manifest remains a review draft. No dua/dhikr manifests exist. The renderer supports Quran only.
- No real Telegram delivery is confirmed. Keep all schedules disabled until three distinct approved items can render and a real Telegram send is verified.

- Latest live check: `41236627114` is still rendering the manifest video after all unit tests and Quran validations passed; `41236627093` is still rendering the Ash-Sharh review MP4 after its automated tests passed. Neither run has completed artifact upload yet, and both Telegram steps are expected to be skipped on push events.


## Rendering performance follow-up (2026-10-31)
- Batch regression tests passed in run `41236627114`, but both render workflows `41236627114` and `41236627093` remained active at the video-render step for an extended period. Live job log blobs were unavailable from the connector, so the cause is not confirmed.
- Removed the unnecessary FFmpeg `deshake` filter from the approved background pipeline in commit `2c7684e57f46739d764a4b7ff25623172b04cba1`. This preserves the approved background and overlays while testing a likely CPU bottleneck. Await the new workflow runs before claiming improvement.


## Render completion update (2026-10-31)
- Run `41236627093` completed successfully on the previous renderer revision: the 94:1–8 MP4 rendered and uploaded as artifact `13055821597` (34,107,653 bytes; expires 2026-11-07). Telegram step was skipped, not delivered.
- Run `41236627114` had not yet completed at the latest check.
- The targeted no-deshake performance change is commit `2c7684e57f46739d764a4b7ff25623172b04cba1`; new runs `41236886998` and `41236886984` were still in setup/install when checked. Do not infer the optimization works until they complete.


## Verified optimized render results (2026-10-31)
- Optimized revision `2c7684e57f46739d764a4b7ff25623172b04cba1` passed both workflow runs:
  - `41236886984` manifest review: Quran checks, unit tests, rendering, MP4 validation and artifact upload all successful; Telegram skipped on push. Artifact `13056036545` (`islamic-video-review`).
  - `41236886998` Ash-Sharh 94:1–8: audio rebuild, background, Quran checks, tests, render and artifact upload all successful; Telegram skipped by intentional pause. Artifact `13055697994`.
- Downloaded the optimized manifest artifact and inspected it: MP4 1080×1920, 30 fps, audio present, 62.8 seconds; representative frame preserves the approved gold cartouche, Arabic verse, gold number medallion, English translation and waterfall background.
- Observed render turnaround improved from roughly 3m52 on the earlier manifest run to roughly 1m45 on the optimized run (runner timing varies). Removing the unnecessary `deshake` filter is validated; the visual reference remains intact.
- New three-distinct-manifest batch tests passed as part of the optimized CI runs.
- Still outstanding: controlled manual Telegram dispatch with private GitHub Secrets configured, followed by user confirmation of receipt. Do not turn on daily/Friday schedules or TikTok publishing until real delivery and three varied approved content types are proven.


## Authoritative user clarification — Telegram is automatic delivery (2026-10-31)
- The user does NOT want to manually open GitHub Actions and dispatch each video.
- Target workflow: the engine automatically generates the planned videos and sends the resulting MP4 files to the user's Telegram. The user downloads them from Telegram and publishes them to TikTok manually.
- Do not present manual workflow dispatch as the normal operating procedure or ask the user to repeat it for each video. A manual dispatch can be used internally for a one-time controlled test only.
- Keep TikTok publishing disabled and manual.
- Do NOT enable a premature schedule: current content/rendering support is not yet ready for three varied daily videos. Complete Quran + authentic dua/dhikr/reminder rendering and validation, confirm a real Telegram delivery, and then configure the scheduled engine to send automatically. Daily/Friday schedules remain disabled until these gates are satisfied.
- Historical notes below about a required user-initiated manual dispatch are superseded by this clarification for the final operating design.


## User reaffirmation — varied video backgrounds (2026-10-31)
- The user explicitly wants background variety; do not send every video with the same background.
- Use a curated pool of multiple approved and rights-verified backgrounds, rotating between videos and avoiding immediate repeats whenever another eligible background exists.
- Possible visual families include calm nature, sky, sea, and Islamic architecture; keep the approved gold cartouche/verse medallions/text hierarchy consistent and readable.
- Do not invent approval or licensing. Never pick an unapproved asset just to make the background different. If the approved pool has no eligible alternative, fail safely and report the limitation.


## Quran variety follow-up — verified repository state (2026-10-31)
- The user wants different surahs and ayah selections while preserving all approved visual/audio requirements.
- `src/render_video_scenes.py` already creates one timed screen per verse and checks the ordered verse list and processed per-verse duration keys. It remains Quran-only.
- `src/validate_quran_text.py` compares exact Unicode Arabic against the reviewed Uthmani reference snapshot; missing or mismatched text fails closed.
- The shared reference snapshot currently has 94:5-6 and 112:1-4; Ash-Sharh 94:1-8 has a separate approved reference file. The Al-Ikhlas manifest is still a candidate with audio and background unapproved, so it is not eligible for production rotation.
- No `data/assets` or asset catalog exists in the current branch tree. Backgrounds are currently supplied in each manifest and checked for approval by the renderer; do not claim automated shared background rotation is active.
- Next safe Quran-variety work: expand reference coverage only from exact reviewed source passages, then add a separate candidate manifest for each passage only after exact matching official recitation, documented reuse rights, and user listening review. Keep translation source/provenance attached to each manifest.
- Keep the ornate gold cartouche, separate gold verse medallions, exact white Arabic, smaller English translation, vertical 9:16/1080x1920/30fps, authentic matching recitation, no music/synthetic recitation, no public reciter name, and manual review/no auto-publishing.


## Full-Quran short-clip engine requirement (2026-10-31)
- Do not build a workflow tied to Surah Ash-Sharh. The first approved render is the visual/audio quality reference only. The Quran selector's intended scope is all 114 surahs and all ayahs.
- User requires clean separate clips of no more than 65 seconds. Renderer now rejects audio duration >65.000s via `validate_video_duration`; regression tests are in `tests/test_render_video_duration.py`.
- Passage selection must be dynamic and contiguous: target 55–60 seconds, hard cap 65 seconds. Use actual durations of complete official verse audio files. Never cut inside an ayah, change recitation speed, reorder, or skip verses within a selected range.
- Full-Quran data is not yet integrated. Current exact Uthmani snapshot is only a small reviewed sample; do not claim all-surah coverage. The official King Fahd Complex verse archive URL is known and individual verse extraction has been proven for Ash-Sharh, but archive filename-to-surah/ayah mapping and rights checks must be generalized and validated.
- Next implementation: inspect the official verse archive directory once, derive and validate an exact mapping for all 6236 ayahs, pair it with a trusted Uthmani text and a verified translation corpus, then select contiguous ranges using real audio durations. Keep provenance and rights internally. If any verse lacks exact source/audio/translation, exclude it transparently rather than fabricating it.
- Preserve gold cartouche, separate gold verse medallions, exact white Arabic, smaller English translation, approved background rotation, authentic recitation, no music/synthetic audio, no public reciter name, 9:16/1080x1920/30fps, and no TikTok auto-publishing.


## Quran-wide archive inventory builder added (2026-10-31)
- New `src/build_official_audio_inventory.py` inspects the official King Fahd Complex Hafs archive via RemoteZip and expects a complete one-to-one mapping of all 6,236 Quran verses across the canonical 114 surah verse counts.
- New workflow `.github/workflows/build-quran-audio-inventory.yml` runs automatically on changes to the inventory builder/workflow on `feature/telegram-review-notifications`, and uploads the JSON inventory as an artifact only if the complete mapping validates.
- First run: `41238698032`; check its result before relying on the generated inventory. A successful inventory means archive path mapping only; it is not a claim that each audio item was individually listened to or that translation/text rights and validation are complete.
- Next: verify the artifact and filename mapping, then connect the exact audio IDs to a trusted Uthmani text source and verified translation source; use per-verse duration metadata to pack contiguous verses into 55–60 second clips, hard maximum 65 seconds.


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


## Resume checkpoint — corpus artifact fix (2026-10-31)
- Latest verified feature branch: `feature/telegram-review-notifications`; never write to `main`.
- Run `41239290344` passed all 8 operational steps. Its logs explicitly report `Validated 6,236 translations from Saheeh International (en.sahih)` and the audio passage probe selected contiguous 94:1–8 at 62.579 seconds.
- The downloaded run artifact `13056846824` did not contain the translation JSON because the workflow's upload path incorrectly named `english_saheeh_translation.json`; the build step actually wrote `saheeh_international_translation.json`.
- Corrected `.github/workflows/build-quran-audio-inventory.yml` in commit `46cf87d48d18ce41679341254ed9695c8927abfb`. Added a fail-fast artifact-input verification (edition `en.sahih`, 6,236 dictionary entries, and retained rights/review status) and corrected the upload path.
- This workflow-fix commit must trigger a fresh Actions run. Check its job and inspect the new artifact to confirm the translation JSON is present and has 6,236 entries. Do not rely on the earlier artifact for translation data.
- The branch had two documentation-only commits after `df8b8e7` before this workflow fix; the feature branch is not to be reset or rebased onto `main`. Continue from the live feature branch head.
- Important content gates remain: Quran-wide exact Arabic Uthmani source is not integrated (the checked-in reviewed reference is still only a small sample); new recordings require exact matching and listening review; translation rights for commercial reuse need confirmation; dua/dhikr items need trusted sources and approval; background catalog variety is not yet active; no actual Telegram MP4 receipt is confirmed.
- Do not enable any schedule, daily/Friday dispatch, or TikTok publishing. TikTok remains manual only.
- Next engineering sequence: verify the new artifact; integrate a Quran-wide Arabic text source with exact 6,236-key validation and source metadata; join it to audio inventory and Saheeh translation by exact `surah:ayah` keys; retain passage-level rights/review gates; then implement safe approved-content queueing and complete a real Telegram delivery test before scheduling.


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


## Resume point — renderer gate passed (2026-10-31)
- Latest run `41240328907` is complete with conclusion `success`; all render steps passed, including the new renderer-level Quran audio approval gate.
- Latest artifact ID `13056564523` (`islamic-video-review`) was downloaded and checked. `review.mp4`: H.264/AAC, 1080×1920, 30 FPS, 62.8 sec. `review.caption.json` parses correctly with real newline characters, `review_required`, and `publishing=disabled`.
- Telegram delivery step was skipped (push event); no delivery receipt exists yet. Next operational milestone is an explicit manual dispatch with Telegram send enabled, then confirm the MP4 arrives in the user's Telegram chat. Do not enable schedules before that confirmation.
- The 94:1–8 render remains review-only: user approval applies to the exact 94:5–6 recording, not the full 94:1–8 candidate. Never publish this candidate without separate listening approval.
- Continue only on `feature/telegram-review-notifications`; `main` remains untouched. Item 5 (dua/dhikr engine) remains deferred.
