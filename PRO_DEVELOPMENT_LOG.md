# Islamic Dua & Adhkar Pro — Development Log

This log is the durable record for work on `feature/quran-video-pro`.
Production branch `feature/telegram-review-notifications` is out of scope and must not be modified by Pro work.

## 2026-11-05 — Baseline audit (documentation only)

### Scope and baseline
- Repository: `samiouess-ux/IslamicTikTokAutomation`
- Branch: `feature/quran-video-pro`
- Audited baseline commit: `7d8c21ae0b7d57ae7b66a28885ebf3ecb299ecdb`
- Latest known review run: [Actions run #106](https://github.com/samiouess-ux/IslamicTikTokAutomation/actions/runs/41945437319)
- This entry records a source inspection. No application code was changed as part of this audit.
- No GitHub Actions workflow was started or rerun during this audit. No Telegram message was sent during this audit. No production branch, Cron, publishing setting, or secret was changed.

### User-approved product goal
Build a genuinely professional Quran video engine whose opening captures attention respectfully, whose visual storytelling and motion are polished, and whose Quran text, translation, recitation, timing, and rights provenance are protected. Each output remains review-only; automatic TikTok publishing stays disabled.

### Confirmed implementation gaps
1. **Visual templates are not meaningfully distinct yet.**
   - `src/render_video_scenes.py` supports four template names, but all use the same overall composition and fixed title/text/verse-number positions.
   - The main differences are accent colors, border geometry, and verse-number decoration. This explains why the last two comparison videos looked almost the same.
   - `tests/test_quran_visual_templates.py` only verifies that the generated PNGs are pixel-different; it does not measure meaningful layout, hierarchy, motion, readability, or perceived design quality.

2. **The agreed opening cover is not implemented in the active Pro renderer.**
   - `DESIGN_SPEC.md` requires a Quran cover showing “القرآن الكريم”, the surah name, and the exact ayah range, targeting 1.6 seconds with a 0.4-second alpha fade.
   - The inspected render path creates verse overlays and starts the selected audio at the beginning; no separate cover-scene implementation or cover timing/fade was found in `src/render_video_scenes.py`.

3. **The video duration limit conflicts with the design specification.**
   - `DESIGN_SPEC.md` sets a maximum of 40 seconds for the final MP4 and audio.
   - `src/render_video_scenes.py` and the active workflow's ffprobe gate currently allow up to 65 seconds.
   - This must be reconciled before calling the renderer compliant with the approved spec.

4. **Approved background candidates are not active rotation assets.**
   - `data/background_candidates.json` contains four user-approved candidates and explicitly says they await integration.
   - `src/asset_rotation.py` requires `rights_verified=true` and normalized `source_url`/`asset_url` fields; the candidate records currently use a different shape and do not satisfy those checks as written.
   - The active manifest renderer takes one background URL from the manifest; the inspected workflow does not select and rotate among the four candidate records.
   - Therefore the existence of four candidate records is not proof that background rotation is operational.

5. **Full-Quran reference coverage is not yet enabled.**
   - `data/reference/quran_text_uthmani.json` currently contains only six reviewed verse entries: Ash-Sharh 94:5-6 and Al-Ikhlas 112:1-4.
   - The catalog builders can prepare 6,236-verse Arabic and Saheeh translation candidate corpora, but the Arabic candidate is explicitly unreviewed and blocked from rendering; translation rights and verse-level review are also still required.
   - The audio inventory workflow contains checks for 6,236 mapped official archive entries, but this does not by itself approve every exact recording for every passage.
   - Full-Quran rotation must remain fail-closed until all required text, translation, audio, and rights gates are met.

6. **The last comparison was not a fair test of content/audio improvement.**
   - Workflow input `compare_designs=true` deliberately renders two visual overrides from the same manifest, same selected audio, and same downloaded background.
   - Identical audio in that comparison is expected; it was intended to isolate visual changes.
   - The actual failure was that the visual changes were too small to create a professional, clearly distinguishable result.

### Confirmed safeguards to preserve
- Exact Arabic text comparison is Unicode-exact; no normalization, rewriting, or automatic correction.
- Arabic rendering requires RAQM and a known Arabic font.
- The renderer requires approved/user-approved background metadata and documented audio approval/rights.
- No music; no synthetic Quran recitation; no public reciter attribution.
- Quran verses must remain ordered and complete; never cut a verse mid-recitation.
- Captions and each video require user review.
- Automatic publishing must remain disabled.

### Required development sequence
1. Design a genuinely new visual direction and define objective acceptance checks for composition, typography, legibility, and motion.
2. Implement the approved opening cover and its timing/fade without inserting silence or changing the recitation stream.
3. Integrate the four already-reviewed background candidates into a rights-aware, deterministic rotation; fail closed if no eligible asset exists.
4. Resolve the 40-second specification versus 65-second implementation mismatch.
5. Strengthen visual regression tests so they test layout and required design elements, not merely pixel inequality.
6. Expand Quran text/translation/audio coverage only through explicit source, rights, exact-match, and human-review gates.
7. Produce a review video, inspect the actual MP4 and audio/video metadata, and record the user's visual/audio feedback before accepting the result.

### Validation status for this audit
- Source inspection: completed for the files listed above.
- Unit tests: not run during this audit.
- Render: not run during this audit.
- Telegram delivery: not run during this audit.
- Production branch / Cron / TikTok publishing: untouched.

### Change-control rules
- All Pro implementation commits go only to `feature/quran-video-pro`.
- Do not merge Pro into production without explicit user approval.
- Do not trigger Actions or send Telegram review videos without explicit user approval for that run.
- Log every code change, test, workflow run, artifact/delivery result, failure, and approval in this file.


## 2026-11-05 — Development milestone 1: opening cover and duration gate

### Changes committed to Pro
- `src/render_video_scenes.py`
  - Added a separate 1080×1920 Arabic opening-cover overlay.
  - Cover includes “القرآن الكريم”, the manifest's Arabic surah name, and the exact selected verse/range rendered with Arabic-Indic numerals.
  - Cover uses a restrained translucent dark panel and gold framing.
  - Cover fades out from 1.2s to 1.6s.
  - The existing audio remains mapped from input 1 without a new delay, inserted silence, speed change, or audio filter.
  - Renderer maximum duration is now 40 seconds.
- `.github/workflows/render-manifest-video.yml`
  - MP4 technical validation now rejects durations above 40 seconds, matching the design specification.
- `tests/test_quran_visual_templates.py`
  - Added checks for opening-cover creation, 1080×1920 dimensions, required timing constants, and refusal when the Arabic surah name is missing.

### Commits
- Renderer: `eac695aee000a1e22dcbf4501ae437d408501866`
- Workflow duration gate: `04eb08b0f7159c6f839a90f142a6b71e47d800e8`
- Opening-cover tests: `30130543311fa96c14b0e03d928058388175fe85`

### Validation and limitations
- GitHub source re-fetch confirmed the renderer contains the new cover path and 40-second cap, the workflow contains the 40-second MP4 gate, and the tests contain the new cover checks.
- Unit tests have **not** been executed.
- No render or MP4 visual/audio inspection has been performed.
- No GitHub Actions run was triggered.
- No Telegram message was sent.
- The cover's appearance, alpha fade behavior, and exact synchronization must be verified in a real rendered review MP4 before this milestone can be accepted.
- This milestone does not yet implement the four-background rotation or a genuinely redesigned verse-screen layout.

### Current status
- Code committed to `feature/quran-video-pro` only.
- Production branch, Cron, secrets, and publishing configuration remain untouched.
- Milestone status: **implemented, awaiting automated and visual validation**.


## 2026-11-05 — Development milestone 2: distinct verse-screen composition geometry

### Changes committed to Pro
- `src/render_video_scenes.py`
  - Replaced the shared fixed title/body/verse-number coordinates with per-template composition geometry.
  - `ornate_gold_classic`, `nature_clean`, `minimal_mushaf`, and `cinematic_landscape` now use different title positions, Arabic text centers, text widths, and verse-number positions, in addition to their existing frame treatments and palettes.
  - Arabic verse text remains sourced verbatim from the manifest; wrapping only inserts visual line breaks between existing words and still fails closed if it cannot fit safely.
- `tests/test_quran_visual_templates.py`
  - Retained pairwise pixel-difference checks and added a separate assertion that the full non-transparent composition bounds differ across all four templates. This rejects a color-only distinction as sufficient evidence.

### Commits
- Renderer layout geometry: `ccba9cf91f39ac2338991d8420f73c975611b648`
- Composition-bound regression test: `29fdcb189f6fcc3c6ac4d983f923579d054619f0`

### Validation and limitations
- Both updated files were committed to `feature/quran-video-pro` only and fetched from that branch for the sequential updates.
- The new test has **not** been executed in CI or locally; distinct alpha bounds are an authored regression assertion, not a passing test result yet.
- No rendered MP4 has been produced or visually inspected. The layouts are structurally more distinct in source, but professional appearance and legibility still require a real review render.
- Background-candidate rotation remains unintegrated. The four candidate records still do not satisfy the strict normalized rights/source/asset schema consumed by `src/asset_rotation.py`; no rights status was invented or weakened.
- No GitHub Actions run was triggered and no Telegram message was sent.
- Production branch, Cron, secrets, and auto-publishing remain untouched.

### Current status
- Milestone 2: **implemented, awaiting automated and rendered visual validation**.


### Follow-up layout safety adjustment
- After checking the new coordinates against the English translation overlay's fixed lower-screen region, moved the `minimal_mushaf` and `cinematic_landscape` verse markers upward to avoid a likely collision with long (up to five-line) translations.
- Commit: `1934a58626210788aebfb5b562239481d9f38d75`.
- This is a source-level spacing correction only; visual clearance still needs confirmation in a rendered MP4.


## 2026-11-06 — User-approved scope pivot: Dua & Adhkar Pro

### Binding product decision
- The user clarified that this Pro branch is to become the dua-and-adhkar specialist branch of the larger IslamicTikTokAutomation engine.
- The existing production branch `feature/telegram-review-notifications` remains Quran-only and must continue unchanged.
- This branch must focus exclusively on professionally produced dua and dhikr videos. Do not add Quran-video production to Pro.
- Reuse safe shared engine capabilities where technically appropriate (content selection/rotation, manifest validation, visual asset selection, video encoding conventions, review safeguards). Do not duplicate the whole engine or couple Pro changes into production.
- The user wants Pro to use the existing/original Telegram bot for review delivery if a safe isolated route can be established. This is a design requirement, not yet implemented or verified. Do not send Telegram messages or change bot configuration/secrets as part of this work without explicit approval.
- All work and decisions must be recorded in this log and a Pro-specific status file so work can resume in a new chat without losing context.

### Read-only source inspection findings
- The current Pro `src/validate_content_manifest.py` already recognizes `content_type` values `quran`, `dua`, and `dhikr`.
- For dua/dhikr it already requires a non-empty `items` list, exact Arabic wording, a named HTTPS religious source, no Quran-recitation audio mislabeled as dua/dhikr, and approval/rights gates for spoken dua or ambient audio.
- The current `src/orchestrator.py` is explicitly Quran-only: `DAILY_CONTENT_TYPE = "quran"`, its plan builder insists on Quran manifests, and it calls the Quran-specific `src/render_video_scenes.py` renderer.
- The current Pro renderer is explicitly Quran-specific (verse/surah overlays, Quran recitation checks and Quran cover). It must not be reused unchanged for dua/dhikr.
- `src/asset_rotation.py` is a potentially reusable shared utility for approved, user-approved, rights-verified backgrounds/audio; its catalog schema must be respected and tested.
- The existing Pro branch currently has no verified dua/dhikr production renderer, no verified dua/dhikr content library, and no verified Telegram delivery integration.
- The existing Quran-oriented history in this log is retained as historical context only; it is not the current Pro product scope.

### Safe implementation plan
1. Map the shared modules and their callers on this branch; identify reusable components versus Quran-only code before changing behavior.
2. Define a strict dua/dhikr content schema with exact wording, source title/URL, hadith grading or authenticity reference where applicable, category, repeat count where relevant, and human-review state. Never invent religious wording or authenticity.
3. Build a dedicated dua/dhikr visual renderer and templates; do not route dua/dhikr through Quran verse/surah rendering.
4. Extend the Pro orchestrator to plan dua/dhikr batches, avoid recent repeats, and fail closed on missing/invalid source metadata.
5. Add unit tests for source validation, Arabic preservation, content selection/non-repetition, layout bounds, audio policy, and review-only publishing.
6. Inspect the existing Telegram delivery architecture read-only and design a separate, clearly labeled Pro delivery route through the original bot. Do not change production workflow, bot secrets, Cron, or send messages until the isolation design is reviewed and explicitly approved.
7. Only after code/tests are ready and separately approved: perform a review render and then a user-approved Telegram review test. No TikTok auto-publishing.

### Current checkpoint and restrictions
- This entry is a documentation-only scope decision based on read-only source inspection.
- No source code, workflow, manifest, bot configuration, production branch, Cron, or secret was changed.
- No GitHub Actions workflow was run; no render was performed; no Telegram message was sent; nothing was published.
- Next action: implement the dedicated dua/dhikr content schema and renderer in this branch only, after mapping exact shared render/manifest helpers. Keep the Quran production engine untouched.


## 2026-11-06 — Dua/dhikr source-validation hardening

### Implemented on this branch
- Updated `src/validate_content_manifest.py` to require every dua/dhikr item to have a unique stable `id`, exact Arabic wording, named HTTPS source, precise `source_reference`, `verification_status: verified`, explicit `human_reviewed: true`, and a supported `kind` classification.
- Optional `repeat_count` must be a positive integer.
- Items classified as `prophetic_dua` must include a non-empty `hadith_grading` field.
- Updated `tests/test_validate_content_manifest.py` fixtures and added regression tests for missing human review, missing hadith grading, and duplicate item IDs.

### Commits
- Validator: `545496fd29b590c38abf61f9a82b3750d90060c6`
- Tests: `e4c3ae5365a44277012a226bb99a5ae191583e33`

### Verification status
- GitHub file writes succeeded on `feature/quran-video-pro`.
- Unit tests were NOT run in this session; these are added tests, not passing test results.
- No GitHub Actions workflow was run, no render was performed, no Telegram message was sent, and no TikTok publishing occurred.
- No production branch, Cron, secrets, or production delivery path was changed.

### Next step
- Implement a dedicated dua/dhikr renderer with its own layouts and strict audio/background review gates; keep the Quran renderer unchanged. Then add renderer-focused unit tests and run only local tests when explicitly safe/approved. Telegram reuse remains a later isolated integration task.


## 2026-11-06 — Dedicated Dua & Adhkar renderer milestone

### Implemented on Pro branch
- Added `src/render_dua_dhikr.py`, a separate renderer that accepts only `dua` or `dhikr` manifests and exactly one reviewed item per video.
- It creates a 1080×1920 Arabic overlay using Amiri Bold and Pillow RAQM; preserves the manifest Arabic wording verbatim, supports an optional English meaning and repeat count, and refuses text that cannot fit the safe layout.
- It uses the manifest's approved background candidate and the existing validation gates. It supports approved spoken-dua/ambient audio files or a deliberately silent clip with an explicit positive duration.
- It enforces the 40-second maximum and outputs a review MP4 only. It contains no Telegram or TikTok publishing action and does not import the Quran renderer.
- Added `tests/test_render_dua_dhikr.py` for vertical overlay dimensions, transparent PNG output, and rejection of empty/overlong Arabic.

### Commits
- Dedicated renderer: `6eded850610126acdc10becac8e66d62cdcb8948`
- Renderer tests: `463512211a001475b23cc5472c190f0de152ccc0`

### Validation status and limitations
- GitHub file creation succeeded on `feature/quran-video-pro`.
- Tests have NOT been executed. The PNG layout test requires a runtime with Pillow RAQM and the Amiri Bold font installed.
- No MP4 render, workflow run, Telegram message, or TikTok publishing was performed.
- The renderer is not yet wired into a Pro-specific orchestrator; current `src/orchestrator.py` remains Quran-only and was not modified.
- The current manifest validator checks background approval flags and source URLs, but a future integration must ensure audio file paths and asset provenance are checked in the actual execution environment.
- The silent-audio path and FFmpeg filter graph still require automated execution/technical validation before use.
- No production branch, Cron, secrets, or production delivery path was changed.

### Next step
- Add an isolated Pro-only orchestrator for dua/dhikr selection, recent-repeat avoidance, and dry-run preflight. Keep the existing Quran orchestrator unchanged. Then add tests for content rotation and confirm the renderer CLI integration without running a render.


## 2026-11-06 — Isolated Pro orchestration milestone

### Implemented on Pro branch
- Added `src/pro_orchestrator.py`; it accepts only `dua` or `dhikr`, uses the existing deterministic `content_rotation.choose_manifests` helper, and requires rotation-approved manifests with a complete, distinct batch.
- Every manifest is passed through the shared fail-closed validator and must contain exactly one item, a stable manifest ID, and mandatory manual review with auto-publishing disabled.
- Added a Pro-specific history path defaulting to `data/dua_dhikr_rotation_history.json`; the Quran orchestrator and its history path remain unchanged.
- The default command is dry-run preflight. Rendering requires the explicit `--render` flag and routes only to `src/render_dua_dhikr.py`.
- Rendering does not consume rotation history. Telegram delivery is not implemented; history must not be committed until a later delivery/approval design defines a confirmed event.
- Added `tests/test_pro_orchestrator.py` for dua plan creation, repeat rejection, wrong content-type rejection, and one-item-per-video enforcement.

### Commits
- Pro orchestrator: `28b0dba34a409497ec5b11f44be299525084205c`
- Pro orchestrator tests: `75a603b2adedfdbeecf043ab75f48189513cbd7f`

### Validation status
- GitHub writes succeeded on `feature/quran-video-pro`.
- Tests have NOT been executed; no passing test claim is made.
- No preflight command, render, Actions workflow, Telegram send, or TikTok publish was run.
- No verified production content library exists yet. The Pro content directory is expected to contain explicitly reviewed manifests; an empty/missing directory correctly blocks selection.
- No production branch, Cron, secrets, or production delivery path was changed.

### Next step
- Add a safe example manifest schema/template without real religious content, then inspect Telegram workflow/bot routing read-only to determine whether a distinct Pro route can share the original bot without changing production behavior.


## 2026-11-06 — Renderer consolidation and Telegram architecture audit

### Renderer consolidation correction
- A deeper branch inventory found that `src/render_dua_video.py` and `tests/test_render_dua_video.py` already existed before the new Pro renderer work. The existing renderer supports multiple sourced items per video, explicit per-item durations, checks spoken/ambient audio duration against the full slideshow, and has a 65-second hard cap (with a 60-second target).
- To avoid two competing renderers, the Pro orchestrator was changed to route to the existing `src/render_dua_video.py` and to validate explicit positive per-item durations plus the renderer's hard cap.
- Pro manifests may contain multiple reviewed items; the orchestrator records all item IDs. It still requires a complete approved manifest batch and uses the separate Pro history.
- The temporary duplicate `src/render_dua_dhikr.py` and its test file were removed from this branch. Their creation/removal is recorded here for transparency.
- Existing `tests/test_render_dua_video.py` is the renderer regression suite; it has not been run in this session.

### Consolidation commits
- Pro orchestrator routed to existing renderer: `17921d5dc5aed0c10474c639ba29229b301c6154`
- Pro orchestrator tests aligned with multi-item manifests: `c62e7cc042381ecdb8f85faab6f93faeb5b34fce`
- Removed duplicate renderer: `5adb589e0bc46c8738cb90d2aa374b2f32ddf15d`
- Removed duplicate renderer tests: `fcd8265d93cf5704cd6c4a671e44df98caf95282`

### Read-only Telegram architecture findings
- `.github/workflows/telegram-quran-request.yml` is guarded to run only on `feature/telegram-review-notifications`; its checkout is also pinned to that production branch. It must not be reused or modified for Pro.
- The existing workflow references repository secrets `TG_BOT_TOKEN` and `TELEGRAM_CHAT_ID`, then calls `src/send_telegram.py`.
- `src/send_telegram.py` uploads a review MP4 to Telegram and does not publish to TikTok, but its caption is hard-coded as `QURAN PRO REVIEW`; it is not an appropriate Pro caption as-is.
- The Pro branch can likely reuse the same original bot credentials through a separate manually dispatched Pro workflow, but this has not been implemented or tested. No secrets were read, changed, or exposed.
- A safe Pro route should be isolated behind a manual-only workflow on `feature/quran-video-pro`, use the existing secret names without changing them, label the message as Dua/Adhkar Pro review, require review-only metadata, and have no TikTok publishing step. Do not dispatch it until the user explicitly approves a send test.

### Validation status
- All changes remain on `feature/quran-video-pro`.
- No tests were executed, no preflight or render command was run, no workflow was dispatched, and no Telegram message was sent.
- Production workflow, production branch, Cron, secrets, and TikTok publishing remain untouched.

### Next step
- Add a Pro-specific caption/sender and a manual-dispatch-only Pro workflow, with tests and strict branch guards. Keep it dormant; do not run it or send Telegram without explicit user approval.


## 2026-11-06 — Isolated Pro Telegram sender

### Implemented on Pro branch
- Added `src/send_pro_telegram.py`; it is separate from the existing Quran sender and labels deliveries as `DUA & ADHKAR PRO`.
- Sender accepts only `dua` or `dhikr` metadata and requires `review_only: true` plus `auto_publish: false`.
- It enforces Telegram's 50 MB video limit and 1,024-character caption limit, requires the existing `TG_BOT_TOKEN` and `TELEGRAM_CHAT_ID` environment secrets, and verifies Telegram's returned message ID.
- It deliberately does not retry ambiguous network failures; an uncertain result must be reconciled before another send to avoid duplicate review messages.
- Added offline unit tests for Pro branding, rejection of Quran content, mandatory review-only metadata, disabled auto-publishing, and caption length.

### Commits
- Pro sender: `9f93f7a143763a2f1d2384c5f8be829ce733b457`
- Sender tests: `b558c01736860d101e37e4aa3a175d4c97b43f61`

### Validation and restrictions
- GitHub file creation succeeded on `feature/quran-video-pro`.
- Tests have NOT been executed. No Telegram API call was made and no credentials were read or changed.
- No workflow was created or dispatched in this step. The Pro sender is not yet connected to an automated/manual workflow.
- Existing Quran sender and production workflow were not edited. No production branch, Cron, secrets, TikTok publishing, or production delivery path was changed.

### Next step
- Design a manual-dispatch-only Pro workflow with a strict `feature/quran-video-pro` ref guard, validate the selected manifest and review-only metadata before rendering, and send only after a deliberate workflow dispatch. Keep it dormant until the user explicitly approves a Telegram test.


## 2026-11-06 — Pro Telegram caption preparation and duration gate

### Implemented
- Added `src/prepare_pro_telegram_caption.py` to validate a dua/dhikr manifest and produce a caption payload explicitly marked `review_only=true` and `auto_publish=false`.
- Caption text is assembled only from the validated manifest's Arabic items and optional supplied English fields; the script does not invent translations.
- Reduced the Pro renderer's target and hard maximum duration to 40 seconds. Anything longer is rejected before media composition.
- Added a focused offline test for the caption-preparation entry point.

### Commits
- Renderer 40-second cap: `3a2fdffb1ec1ba5b9e2fcae4f50eba08f1b57dc3`
- Caption preparation: `d81dc90d07b50c0c8d95d58f55d634bd333f96c4`
- Caption preparation test: `1404abe2c2097252614f95270d5298bf2ae16b3c`

### Not yet done / safety
- Tests have NOT been run.
- No GitHub Actions workflow was added or dispatched in this step.
- No render, Telegram API request, secret access, or TikTok publishing occurred.
- A workflow must not be connected yet: durable reservation/idempotency for content history must be designed first. Current Pro orchestration selects against history but does not persist a reservation after a confirmed delivery. This must be solved before enabling a Telegram workflow, otherwise a later run could select the same manifest again.
- No production branch, production workflow, Cron, or Quran sender was changed.

### Next
- Implement and test a Pro-only reservation ledger with safe states (reserved, delivered, uncertain) and explicit reconciliation semantics. Only after that should a manual-dispatch workflow be added, with both render and Telegram send requiring explicit input confirmations.


## 2026-11-06 — Durable Pro delivery reservation ledger

### Implemented
- Added `src/pro_delivery_ledger.py` with durable JSON ledger operations and atomic file replacement.
- Supported states: `reserved`, `delivered`, and `uncertain`.
- Any existing state blocks a second reservation for the same manifest ID.
- A delivery can be marked `delivered` only with a positive Telegram `message_id`.
- Ambiguous delivery can be marked `uncertain`; it remains blocked from resend.
- Releasing an uncertain/reserved item requires the exact human confirmation token `CONFIRM_NOT_DELIVERED`. Delivered entries are terminal.
- Added offline tests covering duplicate blocking, confirmed delivery, uncertain reconciliation, and terminal delivered state.

### Commits
- Ledger module: `acfa42ea76285f6a6383325617b1bf2ad2bd1e69`
- Ledger tests: `ceb5c3f35ce52786c7bc49d31fcc3934dc60b31c`

### Important integration boundary
- This ledger module is implemented but not yet wired into the Pro orchestrator or a workflow. Before any workflow is enabled, it must reserve a manifest and persist that reservation to the Pro branch before attempting Telegram delivery; then persist delivered/uncertain state after the API result. The workflow must serialize runs and commit ledger updates to avoid concurrent duplicate reservations.
- Tests have NOT been executed.
- No workflow was created or dispatched, no render occurred, no Telegram request was made, and no TikTok publishing occurred.
- Production Quran branch, its workflow, Cron, secrets, and delivery route remain untouched.

### Next
- Integrate the ledger with Pro preflight and design serialized manual-dispatch workflow commits. Keep rendering and Telegram send behind separate explicit confirmation inputs.


## 2026-11-06 — Ledger branch-placement incident and correction

### Verified repository state and correction
- Explicit-ref inspection confirmed the misplaced ledger source and test were removed from `feature/telegram-review-notifications` (source deletion commit `bbf3378fe8ff80c0393dc0922fe155ace5b46277`; test deletion commit `980d8c88114b40272d537735e0e923d2c0e2ca01`).
- Recreated `src/pro_delivery_ledger.py` and `tests/test_pro_delivery_ledger.py` only on `feature/quran-video-pro` (commits `e2622bb20fbd695ccf61f4847203afa691c3e6a7` and `2c989ba003b2f56b4b31ac1ce35e7f0096594986`).
- Added a process-level file lock around ledger read/modify/write operations and atomic JSON replacement. This protects operations sharing one runner filesystem; it does not by itself provide cross-run persistence or serialize separate GitHub runners.
- Integrated reservation before Telegram send, marking uncertain outcomes without automatic retries, and recording a delivered state only after a positive Telegram `message_id` (sender commit `9b7e2e4ab5bc807f74f4a64a485720caec7f2a22`).
- Added the stable manifest ID to the generated Pro caption payload (commit `24a1e9eaf38ef1f4c1ee29f310db37b3b4426c46`).
- Added mocked sender tests for confirmed delivery and uncertain-send duplicate blocking (commit `36739415e233e834e921d2319887e450e9aca3e5`).
- Explicit-ref verification is still required after these writes. No unit tests have been run.

### Impact and safeguards
- Pro Telegram delivery is still not enabled by a workflow. The local ledger is not yet persisted between separate workflow runs; do not claim cross-run idempotency until a safe persistence/serialization workflow is implemented and verified.
- No workflow dispatch, render, Telegram API call, or TikTok publishing was performed.
- No secrets, Cron configuration, or production workflow logic was changed.

### Next safe action
- Re-fetch all changed Pro files using the explicit `feature/quran-video-pro` ref and verify production remains free of Pro ledger files.
- Then design a dormant manual-only Pro workflow that serializes runs and persists the ledger safely before/after Telegram delivery. Do not enable or dispatch it without explicit approval.
- Build a reviewed dua/dhikr content library from trustworthy primary sources before any real delivery.
-### Production cleanup completed (2026-11-06)
- Deleted `tests/test_pro_delivery_ledger.py` from `feature/telegram-review-notifications` using the approved GitHub contents deletion operation.
- Deletion commit: `980d8c88114b40272d537735e0e923d2c0e2ca01`.
- Verified by explicit-ref fetch immediately after production cleanup: both files returned 404 on production and were absent on Pro at that moment. They were later recreated only on `feature/quran-video-pro`, as documented in the subsequent ledger integration entries.
- No tests were run and no rendering, workflow dispatch, Telegram send, or TikTok publishing occurred.

### Explicit-ref verification after ledger/sender integration (2026-11-06)
- On `feature/quran-video-pro`, confirmed these files exist: `src/pro_delivery_ledger.py`, `tests/test_pro_delivery_ledger.py`, `src/send_pro_telegram.py`, `src/prepare_pro_telegram_caption.py`, and `tests/test_send_pro_telegram.py`.
- Current blob SHAs: ledger `309a5afb915a1a25c7ddf5ee7c9a2a4706348828`; ledger tests `d0fc3dfd50f10abb1b4c6622449b2d9afe44e53f`; sender `f93548d0938112072b72600528f5d7362c8d11ad`; caption prep `9551f47852d1460b962b266870952a44bf920e4a`; sender tests `f36a9a86efb89227d134caece6ace000d2591e26`.
- On `feature/telegram-review-notifications`, explicit-ref fetch returned 404 for both ledger source and ledger test.
- `PRO_DEVELOPMENT_LOG.md` and `PRO_PROJECT_STATUS.md` were updated on Pro. No unit tests were run. No workflow was dispatched, no render occurred, and no Telegram or TikTok action occurred.
- Remaining blocker: the local ledger must be persisted before the Telegram request and after its outcome, with serialized workflow runs, so a fresh runner cannot lose the reservation. Until that workflow exists and is verified, cross-run duplicate prevention is incomplete and Telegram sending stays disabled.


## 2026-11-06 — Cross-run ledger persistence design

### Read-only audit
- Re-fetched the Pro status, development log, ledger, sender, caption preparer, orchestrator, and ledger/sender tests from `feature/quran-video-pro`.
- Confirmed there is currently no Pro-specific workflow in `.github/workflows`.
- Confirmed the repository currently has no `content/pro` directory or reviewed Pro dua/dhikr manifest library; the existing content files are Quran-oriented and are not valid Pro content.
- Rechecked production: `src/pro_delivery_ledger.py` and `tests/test_pro_delivery_ledger.py` remain absent from `feature/telegram-review-notifications`.
- No code tests were run; no Actions workflow, render, Telegram API call, or publishing action occurred.

### Design committed
- Added `PRO_LEDGER_PERSISTENCE_DESIGN.md` in commit `e3c50a6c66a13d23c753cb9c7f975c1b633accd5`.
- Selected a branch-committed JSON ledger on the Pro branch, protected by a single fixed GitHub Actions concurrency group.
- Delivery must use a two-phase protocol: reserve and push the ledger before Telegram; send once only after the reservation commit is confirmed; then persist delivered/uncertain outcome. If the final persistence fails, the previously committed reservation remains a duplicate-send block.
- Artifact-only persistence was rejected for now because immutable uploads, retention expiry, discovery/order, and concurrency make it less straightforward to audit.
- The design explicitly prohibits Git data API shortcuts; persistence must use normal checkout/commit/push subject to branch protections.

### Current blockers and next implementation steps
1. Implement sender support for a pre-existing reservation bound to the current workflow run ID.
2. Implement a narrow workflow persistence helper that only commits the ledger file and fails closed on wrong branch or push failure.
3. Add a dormant `workflow_dispatch`-only Pro workflow with exact branch guard, fixed concurrency, and minimal permissions. It must not include schedules or production secrets.
4. Add offline tests for reservation persistence failure, wrong reservation/run ID, uncertain result, confirmed delivery, post-send persistence failure, and duplicate blocking after reload.
5. Create and human-review verified dua/dhikr manifests before any delivery workflow can be used.

### Safety
- The design file is documentation, not an enabled delivery path.
- No Pro workflow was created or dispatched in this step.
- No Pro content was fabricated; no Telegram delivery occurred.
- Production Quran branch, production workflow, Cron, secrets, and Telegram route remain untouched.


## 2026-11-06 — Pre-persisted reservation sender mode

### Implemented on Pro only
- Added `assert_reserved_for_run()` to `src/pro_delivery_ledger.py`. It requires an existing `reserved` entry with matching manifest ID, content type, and workflow run ID.
- Updated `src/send_pro_telegram.py` with an explicit `--reservation-persisted` mode. In that mode it verifies the pre-existing reservation and does not create a new local reservation before Telegram. The default local mode remains for isolated sender tests.
- Added tests for reservation ownership/type validation, refusal before Telegram on a mismatched run, and successful use of a matching pre-persisted reservation.

### Commits
- Ledger assertion helper: `ece3e90accf93ee3e00ab8f4c14612a850eb90db`
- Sender pre-persisted mode: `49d3b98e5793967761296b2168395c804bb88183`
- Ledger tests: `921bc92fb516aae13b53873965016ce77a29d8b1`
- Sender tests: `c6ceb17c9daf76e4e1153484004754cca8f05cef`

### Explicit-ref verification
- Re-fetched the four changed files from `feature/quran-video-pro`; current blob SHAs: ledger `6466ba9faee6c8c76dec47a216aac9818f4f5314`, sender `85667384593044f4fecb8e3306c2c1199edcf35d`, ledger tests `3002c1b102acc4391d71cd0513561f86c6d5347c`, sender tests `11357c3ae85e74d65e29b37e67133d77f453b151`.
- Re-fetched the persistence design and both project docs from the Pro branch.
- Rechecked production: both ledger source and ledger test remain absent from `feature/telegram-review-notifications`.

### Not yet validated / remaining
- Tests have NOT been executed. No workflow helper or Pro workflow has been added yet.
- The pre-persisted mode is only a code capability; no actual branch reservation commit/push protocol is wired in.
- No Actions workflow was dispatched, no render or Telegram request occurred, and no secrets were read or changed.
- Next: add and test a narrow helper that commits only `data/pro_delivery_ledger.json` on the exact Pro branch, then add the dormant manual-only workflow after reviewing the helper and its failure behavior.


## 2026-11-06 — Ledger-only Git persistence helper

### Implemented on Pro only
- Added `src/persist_pro_ledger.py`.
- The helper rejects any branch other than the exact `feature/quran-video-pro` branch.
- It refuses to run when unrelated staged changes already exist, stages only `data/pro_delivery_ledger.json`, verifies that this is the sole staged path, then uses normal `git commit` and `git push` to the exact Pro branch.
- It fails closed on any Git command failure. It does not use Git data/tree/ref APIs and does not touch other paths.
- Added `tests/test_persist_pro_ledger.py` for wrong-branch refusal, pre-existing staged-change refusal, ledger-only commit/push, and unexpected staged-path refusal.

### Commits
- Persistence helper: `8bc5ea2d2eaf7ca4b339cb755b06f959d2e68860`
- Persistence helper tests: `04f7dddb0055f28f47ac522930dd2bde60139766`

### Validation and limits
- Source files were created on `feature/quran-video-pro`; tests have NOT been executed.
- The helper is not yet called by a GitHub Actions workflow. It assumes the workflow checks out the exact branch, configures a commit identity, and grants only the required contents write permission.
- The workflow must still serialize runs and execute reserve -> persist -> send with `--reservation-persisted` -> persist outcome. No Telegram call may happen if the first persistence push fails.
- No Pro workflow was created or dispatched; no render or Telegram request occurred; no secrets were read or changed.
- Production Quran branch and workflow remain untouched.

### Next
- Inspect the new helper and tests by explicit-ref fetch, then create the dormant manual-only workflow with exact branch guard, fixed concurrency, and no schedule. Keep it undispatched until content is reviewed and the user explicitly approves a run.


## 2026-11-06 — Manual-only Pro safety test workflow

### Sender correction
- Explicit source inspection found the prior sender edit had literal escaped newline text and did not expose the CLI flag correctly.
- Fixed `src/send_pro_telegram.py` in commit `a9d5d1a242e653d123fca53eaef4b0b64231287f`: `--reservation-persisted` is now a real CLI flag; in that mode the sender validates the already-persisted reservation and does not create another reservation locally.
- This correction was source-verified from the Pro branch. No Telegram call was made.

### Workflow added
- Added `.github/workflows/pro-safety-tests-manual.yml` in commit `2ab7b6da74210b71240834ebf25ff80532ef84c3`.
- Trigger: `workflow_dispatch` only. No schedule, push, pull-request, or Telegram delivery.
- Exact branch guard requires `refs/heads/feature/quran-video-pro`.
- Fixed concurrency group with `cancel-in-progress: false`.
- Permissions are read-only (`contents: read`); checkout credentials are not persisted.
- Runs only the Pro ledger, sender, and persistence-helper offline unit-test files. No secrets, rendering, external API calls, or Telegram sender invocation are configured.

### Safety / validation status
- Workflow file was created and source-verified, but NOT dispatched. Therefore no test result is claimed.
- No delivery workflow exists. This is only a manual offline test workflow.
- The delivery workflow remains blocked until reviewed content manifests exist and the two-phase persistence/send/persistence sequence is fully integrated and tested.
- No Telegram secret was read or changed; no render, Telegram API request, or TikTok publish occurred.
- Production Quran branch/workflow/Cron/bot route remain untouched.


## 2026-11-06 — Sender and persistence failure-boundary test expansion

### Implemented on Pro only
- Expanded `tests/test_send_pro_telegram.py`:
  - A sender invocation using `--reservation-persisted` now has an explicit test proving that a missing pre-persisted reservation is rejected before `urlopen` (no Telegram request).
  - Added a test proving an ambiguous timeout from the pre-persisted path changes the local reservation to `uncertain`.
- Expanded `tests/test_persist_pro_ledger.py`:
  - Added a push-rejection test proving that a remote persistence failure raises an error and is not reported as a successful persistence.
  - The test also verifies that the failed push is the final Git operation; no later operation can proceed to the sender in a correctly fail-fast workflow.

### Commits
- Sender failure-boundary tests: `a9dcc3129e80e20605a5d858627a0827459e2f1d`
- Persistence push-failure test: `927f0b1c0f5f49bba02bba6f228b186f6c245c9f`

### Validation and safety
- Both test files were fetched again from the exact Pro branch after their commits.
- Tests have NOT been executed; these are added assertions, not passing test results.
- No workflow was dispatched. No render, Telegram API request, or TikTok publish occurred.
- No production branch, main branch, Cron, secrets, or original bot route was changed.

### Remaining integration gap
- The workflow-level guarantee is still not implemented: the first ledger push must complete successfully before the sender step is reachable, and the post-send ledger state must be pushed even when the sender exits with an ambiguous error.
- The delivery workflow remains intentionally absent because there is no reviewed Pro content library. The manual-only workflow is still test-only.


## 2026-11-06 — Two-phase Pro delivery cycle added (not activated)

### Implemented on Pro only
- Added `src/pro_delivery_cycle.py` to coordinate the two-phase sequence:
  1. Read the stable manifest ID/type from the Telegram caption payload.
  2. Create the local `reserved` ledger entry.
  3. Call the ledger-only Git persistence helper; if this fails, the sender is never called.
  4. Call the sender only with `reservation_persisted=True`, which verifies the reservation is bound to this workflow run.
  5. Persist the sender's resulting `delivered` or `uncertain` state.
- If the sender raises after an ambiguous Telegram request, the cycle attempts to persist the `uncertain` state before propagating the error.
- If final persistence fails, the first already-persisted `reserved` entry remains the remote duplicate-send block; no retry is attempted.
- Added `tests/test_pro_delivery_cycle.py` for first-push failure preventing send, uncertain outcome persistence, successful persist/send/persist ordering, and final-push failure behavior.
- Added the new cycle tests to the existing manual-only offline safety-test workflow.
- Corrected the staged-path test fixture so its simulated Git output contains an actual newline.

### Commits
- Two-phase cycle implementation: `e34b1d087b009e010809afd92a96cd2f791b2f72`
- Cycle failure-boundary tests: `82d66a045cb8afd3a293960df3640c485d741ea3`
- Manual safety suite includes cycle tests: `fda5a62f89636b004e0bce77980e3cb9f26dc7fb`
- Corrected persistence test fixture: `5bf69ce275b077a04ba92097b5fad2ee80c7d0ec`

### Validation and safety
- Source and test files have been committed on `feature/quran-video-pro`.
- Tests have NOT been executed; the manual safety workflow has NOT been dispatched.
- The cycle is not connected to a delivery workflow and has not been run. No Pro content was rendered and no Telegram request or TikTok publish occurred.
- No production branch, `main`, production workflow, Cron, secrets, or original bot route was changed.

### Remaining
- Review the new cycle and test files for correctness, then execute the offline test suite only after explicit approval.
- Before any delivery workflow is created or enabled, obtain a trustworthy, source-verified, human-reviewed Pro dua/dhikr content library. No such library currently exists.


### Additional fail-closed hardening — 2026-11-06
- The delivery cycle now verifies that its ledger path is exactly the Pro branch-committed file under the supplied repository checkout. A different/local-only ledger path is rejected before reservation or send.
- The cycle now requires the persistence helper to return an explicit `True` after the reservation push. A no-op/false result blocks Telegram just like a push exception.
- It likewise requires explicit confirmation that the outcome state was committed/pushed. A false result is treated as persistence failure; the already-pushed reservation remains the remote duplicate block.
- Added tests for false/no-op first persistence preventing sender invocation and for rejecting a ledger path outside the persisted Pro checkout.
- Commits: hardening `efc65604523b0c3579fd8b38c3a8a927a8a3a7a8`; tests `885db308e84ec7cd97798bb41405ed377e2cb8a1`.
- These tests remain unexecuted. No workflow dispatch, render, Telegram request, or TikTok publish occurred.


### Ambiguous-outcome persistence failure test — 2026-11-06
- Added a delivery-cycle test for the case where Telegram outcome is ambiguous, the sender marks the local entry `uncertain`, and the follow-up Git push fails.
- The test asserts the cycle reports a blocking persistence error and does not continue/retry. The pre-send remote reservation remains the duplicate guard.
- Commit: `a34fcfffba92dd7bcb1f237487c9793c2596dfe8`.
- Test remains unexecuted; no workflow dispatch or external delivery action occurred.


## 2026-11-06 — Static review of Pro delivery boundary

### Review performed (read-only)
- Re-fetched and inspected the Pro-only delivery coordinator, Git ledger persistence helper, Telegram sender, and their offline tests from `feature/quran-video-pro`.
- Confirmed the coordinator checks the exact Pro ledger path, reserves before persistence, refuses to call Telegram unless the first persistence helper returns explicit `True`, and persists the resulting state after the sender returns or raises.
- Confirmed the persistence helper rejects the wrong branch and pre-existing staged changes, stages only `data/pro_delivery_ledger.json`, verifies the staged path set, and pushes only to `feature/quran-video-pro` without force-push.
- Confirmed the sender requires a matching persisted reservation in coordinator mode, has no automatic retry, enforces the 50 MiB MP4 cap, and only marks delivery after a positive Telegram `message_id`.
- Reviewed the failure-boundary tests for first-push rejection/no-op, ambiguous sender outcomes, failed outcome persistence, successful persist/send/persist ordering, wrong-branch refusal, unrelated staged files, and push rejection.

### Review result and limits
- No immediate static-code defect was identified in the reviewed two-phase safety boundary; this is a source review only, not runtime validation.
- The workflow-level integration is still absent. Therefore this review does not mean automated Pro delivery is enabled or ready.
- Offline unit tests remain NOT RUN. The manual-only safety workflow remains undispatched. No render, Telegram request, or TikTok publish occurred.
- No files on `main` or `feature/telegram-review-notifications` were changed during this review.

### Next safe step
- Await explicit approval before running the offline Pro unit-test suite. Keep delivery workflow creation blocked until reviewed dua/dhikr manifests exist and the workflow integration is separately reviewed.


## 2026-11-06 — Pro content-validation and renderer boundary review

### Read-only review
- Re-fetched and inspected `src/validate_content_manifest.py`, `src/render_dua_video.py`, and `src/pro_orchestrator.py` from the exact Pro branch.
- Confirmed the Pro orchestrator accepts only `dua` or `dhikr`, requires rotation-approved manifests, runs the shared validator, requires explicit positive item durations, applies the 40-second hard cap, and defaults to preflight; rendering requires the explicit `--render` flag.
- Confirmed the dedicated renderer independently rejects non-dua/dhikr content, validates the manifest before rendering, requires an HTTPS background URL that has both approval and user approval metadata, and checks declared audio duration instead of silently padding or trimming it.
- Confirmed the shared validator requires each dua/dhikr item to carry a stable unique ID, exact non-empty Arabic text, named HTTPS source, precise source reference, `verification_status: verified`, `human_reviewed: true`, and an explicit item classification. Prophetic duas require a non-empty hadith-grading field.

### Important limitation recorded
- These checks validate required metadata and workflow gates; they do not independently authenticate the Arabic wording, source interpretation, hadith grading, or media reuse rights. Those remain human/source-review responsibilities.
- No reviewed Pro content library was found or added. Production content selection and all real rendering/delivery remain blocked until source-by-source review is completed.
- No code tests were run, no render or workflow was started, and no Telegram/TikTok action occurred.

### Documentation correction
- Updated this log's title to the current Dua & Adhkar Pro scope. Earlier Quran-oriented entries remain as historical records only; the current scope pivot entry governs this branch.
- No production branch, `main`, production workflow, Cron, secrets, or original Telegram route was changed.


## 2026-11-06 — Pro content intake gate documented

### Implemented on Pro only
- Added `content/pro/README.md` to establish the dedicated Dua & Adhkar Pro content intake and human-review process.
- The directory is explicitly reserved for dua/dhikr manifests; Quran production manifests in other directories are not Pro content.
- Documented the required exact Arabic check, named HTTPS source and precise reference, content classification, verification and human-review flags, hadith grading for prophetic duas, separate media-rights review, and the 40-second duration ceiling.
- Explicitly prohibited guessed or AI-invented religious wording and marking items verified merely to pass validation.
- The README is a review gate, not an approved content manifest. No religious content was added.

### Commit
- Content review guide: `d0f2215287c106928dd2c9aedd11cba6f8d8c1b5`.

### Validation and safety
- The new file was created on `feature/quran-video-pro` only.
- No unit tests were run; no manifest was approved; no preflight, render, Actions workflow, Telegram request, or TikTok publish occurred.
- The delivery workflow remains absent and Telegram delivery remains disabled.
- Production Quran branch, `main`, Cron, secrets, and original Telegram route were not changed.

### Next
1. Review and run the offline Pro safety tests only after explicit user approval.
2. Populate `content/pro` only with individually source-checked and human-reviewed manifests.
3. Do not create or enable a delivery workflow until the content library exists and the two-phase workflow integration has been separately reviewed.


## 2026-11-06 — Pro content-source research started

### Research performed
- Began the content-library phase after the successful offline Pro safety workflow run recorded above.
- Identified Quran.com / Quran Foundation developer documentation as the primary starting point for Qur'anic verse text and exact verse references.
- Identified Sunnah.com as a searchable reader across named hadith collections for locating exact Prophetic dua/dhikr narrations.
- Read Sunnah.com's own About page and recorded its limitations: it is a research resource, not a fatwa service; Arabic and English numbering may differ; and grading metadata coverage is not uniform across collections.
- Third-party compilations and APIs may help discover candidates but will not be treated as the primary evidence or as proof of authenticity.

### Review policy for each candidate
- Open and compare the exact Arabic against the cited Qur'anic verse or full hadith narration.
- Record source collection, book/chapter where available, reference and numbering scheme, narrator, and grade together with the grading authority/status.
- Do not infer a grade from a search result, a website badge without provenance, or a secondary compilation.
- Preserve the exact source wording; do not paraphrase religious Arabic or combine separate narrations into one item.
- Require human review before marking any item verified or adding it to the production manifest.

### Current outcome and safety
- This is source-discovery research only. No specific dua/dhikr has been selected, authenticated, or approved.
- No religious text or manifest was added; no code or workflow was changed.
- No tests, render, Telegram request, or TikTok publishing occurred in this step.
- Next: define the content review record/schema, then assess individual candidates one by one against the full primary source and grading evidence.


## 2026-11-06 — Per-item Pro content review template

### Implemented on Pro only
- Added `content/pro/REVIEW_TEMPLATE.md` as a structured human-review worksheet.
- Captures the exact Arabic and primary source, precise reference and numbering scheme, narrator, hadith grading authority/evidence, context/classification, human-review decision, separate audio/background rights checks, duration, and readiness status.
- Explicitly states that this worksheet is not a production manifest, does not set validator approval flags, and does not authorize render or delivery.

### Commit and validation
- Template commit: `372351501a60139963091b43a1d044ca6fe8277e`.
- File created on `feature/quran-video-pro` only. No religious content was added.
- No tests or render were run; no Telegram request or TikTok publishing occurred.
- Next: use the template to evaluate individual candidates from the full primary source. Keep any unresolved candidate blocked.
