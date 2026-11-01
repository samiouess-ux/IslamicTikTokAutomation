# Project status — IslamicTikTokAutomation

Last updated: 2026-11-01

## Latest delivery-slot correction and render fixes (2026-11-01)
- This section supersedes older schedule notes below: the required schedule is **one distinct Quran review video at each Tunisia slot: 04:00, 12:00, and 18:00** (GitHub cron: `0 3,11,17 * * *` UTC). GitHub may delay scheduled starts under load.
- Each scheduled run prepares one video only; it must not expect a three-video batch.
- Fixed `src/build_quran_draft_manifests.py`: its old minimum of two manifests contradicted the one-video-per-slot workflow. It now accepts one prepared distinct-surah draft while retaining all review/production gates. Added a one-manifest regression test.
- A subsequent run exposed a long Saheeh translation that exceeded the renderer's fixed five-line layout. Updated `src/render_quran_review_previews.py` to step down the translation font size while preserving every word; it refuses clipping if the text still cannot fit. Added a wrapping regression test.
- Relevant commits: `99fd01bba9a149ec136398d12f36127fe0503eb1` (single manifest), `0eeabe3c07fa4c1dd92bd4478d1a9f8225059bad` (single-manifest test), `78687c5988f69fc7d21c0d666e0f3dd47ad9082c` (translation fitting), `ff1cf0e2955fc5a2e9ea8cddd3d80521826473a1` (translation test).
- Test workflow `test-quran-request.yml` run `41289938456` passed. Full scheduled-pipeline validation run `41289938290` is still being checked; do not declare the renderer or Telegram delivery verified until it completes.
- Telegram delivery is not proven by push-triggered tests. The user confirmed a Telegram test message, but the first scheduled MP4 delivery still needs an actual Telegram API confirmation and a successful delivery-history push.
- TikTok publishing remains manual-only; never enable automatic TikTok publishing. Do not modify `main`.


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
- Earlier French translation research is retained only as historical context; French is no longer an output language.
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
