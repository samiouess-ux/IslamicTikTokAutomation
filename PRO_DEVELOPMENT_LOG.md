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


## 2026-11-06 — First Qur'anic dua candidate located (not approved)
- Located a candidate supplication at Qur'an 2:201 (Surah Al-Baqarah) and opened its Quran.com primary-source page: https://quran.com/2/201 .
- The page shows the Arabic text, exact verse reference, English meaning, and nearby verses/context.
- Kept the item at `candidate` status only. No Arabic text was copied into a production manifest, no validator approval flags were set, and no human approval is claimed.
- Next review must compare the complete Arabic verse exactly against the source page, record its context and reference using the review template, and obtain human review. Media rights remain a separate later gate.
- No render, Telegram request, or TikTok publishing occurred.


## 2026-11-06 — Initial Qur'anic dua and morning/evening dhikr source comparison

### Research and source comparison
- Opened Quran.com Al-Baqarah 2:201 and checked the displayed Arabic verse, exact reference, and adjacent context (2:200–202).
- Located the Abu Hurairah morning/evening supplication in Sunan Abi Dawud 5068 and Jami' at-Tirmidhi 3391, then compared it with Riyad as-Salihin 1453.
- Found material wording differences between the collections/compilation. The exact variants are recorded independently in `content/pro/CANDIDATE_RESEARCH_001.md`; no blended wording is permitted.
- Recorded source-specific grading statements separately: Tirmidhi's page reports Abu 'Isa's grade as hasan; the Abu Dawud listing displays Al-Albani's sahih grade. No claim of unanimous grading is made.

### Commit and current status
- Candidate comparison note: `a5a8c7c138371b6a44e19a224aff96963f64192a`.
- Both entries remain research candidates, not human-approved production content. Exact-text/context review for the Qur'anic verse and source/variant/grading review for the hadith are still pending.
- No production manifest, render, Telegram delivery, or TikTok publishing occurred. Media rights have not been reviewed.
- Next: human reviewer to choose one exact hadith collection/version (or reject the candidate), then complete the review worksheet without merging variants.


## 2026-11-06 — Follow-up source verification and correction

Re-opened Quran.com Al-Baqarah 2:201 and the exact hadith pages for Abu Dawud 5068, Tirmidhi 3391, and Riyad as-Salihin 1453. Confirmed the displayed Arabic text and source references. A grading metadata nuance was corrected in the candidate research note: Tirmidhi 3391's Arabic matn contains Abu 'Isa's statement that the hadith is hasan, while the separate Sunnah.com Grade field displays Sahih (Darussalam). Those statements are now kept as separate attributions. Riyad as-Salihin 1453 also records its own wording and attribution and must not be used to silently normalize either collection's matn.

The candidate remains unapproved pending human review and an explicit choice of one source/version. No manifest, render, Telegram send, or TikTok publication occurred.


## 2026-11-06 — Candidate PD-002: Sayyid al-Istighfar

Opened Sahih al-Bukhari 6306 directly. The source page identifies the report as narrated by Shaddad bin Aws, gives the Arabic matn and the day/night recitation context, and lists Book 80, Hadith 3. Recorded this as a separate source-checked candidate in `content/pro/CANDIDATE_RESEARCH_001.md`. The supplication is not yet approved: human exact-text/context review, media-rights review, and duration suitability under the 40-second cap remain open. It must not be truncated merely to meet the cap.

No production manifest, render, Telegram delivery, or TikTok publishing occurred.


## 2026-11-06 — Media rights and user's Telegram text-review decision

### Media rights baseline
Added `content/pro/MEDIA_RIGHTS_POLICY.md`. Pexels and Pixabay may be used as discovery sources for background visuals, but their general licenses do not automatically clear every depicted person, logo, artwork, or property. Each exact downloaded asset needs a retained URL, creator, download date, license evidence, intended use, and third-party-rights check. Audio recordings need explicit recording-specific permission for editing, video synchronization, social posting, and monetization if applicable. No recording is pre-approved. No music.

### User's review workflow decision
The user explicitly stated that they will verify the Arabic texts when preview videos arrive on Telegram and tell us corrections/approval. Record this as the human text-review gate at the Telegram preview stage. It does not mean any current candidate is approved; candidates remain unapproved until the user reviews the delivered preview. Do not claim a Telegram preview delivery has occurred. The delivery cycle is still not wired into a workflow.

No render, Telegram delivery, or TikTok publication occurred in this step.


## 2026-11-06 — Code inspection: preview-stage human review mismatch

Inspected `src/pro_orchestrator.py`, `src/render_dua_video.py`, `src/validate_content_manifest.py`, and `content/pro/README.md`. The validator currently rejects any dua/dhikr item unless `human_reviewed: true`; the orchestrator validates before rendering. This conflicts with the user's explicit desired process: receive the first Arabic-text preview in private Telegram, inspect it personally, then report corrections/approval.

### Required safe design (not implemented yet)
- Introduce explicit content lifecycle states such as `candidate_preview` and `production_approved`.
- Permit only a source-cited, rights-cleared, preview-only candidate through the preview render/send path; it must be clearly marked as a private review preview and must not be eligible for production rotation or public posting.
- Keep production manifests strict: user text approval/corrections recorded, required media rights checks complete, and normal rotation/production approval only after the Telegram review step.
- Add negative tests proving candidate previews cannot pass as production manifests and cannot enter TikTok/publication paths.
- Wire the preview delivery separately from production delivery; never silently relax the existing production validator.

No code changed in this step. No render, Telegram send, or TikTok publication occurred. This is now a documented blocker and next implementation task.


## 2026-11-06 — Corrected stale duration test

Code inspection found a mismatch: `src/render_dua_video.py` defines both target and hard maximum as 40 seconds, while `tests/test_render_dua_video.py` still asserted 60/65 seconds. Updated the regression to assert 40/40 and reject a 41-second item. Commit: `8ae136c9434fe822786950a287a8bb495a52cf42`.

No renderer code changed. Offline tests have not yet been rerun after this commit. No render or Telegram send occurred.


## 2026-11-06 — Implemented isolated candidate preview path

### Code changes
- `src/validate_content_manifest.py`: introduced an explicit `allow_candidate_preview` argument. Only a manifest marked both `candidate_preview` and `preview_only` can use the opt-in path. Pending human review is allowed only there; the production/default path still rejects it. Production-approved manifests cannot be marked preview-only.
- `src/pro_orchestrator.py`: added explicit single-manifest preview preflight and local render options. Preview candidates bypass rotation discovery but must not be rotation-approved. They retain source verification, media approval, item timing, stable ID, and 40-second checks. Local output goes only to `output/pro_preview`.
- `src/render_dua_video.py`: added `--preview-only`; candidate manifests are rejected by the normal render invocation, and production manifests are rejected when the preview flag is used.
- Added regression tests for validator gating, production/preview separation, rotation exclusion, and renderer flag requirements.

### Commits
- Validator: `6340df9520ff8b494a057edb61d9946332a8ae79`
- Renderer: `7912b6878d086193c97dc580185f5e1fd2654bce`
- Orchestrator: `62ba4b3292ef3fce39b6cbbe60c2d85e54a1d9b2`
- Validator tests: `81ed08db8cc14102d26d042b5a60ace054282d45`
- Orchestrator tests: `704312d80d9f878cf0b7bb58098795d72aedd53d`
- Preview CLI fix: `7ea0169dcaf3cb683e78e33cc552245f9b8dafc6`
- Renderer tests: `f66afa9eabc1784280c8cf02971e8c47ed3d6e58`

### Safety status
- This is local preview-only capability, not Telegram preview delivery. No private Telegram sender/workflow has been added or enabled in this change.
- No actual render, Telegram API call, TikTok publish, rotation-history update, or production workflow execution occurred.
- Tests have not been run after these changes. The earlier offline test workflow success predates this implementation.
- All changes are confined to `feature/quran-video-pro`.

### Next
1. Review and execute the offline test suite for the new preview lifecycle.
2. Implement a separate private Telegram preview route with explicit preview labels and no production-ledger/rotation side effects; keep it uninvoked until the user explicitly authorizes an actual send.
3. Add negative tests proving preview candidates cannot enter production rotation/delivery and production-approved manifests cannot be demoted into preview mode.


## 2026-11-06 — Implemented isolated candidate preview path

- Validator: explicit allow_candidate_preview opt-in. Only candidate_preview plus preview_only=true may bypass pending human review; the default production path remains strict.
- Orchestrator: explicit single-manifest preview preflight and local render options. Candidate previews are excluded from rotation and must pass source, media, timing, stable-ID, and 40-second gates.
- Renderer: --preview-only required for candidate manifests; production manifests cannot use that flag.
- Added validator, orchestrator, and renderer regression tests.
- Commits: validator 6340df9; renderer 7912b68; orchestrator 62ba4b3; validator tests 81ed08d; orchestrator tests 704312d; CLI fix 7ea0169; renderer tests f66afa9.
- This does not yet deliver previews to Telegram. No render, Telegram request, TikTok publish, history update, or production workflow run occurred.
- Tests have not been run after these changes. Earlier manual offline workflow success predates this implementation.
- Next: run offline tests, then implement a separate private Telegram preview route with explicit authorization before any real send.


## 2026-11-06 — Manual offline workflow updated to cover candidate preview tests

### Review finding
The Pro manual workflow `.github/workflows/pro-safety-tests-manual.yml` still executed only the original four delivery-ledger/sender/persistence/cycle test modules. The recently added candidate-preview validator, orchestrator, and renderer tests were not included, so a green run would not have verified the new preview lifecycle.

### Change
- Expanded the manual-only workflow to run all seven Pro offline test modules:
  - `test_pro_delivery_ledger.py`
  - `test_send_pro_telegram.py`
  - `test_persist_pro_ledger.py`
  - `test_pro_delivery_cycle.py`
  - `test_validate_content_manifest.py`
  - `test_pro_orchestrator.py`
  - `test_render_dua_video.py`
- Preserved the exact `feature/quran-video-pro` branch guard, read-only `contents: read` permission, and manual-only `workflow_dispatch` trigger.
- No Telegram token/secret, rendering command, network delivery, TikTok publication, or production workflow was added.

### Commit and verification
- Workflow update commit: `56476b87d25c7da651f51819cad64cb983179bbe`.
- Status record commit: `3554439d0bdbd3a5fb45458a8a56f640268eb79b`.
- Re-fetched the workflow from `feature/quran-video-pro` and verified all seven test commands, the branch guard, and read-only permission.
- The workflow has NOT been dispatched; tests have NOT run. The available GitHub connector actions in this session do not include workflow dispatch, so no test result is claimed.

### Safety / next step
- No local render, Telegram request, TikTok publish, or production delivery occurred.
- No change was made to `main` or `feature/telegram-review-notifications`.
- Next: run the expanded offline workflow through a supported manual dispatch route. Continue Telegram preview sender implementation only after test results are available, and keep any real send behind a separate explicit user authorization.


## 2026-11-06 — Isolated Telegram candidate-preview sender added
- Added `src/send_pro_preview_telegram.py`, a separate sender for a single candidate-preview MP4. It accepts only dua/dhikr manifests marked `candidate_preview` and `preview_only: true`, rejects rotation-approved candidates, and reuses the strict preview validator.
- Requires an explicit `--confirm-preview-send` flag, a separately named Pro preview bot token and private numeric chat ID, and a `PREVIEW-ONLY-*.mp4` file. Caption is clearly marked “PREVIEW — NOT APPROVED FOR POSTING”.
- No automatic retries. A transport/response ambiguity is not retried. This sender does not touch the production delivery ledger or rotation history and never publishes to TikTok.
- Added `tests/test_send_pro_preview_telegram.py` covering confirmation gate, candidate-only gate, private destination/file checks, caption labeling, one-call send behavior, isolation from production state, and no automatic retry.
- Expanded `.github/workflows/pro-safety-tests-manual.yml` to include the new preview-sender test module. It now invokes eight focused offline test modules.
- Commits: sender `80e290cf2d77edb172d6794bdb0f2c38cf60d5bd`; tests `4997fe46c0695f1eb2144c0d2f1d5c4f6a04a07a`; workflow `06fda285fd198382c6cd3df4ee018eea66bfb034`.
- This is implementation only. The sender was not invoked, no token/chat secret was added, no MP4 was rendered, no Telegram request was made, and no TikTok post occurred. Tests have not been executed; the workflow has not been dispatched.
- Next: re-fetch and statically review the sender/tests/workflow, update the durable status/log, then obtain a supported manual workflow-dispatch path for offline tests. Keep actual Telegram preview delivery disabled until the user explicitly authorizes a specific send.


## 2026-11-06 — Isolated preview sender hardening
- Added `src/send_pro_preview_telegram.py`: candidate-preview only; explicit `--confirm-preview-send`; separate Pro preview token/chat variables; positive numeric private-chat ID; preview-only MP4; warning caption `PREVIEW — NOT APPROVED FOR POSTING`; one request, no automatic retry; no production ledger or rotation-history use.
- Added exact manifest/filename binding and safe 1–80 character preview IDs to prevent path traversal or mismatched files.
- Added offline sender tests and included them in the manual workflow (eight test modules total). Static re-fetch verified exact Pro branch guard, read-only contents permission, and no secrets or delivery/publish steps.
- Commits: sender 80e290cf2d77edb172d6794bdb0f2c38cf60d5bd; tests 4997fe46c0695f1eb2144c0d2f1d5c4f6a04a07a; workflow 06fda285fd198382c6cd3df4ee018eea66bfb034; safe ID 9a8577fae641c5fa64369293594bf9dc3d0cc6e5; exact file binding a687af0cef089dc2265570061f64c5bc6c11bd3f; tests 25ee33f4272aee847187a3550c6b9d19cffb8d5f and 141a630af57a840abe49e99897f6e3c8e6182042.
- Static re-fetch only: tests NOT RUN; workflow NOT DISPATCHED. No render, Telegram request, secrets, TikTok publish, or production-branch changes.
- Next: obtain a supported manual dispatch path, run offline tests, then continue with candidate manifest/assets. Actual preview sending still requires explicit authorization for that exact send.


## 2026-11-06 — Read-only review of Pro safety tests
### Files reviewed
- `tests/test_send_pro_preview_telegram.py`
- `tests/test_pro_delivery_cycle.py`
- `tests/test_persist_pro_ledger.py`
- `.github/workflows/pro-safety-tests-manual.yml`
- Current `PRO_PROJECT_STATUS.md` and recent implementation history.

### Review findings
- Preview sender tests assert no network call without explicit confirmation; reject production/rotation-approved manifests; reject non-preview or mismatched filenames; require a positive numeric destination; check the not-approved-for-posting caption; and verify one request/no retry plus no production ledger or rotation-history side effects.
- Delivery-cycle tests exercise first-persistence failure/no-op, ambiguous sender outcomes, uncertain-state persistence failure, correct persist/send/persist order, final-persistence failure, and rejection of an out-of-checkout ledger path.
- Persistence-helper tests exercise exact Pro-branch enforcement, refusal of pre-staged or unrelated files, ledger-only staging/commit/push, and fail-closed behavior on remote push failure.
- The manual workflow remains manual-only, guarded to `refs/heads/feature/quran-video-pro`, with `contents: read`, and invokes eight offline test modules. It contains no render/send/publish command; invoking the renderer's unit-test module is not a render.
- Static review did not establish an immediate defect. Follow-up hardening idea: the preview sender's positive numeric chat-ID check is a practical private-chat restriction, but the current test does not verify Telegram's returned `chat.type`; assess whether a preflight/type check is needed before enabling any real preview route.

### Validation and change boundary
- These test files were inspected only; the expanded eight-suite workflow was NOT run or dispatched.
- Historical workflow run `42259731118` is still the confirmed successful run for the four original suites only. It must not be represented as a pass for the expanded eight-suite set.
- No code or workflow was modified in this review. No render, Telegram request, TikTok publication, secret/Cron change, or production/main change occurred. The original Quran engine remains untouched.

### Next
1. Continue static review of content validation, media-rights gates, and any future workflow integration.
2. Resolve the private-destination hardening question before authorizing a preview send.
3. Obtain explicit authorization before dispatching the expanded offline test workflow; actual Telegram sending remains a separate approval.


## 2026-11-06 — Read-only renderer, validator, and media-rights review

### Scope inspected
Re-fetched and inspected the current versions of:
- `src/render_dua_video.py` (blob `b23130dbe184cdb4ccdcc680bb95cec7d4388b41`)
- `src/validate_content_manifest.py` (blob `5146070fea6ab8ed65cd6d192e8a255472260ba1`)
- `src/pro_orchestrator.py` (blob `a76c75e72bdc030575652f9a76f105ee91865675`)
- `content/pro/MEDIA_RIGHTS_POLICY.md` (blob `70de3ebb9755ba20a7e77b3cd87d306955e75506`)

### Findings (not yet fixed)
1. **Approved background URL is not bound to the approved candidate.** The validator requires `background_candidate.direct_video_url` and approval flags on that candidate. The renderer then selects `approved_background_url` first when present, without checking equality with the candidate URL. A different HTTPS URL can pass the later URL syntax check and be downloaded. Required fix: validate exact URL binding and reject mismatch; add negative tests.
2. **Production manifest IDs lack the preview safe-ID constraint.** `build_preview_plan()` enforces a 1–80 character ASCII filename-component pattern. Normal `build_plan()` only requires a non-empty string, and `render_plan()` interpolates it into an output path. Required fix: use one shared strict ID validator for both paths and test slash/traversal-like IDs before rendering.
3. **Audio is checked globally, not synchronized per screen.** `build_slideshow()` assigns per-item display durations, while `validate_audio_duration()` compares only the whole audio file with the total duration. The renderer comment explicitly states audio is not synced per item. This is a multi-item correctness risk; it does not establish that a specific rendered file is wrong. Required fix: define an explicit per-item audio/timing contract or constrain the first release to a safe single-item audio arrangement, then test boundaries.
4. **Media-rights policy is stricter than manifest enforcement.** The policy requires exact asset page/ID, creator, platform, download date, license evidence, intended use/edits, and third-party-rights review. The current validator checks background candidate URLs and approval booleans but does not enforce that complete per-asset record. Required fix: add a structured rights record and fail closed when any required evidence is absent.

### Validation and safety boundary
- Static code review only. No code changes, test execution, workflow dispatch, render, Telegram request, or TikTok publication occurred.
- The expanded eight-suite offline workflow remains NOT RUN. The historical successful run `42259731118` covered only the four original suites and is not evidence for the expanded suite.
- No manifest or media asset was approved by this review. No candidate text/media has been cleared for rendering or delivery.
- All review remained on `feature/quran-video-pro`. `main` and `feature/telegram-review-notifications` were not touched; the original Quran production engine remains untouched.

### Documentation
- Updated `PRO_PROJECT_STATUS.md` with this review summary. Status documentation commit: `d6dffa48ecfe2f068c87c1847117371167f4aa25`.
- Next: close the four validation gaps with focused negative tests, then review candidate manifest/asset records. Any code change, test dispatch, render, or Telegram send still requires separate explicit approval.


## 2026-11-06 — Read-only regression-test coverage review
- Re-fetched `tests/test_render_dua_video.py` (blob `6b0e01359d667682bd1f11ff317607518a07fa41`) and `tests/test_pro_orchestrator.py` from `feature/quran-video-pro`; inspected them alongside the current renderer, validator, and orchestrator.
- Audio: existing tests cover total-file duration mismatch/fail-closed behavior and explicitly assert the renderer's documented limitation. They do not prove per-item audio-to-screen synchronization or a safe multi-item audio mapping.
- Background: no regression test was found that supplies a different `visual.approved_background_url` from `visual.background_candidate.direct_video_url` and expects rejection. The previously identified binding gap remains untested.
- Output identity: the orchestrator tests reject an unsafe ID on the candidate-preview path, but do not exercise an unsafe ID through normal production `build_plan()` / `render_plan()`. The production-path ID validation gap remains untested.
- Media rights: the inspected tests do not require the complete per-asset provenance record described by `content/pro/MEDIA_RIGHTS_POLICY.md`; current validation tests focus on metadata/approval flags. Full rights-evidence enforcement remains unproven.
- These are coverage gaps corresponding to the previously documented implementation gaps; they are not evidence that a specific rendered video was incorrect or that an asset was actually used without permission.
- Validation boundary: source/test inspection only. No tests executed, no workflow dispatched, no code or workflow changed, no render, Telegram request, or TikTok publication. No secrets, Cron, or delivery settings changed. All work stayed on `feature/quran-video-pro`; `main` and `feature/telegram-review-notifications` were not touched. The original Quran production engine remains untouched.
- Next: prepare focused negative/integration test cases for production IDs, approved-background URL binding, per-item audio timing, and required media-rights evidence. Implementation and test execution remain gated by separate explicit approval.

## 2026-11-06 — Read-only delivery preflight boundary review

### Files re-fetched and inspected
- src/pro_delivery_cycle.py (blob f84580d8b58cf3debc959946ff7284be5fb3734c)
- src/send_pro_telegram.py (blob 4d232e5fdeb947b977dc099ca610178beb01fd93)
- tests/test_pro_delivery_ledger.py
- tests/test_persist_pro_ledger.py
- .github/workflows/pro-safety-tests-manual.yml (blob a6516c54dccdbd93227a76d59e253dccaa5f7f26)

### Confirmed behavior and finding
- The cycle validates the ledger path, reads/parses caption JSON, validates manifest ID/content type/run ID, reserves the manifest locally, and persists the reservation before calling the sender. A failed or false first persistence result prevents the Telegram sender from being called.
- The sender validates configured token/chat values, run ID, MP4 existence/non-zero size/50 MiB cap, caption JSON and review-only flags, manifest ID, and content type before constructing and executing the Telegram request.
- These local sender validations occur before the sender's network-request try/except. If one fails after the cycle has already persisted the reservation, the cycle catches the exception and attempts a second persistence of the ledger as it stands. Because the sender has not transitioned the entry to uncertain, this generally leaves the already-persisted entry in reserved state, blocking reuse of that manifest even though no Telegram request was attempted.
- By contrast, exceptions inside the actual request/response boundary are handled by the sender by attempting to transition the reservation to uncertain; the cycle then persists that outcome. Local preflight failure is therefore distinct from an ambiguous Telegram outcome.
- Ledger tests cover duplicate blocking, run/type binding, message-ID requirements, uncertain reconciliation, and terminal delivered state. Persistence tests cover exact-branch restriction, staged-change refusal, ledger-only push, and push failure. The manual workflow is manual-only, exact-Pro-branch guarded, and read-only (contents: read); it lists eight offline test modules.
- Static search did not return a caller reference for run_delivery_cycle; that search result alone is insufficient to prove there is no caller elsewhere. The inspected workflow itself is a safety-test workflow, not a delivery workflow.

### Recommended follow-up (not implemented)
- Split local preflight validation from the transport attempt and run it before reserving/persisting, or introduce a distinct typed pre-send failure path that safely handles a reservation only when it is proven no Telegram request began.
- Add tests proving invalid/missing MP4, oversized MP4, invalid caption, and missing configuration do not cause a Telegram request and do not leave an unreconciled reservation blocking a safe retry. Keep transport timeout/ambiguous-response tests asserting uncertain and no automatic retry.
- Do not weaken duplicate protection or automatically release a reservation after a transport ambiguity.

### Validation and safety boundary
- Read-only source/test inspection only. No code or workflow changed; no tests executed or dispatched; no render, Telegram request, or TikTok publication occurred.
- No secrets, Cron, or delivery configuration changed. All inspection remained on feature/quran-video-pro; main and feature/telegram-review-notifications were not modified. The original Quran production engine remains untouched.
- The expanded eight-module safety suite remains NOT RUN. Historical run 42259731118 covers only the earlier four suites.

## 2026-11-06 — Existing Telegram bot reuse design (documentation only)
- User clarified that the existing Telegram bot is already connected to and working with the original Quran production engine. The Pro goal is to reuse that same bot and private review destination without changing or disturbing the original engine.
- Read-only inspection of the Pro branch found that the original Quran request workflow references the existing repository secrets `TG_BOT_TOKEN` and `TELEGRAM_CHAT_ID`, while the isolated Pro preview sender expects `PRO_PREVIEW_TG_BOT_TOKEN` and `PRO_PREVIEW_TELEGRAM_CHAT_ID` as environment variables.
- Proposed isolated mapping for a future Pro-only workflow:
  - `PRO_PREVIEW_TG_BOT_TOKEN: ${{ secrets.TG_BOT_TOKEN }}`
  - `PRO_PREVIEW_TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}`
- This would let the Pro preview sender consume the existing secret values under its own environment-variable names, without creating a second bot or changing the original workflow/secrets. The secret values themselves are not readable through this inspection, so their validity and actual Telegram delivery have not been tested.
- Proposed next integration: a separate manual-only workflow stored and run only on `feature/quran-video-pro`, with an exact Pro-branch guard and Pro-branch checkout. It would invoke only the candidate-preview sender, require an explicit per-send confirmation, accept only the exact `PREVIEW-ONLY-*.mp4` / candidate-manifest pairing, and remain preview-only. It must not call or modify the original Quran workflow, production orchestrator, ledger/rotation, or TikTok publishing.
- Status: **design proposal only — NOT IMPLEMENTED or tested**. No workflow was created or changed; no secrets were read, added, or changed; no workflow was dispatched; no render or Telegram request was made; no TikTok publication occurred.
- Scope protection: all inspection and documentation are confined to `feature/quran-video-pro`. `main`, `feature/telegram-review-notifications`, and the original production Quran engine remain untouched.
- Next: continue static review of the isolated Pro workflow design and its gates. Creating the workflow, dispatching it, rendering a candidate, and sending a Telegram preview each remain separate actions requiring the relevant explicit approval.


## 2026-11-06 — Read-only Telegram workflow integration gate review
- Re-fetched the Pro preview sender, Pro manual safety workflow, original Quran Telegram workflow, and Pro orchestrator from `feature/quran-video-pro`; source inspection only.
- Confirmed the preview sender requires the explicit `--confirm-preview-send` flag before making a request, validates candidate-only lifecycle and a preview warning caption, accepts only a `PREVIEW-ONLY-*.mp4` whose exact name matches the manifest ID/type, and makes one Telegram request without automatic retry.
- Confirmed the original Quran Telegram workflow is scoped to `feature/telegram-review-notifications` and uses the existing `TG_BOT_TOKEN` / `TELEGRAM_CHAT_ID` repository secrets. It was only read; no original workflow or production code was changed.
- Integration requirements for any future Pro-only workflow: manual `workflow_dispatch` only (no push/schedule trigger); exact `refs/heads/feature/quran-video-pro` guard before secret exposure; checkout that exact branch; map existing secrets only into the Pro sender's expected environment-variable names; no user-controlled arbitrary shell/path interpolation; constrain candidate manifest and output paths to the Pro preview locations; and require an explicit, default-false per-run send confirmation before invoking the sender.
- Keep preview creation and Telegram delivery as separate approval gates. A run that only prepares/renders a candidate must not send it. Failure-notification handlers must not send Telegram messages, because that would bypass the explicit preview-send gate.
- The sender's numeric positive chat-ID check is a local format restriction, not an independent Telegram API verification of chat type. Do not claim the destination was verified as a private chat until a separately approved test or reliable API check establishes that. The existing secret values are not visible to this inspection.
- Status: design review only. No code/workflow changes, tests, workflow dispatch, render, Telegram API request, secret access/change, TikTok publication, or production-branch activity occurred. Original Quran production engine remains untouched.
- Next: retain this gate design; do not create or run the Pro delivery workflow, render a preview, or send Telegram until each corresponding action is explicitly authorized.


## 2026-11-06 — Read-only preview integration and workflow-isolation review

### New static findings
- Re-fetched `.github/workflows/pro-safety-tests-manual.yml`, `src/send_pro_preview_telegram.py`, `tests/test_send_pro_preview_telegram.py`, `src/validate_content_manifest.py`, `.github/workflows/render-first-video.yml`, and `.github/workflows/render-manifest-video.yml` from the exact Pro branch.
- Preview test fixture gap reconfirmed: `tests/test_send_pro_preview_telegram.py::manifest()` omits the required top-level `source` object. The shared validator rejects that fixture before caption assertions, exact-filename mismatch assertions, mocked successful-send assertions, or mocked transport-timeout assertions can reach their intended code paths. This is a static control-flow inference only; tests were NOT executed and no runtime failure is claimed. Fix the fixture by supplying a valid source object; do not weaken the validator.
- The eight-suite manual safety workflow does include `test_send_pro_preview_telegram.py` and is manual-only, guarded to exact `refs/heads/feature/quran-video-pro`, checks out that branch with persisted credentials disabled, and has `contents: read`. It does not render or send Telegram; the test module is only invoked as an offline unit-test suite. The workflow was NOT dispatched.
- Workflow-isolation risk: `.github/workflows/render-first-video.yml` has `workflow_dispatch` without an exact-branch guard and a `push.paths` trigger without a branch filter. Its checkout is not pinned to a safe Pro-only branch, and its steps download Quran recitation/background assets and render an Ash-Sharh Quran video. It must be disabled from Pro execution by an exact branch guard and trigger scoping, or otherwise safely isolated, before Pro branch work can be considered workflow-safe. This is a configuration risk from static inspection, not evidence that it ran.
- `.github/workflows/render-manifest-video.yml` also exposes `workflow_dispatch` without an exact Pro branch guard and checks out the triggering ref by default; its steps validate Quran references and can render manifest videos. Treat it as another legacy mixed-scope workflow requiring exact branch protection or isolation before any Pro Actions use. It was NOT run.
- `.github/workflows/telegram-quran-request.yml` remains explicitly scoped to `feature/telegram-review-notifications` and checks out that same production branch. It was only read for comparison and was not changed.

### Recommended safe remediation order (not implemented)
1. Add exact Pro branch guards / trigger scoping to legacy Quran render workflows on the Pro branch so they cannot run from Pro. Keep the production branch's workflow untouched.
2. Correct the preview-test manifest fixture with the required top-level `source` object and add assertions that the validator accepts the intended candidate fixture before network mocks are evaluated.
3. Add a separate preview-only idempotency record for Pro candidate sends, preserving no-auto-retry behavior for uncertain transport outcomes; do not reuse the production ledger.
4. Add a dormant Pro-only manual preview workflow using the existing Telegram secrets mapped to the Pro sender's environment names, with explicit render/send confirmations and exact Pro branch guard. This remains a proposed design only.
5. Run the eight offline suites only after separate explicit approval; do not dispatch a render or Telegram workflow as part of test validation.

### Verification boundary
- Static inspection and documentation planning only. No code, workflow, manifest, secret, Cron, or bot configuration changed in this review.
- No tests were executed; the eight-suite workflow remains NOT RUN / NOT DISPATCHED.
- No render, Telegram request, TikTok publish, or workflow dispatch occurred.
- All inspected Pro files were read from `feature/quran-video-pro`. No change was made to `main` or `feature/telegram-review-notifications`; the original Quran production engine and its active Telegram route remain untouched.


## 2026-11-06 — Pro workflow inventory and production-isolation checkpoint
- Continued read-only inspection of workflow files on `feature/quran-video-pro`; no workflow was executed.
- High-risk finding: `.github/workflows/build-quran-audio-inventory.yml` has a manual trigger without an exact Pro-branch guard, grants `contents: write`, uses the original Telegram secrets, and its normal path reserves production Quran delivery state, commits data, rebases against `feature/telegram-review-notifications`, and pushes to that production branch. Its `test_only=true` path still does not suppress the Telegram send step. Dispatching this workflow from Pro could therefore send Telegram content and write to the original production branch. This is a static risk assessment; there is no evidence it has been dispatched from Pro.
- High-risk finding: `.github/workflows/render-manifest-video.yml` has manual dispatch without an exact Pro-branch guard, checks out the triggering ref by default, and can render Quran manifests; its ordinary delivery path can send through the original Telegram credentials. Do not dispatch it from Pro.
- Additional isolation findings: `.github/workflows/render-first-video.yml` has no exact branch guard and can render Quran content; `.github/workflows/render-second-ash-sharh-review.yml` can render Quran content although its Telegram-send step is currently disabled with `if: false`. Several legacy/manual Quran preparation and test workflows also lack exact branch guards or explicitly check out the production branch; keep them out of Pro execution.
- Production protection decision reaffirmed: the original `feature/telegram-review-notifications` branch, its Telegram workflow, existing bot credentials, and its scheduled delivery path are out of scope. Do not edit, disable, dispatch, or alter them. Pro-side isolation changes, if later approved, must be confined to `feature/quran-video-pro` and must not change production scheduling or delivery configuration.
- The existing Pro-to-original-bot integration remains a proposal only: a future Pro-only manual workflow may map existing repository secrets into the Pro sender's distinct environment-variable names. No secret values were read or changed; no Pro workflow was created or dispatched; no Telegram message was sent.
- Verification boundary: static source inspection and documentation only. No code/workflow implementation, tests, dispatch, render, Telegram request, TikTok publication, Cron change, or production-branch modification occurred. The eight-suite Pro safety workflow remains NOT RUN / NOT DISPATCHED.
- Next safe step: continue read-only inventory, then prepare a Pro-branch-only isolation patch for explicit review. Do not apply it, run Actions, render, or send until separately authorized.


## 2026-11-06 — Remaining workflow inventory (read-only)
- Continued static inspection of workflow files on `feature/quran-video-pro`; no workflow was executed.
- Lower-risk artifact/preparation workflows reviewed: `extract-ash-sharh-verses.yml`, `extract-ash-sharh.yml`, `prepare-ash-sharh-1-8-audio.yml`, and `fetch-pexels-background.yml`. They use `contents: read`, download/extract source media, use FFmpeg for concatenation/metadata/preview, and upload short-retention review artifacts. No Git push, Telegram secret, or Telegram API send step was found in these files. Their manual triggers lack an exact Pro-branch guard, so do not dispatch them from Pro; they are legacy Quran/media preparation workflows, not Pro production workflows.
- Read-only inspection workflows reviewed: `check-official-archive-connectivity.yml`, `inspect-official-audio.yml`, `inspect-verse-archive.yml`, and `inspect-verse-archive-link.yml`. They perform external HTTP/ZIP metadata inspection only, with `contents: read` (or no write permission declared); no Telegram or Git push step was found. Manual triggers are not branch-guarded, so still keep them out of routine Pro execution.
- `cloud-runner-check.yml` is a runner/FFmpeg environment check with `contents: read`; no Telegram or repository write step found. `official-audio-preflight-tests.yml` checks out the separate `fix/official-archive-preflight` branch and runs isolated tests; no Telegram or Git push step found.
- `review-background-candidates.yml` is manual-only and read-only but explicitly checks out `feature/telegram-review-notifications`, installs FFmpeg, and runs the original engine's background-review preparation script. Do not run it from Pro; it executes production-branch code even though it does not write to that branch.
- These lower-risk classifications do not override the previously recorded high-risk findings for `build-quran-audio-inventory.yml`, `render-manifest-video.yml`, and the unguarded legacy Quran render workflows. The complete workflow inventory still needs a final cross-check against every file in the directory before declaring isolation complete.
- No exact Pro-branch guards were added. No workflow, code, secret, Cron, or bot configuration was changed. No tests, Actions dispatch, render, Telegram request, or TikTok publish occurred. No production branch was touched; original Quran engine remains unchanged.
- Next: produce the consolidated allow/deny matrix and, only after explicit approval, make narrowly scoped Pro-branch-only workflow isolation changes. Do not disable or alter the production branch's active workflow or schedule.


## 2026-11-06 — Pro-only legacy workflow isolation applied
- User authorized implementation on the Pro branch. Added a job-level guard `if: github.ref != 'refs/heads/feature/quran-video-pro'` to the legacy Quran/media/test workflows so their jobs are skipped when a run is launched from the Pro branch. This preserves their existing behavior on their intended non-Pro refs while blocking accidental execution from Pro.
- Updated and re-fetched with matching guard: `.github/workflows/build-quran-audio-inventory.yml` (commit `72bd161e467b963959f09bc07ac26b75c57f581e`), `render-manifest-video.yml` (`11d83453e9820ef2a793a2500bbae0e46c4e3d7e`), `render-first-video.yml` (`d3db7548b680f56ebbf50ffc7082e9095b87a604`), `render-second-ash-sharh-review.yml` (`140db47e5fd618903f40beb94ae1333b5740d583`), `build-ash-sharh-short-pause-preview.yml` (`d492db87a69e320565573436d2c22cc236117956`), `check-official-archive-connectivity.yml` (`e1d6ed22307ec380b1e34ce7fefa39c30abf72ec`), `cloud-runner-check.yml` (`71c7e07f5a21280eae2ae6cada7f8f69a3610b71`), `extract-ash-sharh-verses.yml` (`07cc4b0a8970acf2619882fd989875134bdab2c8`), `extract-ash-sharh.yml` (`de1b5051b86931a31b74328d0818db9e0af904a2`), `fetch-pexels-background.yml` (`e965adbd0afd2096136171857f915d8312098a0e`), `inspect-verse-archive-link.yml` (`90f91e2a3fc14795df5700da78bc73e19863ca6e`), `inspect-verse-archive.yml` (`d1bb5e4c728aaeb216dd0669cd72a92f1828813d`), `official-audio-preflight-tests.yml` (`68b9f997c9792563232402c700e1b98f11d06325`), `prepare-ash-sharh-1-8-audio.yml` (`f433f8b2f45158c08016ad5fa628b14e15ff8e0b`), `quran-batch-engine-tests.yml` (`7f0ff6af1e818a7c2d83bf63eb4f2fc9f31cd774`), `review-background-candidates.yml` (`a5d5dcd40e0b16ea89298d2bd6aca42cd6d7ad4c`), `test-quran-request.yml` (`9eb99f68b815ee8207fd930d7fb4fb02599aaca8`), and `test-second-video-renderer.yml` (`a7e99d15553ea727b2381c14cc64204a2495538a`).
- `inspect-official-audio.yml` already had a Pro-blocking guard; re-fetch confirmed it. `pro-safety-tests-manual.yml` retains its exact Pro-only guard. `telegram-quran-request.yml` remains scoped to the original production branch and was not changed.
- All work stayed on `feature/quran-video-pro`. No changes to `main` or `feature/telegram-review-notifications`, original Quran code, active production workflow, Telegram secrets, bot settings, Cron, or schedule.
- No Actions workflow was dispatched; no tests, render, Telegram API request, TikTok publish, or secret access occurred. Eight-suite Pro safety workflow remains NOT RUN. The changes are source-level guards; runtime Actions behavior has not been exercised.
- Next: verify the complete 21-file workflow matrix, then address the preview-test fixture and remaining Pro delivery gates separately. Do not create or dispatch a Pro Telegram delivery workflow or send a preview without separate explicit authorization.


## 2026-11-06 — Preview fixture correction and complete workflow guard matrix
- Corrected `tests/test_send_pro_preview_telegram.py::manifest()` by adding the required top-level `source` object (Quran.com / Al-Baqarah 2:201). Commit: `4c9f25c36765a4fe97f1e448345e790bcd7c98e2`; re-fetch verified blob `da477d948c62dc57d4b95815435098569687553b`. This repairs the statically identified fixture/validator mismatch; tests were not run.
- Cross-check of the 21 workflow files on this Pro branch: 18 legacy workflows now have a job-level condition that skips their job when `github.ref` is `refs/heads/feature/quran-video-pro`; `inspect-official-audio.yml` already had the same Pro-blocking condition; `pro-safety-tests-manual.yml` retains its exact Pro-only gate; `telegram-quran-request.yml` remains explicitly limited to `feature/telegram-review-notifications`. This is a static configuration check, not an Actions execution test.
- The original production branch/workflow, Telegram bot credentials, schedule, Cron and delivery path remain untouched. No secret values were read or changed.
- No tests were run, no workflow was dispatched, no render or Telegram request occurred, and no TikTok publish occurred. The eight-suite Pro safety workflow remains NOT RUN.
- Next: continue with a separate Pro-only preview-delivery design. Keep candidate rendering, Telegram send, and TikTok publishing as distinct approval gates. Do not create or dispatch an active delivery path or send a preview until the exact action is separately authorized.


## 2026-11-06 — Preview sender duplicate-send review (static)
- Re-fetched `src/send_pro_preview_telegram.py` (blob `14070ef7bcfcaa0d0f6818f81b926322674910c0`) and `tests/test_send_pro_preview_telegram.py` (blob `da477d948c62dc57d4b95815435098569687553b`) from `feature/quran-video-pro`.
- Confirmed the sender requires explicit `--confirm-preview-send`, validates candidate-only lifecycle and exact preview filename/manifest binding, makes one Telegram API request per invocation, and does not automatically retry transport failures.
- Confirmed a remaining duplicate-send limitation: the preview sender has no durable idempotency record or message ledger. A person or future workflow could invoke it again with the same candidate and send another preview. This is a static code-path finding; no duplicate send is known to have occurred.
- Recommended design before any delivery workflow: a Pro-only durable preview-send ledger keyed by stable candidate ID plus immutable video/manifest identity; reserve before the request, persist the reservation before network access, and mark delivered only after a valid Telegram message ID. Ambiguous transport outcomes must remain blocked pending human resolution; never auto-retry. Keep this preview ledger separate from production rotation and the original Quran engine.
- No code or workflow was changed in this review. No tests were run, no workflow dispatched, no render, Telegram request, TikTok publish, secret access, or Cron change occurred. The original production branch and Telegram route remain untouched. The expanded eight-suite Pro workflow remains NOT RUN.
- Next: design and review the preview idempotency state machine and its failure-boundary tests. Implementation requires separate explicit approval; delivery workflow creation/dispatch and an actual preview send remain separate approval gates.

- Additional design refinement after inspecting `src/pro_delivery_ledger.py` (blob `6466ba9faee6c8c76dec47a216aac9818f4f5314`): do not silently reuse the production-style delivery ledger unchanged for previews. It is keyed by manifest ID and records content type/run ID/message ID, but does not bind a reservation to immutable manifest/video hashes or distinguish preview lifecycle as its own ledger domain. Prefer a separate preview ledger (for example `data/pro_preview_send_ledger.json`) with candidate ID, manifest SHA-256, MP4 SHA-256, workflow run ID, state, timestamps, and Telegram message ID. A matching prior reservation/delivery/uncertain entry must block a second send; a changed artifact should require a new reviewed candidate version, not overwrite the old identity. Cross-run persistence and one fixed workflow concurrency group are required; the local file lock alone only serializes processes on one runner.


## 2026-11-06 — Preview idempotency test matrix and concurrency review (static)
- Re-fetched the Pro manual safety workflow (`a6516c54dccdbd93227a76d59e253dccaa5f7f26`), preview sender (`14070ef7bcfcaa0d0f6818f81b926322674910c0`), delivery-ledger tests (`3002c1b102acc4391d71cd0513561f86c6d5347c`), and delivery-cycle tests (`392f199cb1d85f9193b15d2718edb7ba4b7d493a`).
- The existing safety workflow has a concurrency group for the test workflow only; it does not protect a future preview-send workflow. A preview delivery workflow must use one fixed workflow-level concurrency group with `cancel-in-progress: false`, in addition to durable persisted ledger state. Local file locking is not a cross-run lock.
- Important identity rule: use candidate ID as the unique ledger key, and store manifest/video SHA-256 hashes as immutable attributes. Do NOT use only a composite candidate+hash key: a changed file could otherwise create a second key and bypass the duplicate block. If the same candidate ID appears with different hashes, fail closed and require a separately reviewed candidate version/ID.
- Required offline tests before delivery: first reservation persisted before request; repeated same candidate blocked; same candidate with changed manifest hash blocked; same candidate with changed MP4 hash blocked; confirmed Telegram message ID transitions to delivered and is terminal; timeout/connection reset/invalid Telegram response transitions to uncertain and blocks resend; preflight errors (missing/empty/oversized MP4, invalid manifest/caption/config) happen before reservation; persistence failure before request means zero network calls; failure persisting post-send result leaves remote reservation blocking; concurrent attempts serialize and only one can reserve.
- The current preview sender still performs no ledger reservation or idempotency check. The current preview tests cover one-call success and no automatic retry, but not repeat-invocation blocking, artifact hash binding, or cross-run concurrency. This is a static coverage assessment; tests were not run.
- No code/workflow changes, tests, dispatch, render, Telegram send, TikTok publish, secret access, or Cron changes were performed. Original production engine/branch remain untouched. Eight-suite Pro workflow remains NOT RUN.


## 2026-11-06 — Pro preview-to-original-Telegram integration review
- Read-only re-fetch on `feature/quran-video-pro` confirmed `.github/workflows/telegram-quran-request.yml` remains explicitly limited to `feature/telegram-review-notifications` and checks out that same production branch. It was not changed.
- The original Quran sender `src/send_telegram.py` reads `TG_BOT_TOKEN` and `TELEGRAM_CHAT_ID`; its caption is Quran-specific. The Pro preview sender uses separate environment names `PRO_PREVIEW_TG_BOT_TOKEN` and `PRO_PREVIEW_TELEGRAM_CHAT_ID`, requires explicit `--confirm-preview-send`, and labels the message as an unapproved preview.
- Reuse design remains: a future Pro-only workflow may map the existing repository secrets into the Pro sender's environment variables, without reading or changing secret values and without modifying the production workflow. This mapping has NOT been implemented or tested; secret availability/permissions remain unverified.
- Important destination limitation: Pro preview sender currently accepts only a positive numeric chat ID and does not independently query Telegram `chat.type`. Treat private-chat destination as a configuration requirement to verify during an explicitly approved test, not as proven by static code alone.
- No Pro delivery workflow was created or enabled. No tests or Actions were run, no render or Telegram request occurred, and no TikTok publishing occurred.
- No code, original bot configuration, secrets, Cron, production workflow, `main`, or `feature/telegram-review-notifications` was changed. Original Quran production engine remains untouched.
- Next: finish a fail-closed integration design, including destination verification and preview idempotency, before requesting separate approval for implementation. Rendering, workflow dispatch, Telegram send, and TikTok publishing remain distinct actions requiring explicit authorization.


## 2026-11-06 — Cross-run preview ledger persistence review
- Re-fetched `src/persist_pro_ledger.py`, `src/pro_delivery_ledger.py`, and `tests/test_persist_pro_ledger.py` from the Pro branch.
- Existing production-style Pro ledger persistence commits only `data/pro_delivery_ledger.json`, enforces the exact `feature/quran-video-pro` branch, rejects pre-staged/unrelated paths, and pushes to that exact branch. It requires repository write permission in the workflow token. Its tests cover wrong branch, unrelated staged paths, exact ledger-only commit/push, and push failure.
- Existing local ledger locking/atomic writes protect concurrent processes sharing one filesystem, but do not by themselves serialize separate GitHub-hosted runners. A future preview workflow must have one fixed concurrency group with `cancel-in-progress: false`; it must also handle a failed/non-fast-forward persistence push as a hard stop before Telegram.
- Do not reuse `data/pro_delivery_ledger.json` for preview identity: production delivery ledger keys by manifest ID and has different lifecycle semantics. Preview requires a separate durable file, candidate-ID uniqueness, manifest and MP4 SHA-256 identity, and reserved/delivered/uncertain states. Preflight must complete before reservation; reservation must be durably pushed before the network request; a valid Telegram message ID is required for delivered; ambiguous transport/response or final persistence failure must remain blocked pending human reconciliation.
- The future workflow's `contents: write` permission should be job-scoped and granted only after an exact Pro ref guard; never expose the existing bot secrets to non-Pro refs. The production workflow remains unchanged.
- This was static inspection and design documentation only. No code, workflow, tests, dispatch, render, Telegram request, TikTok publish, secrets, Cron, bot settings, or production branch changed. Original Quran production engine remains untouched; eight-suite safety workflow remains NOT RUN.
- Next: define the exact preview-ledger schema and state-transition contract, then review the proposed manual-only workflow boundary. Implementation and all execution/delivery actions remain separately gated.


## 2026-11-06 — Preview ledger schema and transition contract
- Re-fetched preview sender, existing delivery ledger, and delivery cycle. Preview sender currently has no persistence/idempotency integration; the production delivery cycle is a different interface and must not be reused unchanged for candidate previews.
- Proposed separate file: `data/pro_preview_send_ledger.json`, schema version 1, top-level `entries` keyed by immutable candidate ID. Each entry must include:
  - `candidate_id`, `content_type` (`dua` or `dhikr`), `manifest_sha256`, `video_sha256`, `workflow_run_id`;
  - `state` (`reserved`, `delivered`, or `uncertain`), `created_at`, `updated_at`;
  - `telegram_message_id` (null unless delivered), plus optional non-secret diagnostic outcome metadata.
- Identity rule: candidate ID is the unique key. If it already exists, reject every second send regardless of state. If the same candidate ID is presented with changed manifest/video hashes, reject as an identity conflict; a materially changed candidate must receive a new reviewed candidate ID. Hashes are immutable evidence, not a way to bypass the uniqueness rule.
- Required order:
  1. Preflight every local input before reservation: exact Pro ref, manifest lifecycle and validator, candidate ID/path safety, exact PREVIEW-ONLY filename, MP4 existence/size, caption length, bot/chat configuration presence, and compute SHA-256 for manifest and MP4.
  2. Acquire the Pro workflow's fixed concurrency group (`cancel-in-progress: false`); load the latest remote ledger and reject malformed/unknown schema or an existing candidate ID.
  3. Write `reserved` with hashes/run ID and push only this ledger file to the exact Pro branch. Telegram must not be called unless that push succeeds and the committed reservation is re-read/verified.
  4. Call Telegram once only. No automatic retry for timeout, connection loss, malformed response, or any uncertain outcome.
  5. On a valid Telegram success response with positive integer `message_id`, write/push `delivered`. If Telegram outcome is ambiguous, write/push `uncertain`. If final ledger persistence fails, the previously persisted `reserved` record remains a duplicate-send block and must be manually reconciled.
- State transitions: `reserved -> delivered`, `reserved -> uncertain`, and human-confirmed `uncertain -> delivered` only when a valid message receipt is recovered. Releasing `reserved/uncertain` as not delivered requires a separate explicit human confirmation and evidence check. Never auto-delete or auto-expire a reservation.
- Concurrency/persistence: local file locks alone do not protect different GitHub runners. Serialize preview workflow runs with one fixed concurrency group; use a fresh checkout/fetch before read-modify-write; on push conflict/non-fast-forward, stop before Telegram and reconcile from the remote ledger rather than force-pushing. The workflow should grant `contents: write` only in its exact-Pro-guarded job.
- Keep this file and lifecycle entirely separate from `data/pro_delivery_ledger.json`, production rotation/history, the original Quran sender/workflow, and TikTok publishing. The existing preview sender must not be called directly by a workflow until this ledger wrapper is implemented and tested.
- This is a design checkpoint only. No code, workflow, tests, dispatch, render, Telegram request, TikTok publish, secret, Cron, bot setting, or production branch changed. Original Quran engine remains untouched; expanded eight-suite safety workflow remains NOT RUN.
- Next: review the complete manual-only Pro workflow security boundary (trigger, exact ref guard, secret exposure, write permissions, artifact paths, concurrency, and failure behavior) before requesting approval for implementation.


## 2026-11-06 — Manual Pro preview workflow security boundary
- No Pro preview-delivery workflow currently exists; the only Pro-specific workflow in the reviewed inventory is the manual read-only safety-test workflow. Therefore no delivery path is active.
- Required trigger: `workflow_dispatch` only. Do not add `schedule`, `push`, `pull_request`, `workflow_run`, or reusable-call triggers for preview delivery.
- Required isolation: job-level exact-ref condition `github.ref == 'refs/heads/feature/quran-video-pro'`; checkout explicitly pins `feature/quran-video-pro` (never the triggering ref implicitly). Do not use `pull_request_target`.
- Permissions: default to `contents: read`; grant `contents: write` only to the single guarded delivery job that must persist the preview ledger. No package, actions, or other write scopes. Do not grant repository-wide permissions unnecessarily.
- Secret exposure: do not define Telegram secrets at workflow/job global environment. Map `secrets.TG_BOT_TOKEN` and `secrets.TELEGRAM_CHAT_ID` only into the final, explicitly confirmed Pro preview-send step, after all branch, artifact, manifest, rights, and ledger-reservation checks. Never echo, print, interpolate into shell command text, upload, or persist secrets. Existing secret values/settings remain unchanged.
- Input/artifact boundary: do not accept arbitrary caller-provided paths or URLs. Resolve manifest and MP4 only beneath fixed Pro candidate/output directories; reject symlinks/path traversal and enforce the exact `PREVIEW-ONLY-{dua|dhikr}-{candidate_id}.mp4` naming contract. Bind the manifest and MP4 hashes in the separate preview ledger. Do not fetch unreviewed arbitrary URLs during the send job.
- Execution order: validate branch and inputs; preflight; fetch latest Pro ledger; acquire serialized run; reserve and persist the ledger; re-fetch/verify the committed reservation; only then expose Telegram secrets to the one send step. After one send attempt, persist delivered/uncertain state. No automatic retry. Push conflict, missing ledger, invalid response, or persistence failure must stop/retain a blocking state.
- Concurrency: one fixed group for all Pro preview sends, `cancel-in-progress: false`; do not use a per-candidate group, which would allow two candidates/runs to race the same shared ledger.
- Output handling: retain only non-secret run metadata and Telegram message ID/state; do not print token/chat ID. No TikTok API credentials, publish step, or automatic posting action may exist in this workflow.
- Test separation: offline safety tests remain a separate manual read-only workflow and must not receive Telegram secrets or `contents: write`. Do not dispatch either workflow without a separate explicit instruction.
- This is a static architecture checkpoint, not an implementation. No workflow/code/test/dispatch/render/Telegram/TikTok/secret/Cron/bot-setting/production-branch change occurred. Original Quran engine remains untouched; eight-suite safety workflow remains NOT RUN.
- Next: prepare an implementation checklist and targeted offline test matrix for the ledger wrapper and workflow guards. Request explicit approval before creating/changing code or workflows; keep render and Telegram send as separate approvals.


## 2026-11-06 — Implementation checklist and targeted offline test matrix (design only)

### Implementation sequence (not yet authorized or started)
1. Add a standalone preview-ledger module and schema version 1 at `data/pro_preview_send_ledger.json`; do not alter or reuse the production delivery ledger.
2. Implement strict parsing and fail-closed validation: top-level object/schema version/entries shape; candidate key and embedded ID agreement; supported content type/state; exact lowercase 64-hex SHA-256 values; non-empty workflow run ID and timestamps; Telegram message ID null except for delivered, and a positive integer for delivered (explicitly reject bool, because Python bool is an int subclass).
3. Implement immutable candidate identity: candidate ID is the unique key; any existing ID blocks another send; changed manifest/video hashes under that ID are a conflict, not a new attempt.
4. Implement atomic write (temporary file + replace), fsync where supported, and local process lock. Treat local lock as same-runner protection only; rely on the workflow-wide fixed concurrency group for cross-run serialization.
5. Implement explicit transition validation only: reserved→delivered/uncertain; uncertain→delivered only with a recovered valid receipt; no automatic expiry/deletion/release. Human reconciliation must be a separate deliberate operation with evidence.
6. Implement a Pro-only persistence wrapper: exact branch check; fresh remote state; only the preview-ledger path may be committed; reject unrelated staged changes; no force push; any conflict or failed verification stops before Telegram.
7. Implement a manual-only Pro workflow only after the ledger wrapper and offline tests are ready. Keep exact ref guard, pinned checkout, fixed concurrency, least permissions, and secrets scoped only to the final send step.
8. Add the orchestration wrapper so complete local preflight occurs before reservation; verify the remote reservation before the single Telegram call; persist delivered/uncertain afterwards. Keep preview flow separate from production delivery/rotation.
9. Keep actual render and Telegram send as separate approvals. Do not connect a schedule, TikTok publishing, or the original Quran workflow.

### Targeted offline test matrix (mocked filesystem/network/Git; no live services)
- Schema: valid empty ledger; valid entries; malformed JSON; non-object root; missing/unknown schema version; malformed entries container; unknown fields/states where strict policy requires rejection; key/embedded candidate ID mismatch.
- Types and identity: reject bool/zero/negative/non-integer message IDs; reject malformed SHA-256 and wrong content types; reject empty run IDs/timestamps; duplicate candidate ID; same ID with changed manifest hash; same ID with changed video hash; same hashes with duplicate ID.
- Atomicity/concurrency: simulated write/replace failure leaves previous file intact; lock contention serializes local writers; two independent mocked workflow attempts against the same remote ledger result in only one reservation; stale read/push conflict stops before send.
- State machine: reserved→delivered with valid receipt; reserved→uncertain on timeout/connection loss/invalid or ambiguous response; reject delivered without receipt; reject invalid transitions; uncertain→delivered only with recovered receipt; no automatic release/expiry.
- Preflight: invalid manifest/lifecycle, unsafe candidate ID, path traversal, symlink, wrong PREVIEW-ONLY filename, missing/empty/oversized MP4, caption over limit, missing config, or hash/read failure all fail before reservation and before network call.
- Ordering: no Telegram call if initial persistence fails; no Telegram call until remote reservation is re-fetched and verified; exactly one Telegram attempt on success path; no retry on timeout/connection loss/malformed response; ambiguous result is persisted as uncertain; final persistence failure leaves the previously persisted reserved record blocking duplicates.
- Persistence boundary: exact Pro branch accepted; any other branch rejected; only preview-ledger path committed; unrelated staged changes rejected; push conflict/non-fast-forward fails closed; no force-push.
- Workflow static checks: workflow_dispatch only; exact Pro ref guard; checkout pinned to Pro branch; fixed global concurrency group with cancel-in-progress false; read-only default permissions and narrowly scoped guarded write job; no global Telegram secrets; secret mapping only in final send step; no echo/log/upload of secrets; no TikTok credentials/publish step; no production branch reference or production sender invocation.
- Negative guarantees: tests assert no real HTTP/network, Telegram, GitHub write, render, secrets, or TikTok calls. Use injected fakes/mocks and temporary directories only.

### Test execution gates and current state
- This matrix is a plan, not evidence of passing tests. No new module, workflow, or test has been implemented in this checkpoint.
- The existing eight-suite `pro-safety-tests-manual.yml` remains NOT RUN; no workflow dispatch was performed.
- No render, Telegram send, TikTok publish, secret read/change, Cron change, original bot/workflow change, production branch change, or original engine operation occurred.
- Next review item: inspect current branch tree and test conventions to map each checklist item to exact files/fixtures, then request explicit approval before implementation. Keep test execution and any Telegram preview send separately gated.


## 2026-11-06 — Checklist mapped to current source/test layout (static inspection)

### Existing files and reusable conventions
- `src/send_pro_preview_telegram.py` (SHA `14070ef7bcfcaa0d0f6818f81b926322674910c0`): keep as the one-shot transport adapter, but do not wire it directly to a workflow until the separate preview ledger/orchestration exists. Its current tests mock `urllib.request.urlopen`.
- `tests/test_send_pro_preview_telegram.py` (SHA `da477d948c62dc57d4b95815435098569687553b`): current `ProPreviewTelegramSenderTests` provides temporary-file manifest/video fixtures and mocks `urlopen`. Extend for transport-response validation and assert no second attempt; avoid real network.
- `src/pro_delivery_ledger.py` + `tests/test_pro_delivery_ledger.py`: useful patterns for JSON ledger state transitions, duplicate blocking, and bool-vs-int message ID validation. Do not import/reuse its production ledger path/schema as the preview ledger; implement a separate module and separate tests.
- `src/persist_pro_ledger.py` + `tests/test_persist_pro_ledger.py`: useful exact-branch, staged-path, commit/push failure test patterns. Current constant/path target is `data/pro_delivery_ledger.json`; future preview persistence must use a separate explicit path and must not silently change this production delivery helper.
- `src/pro_delivery_cycle.py` + `tests/test_pro_delivery_cycle.py`: useful reserve→persist→send→persist ordering and mocked dependency injection patterns. It imports the production ledger/persistence path and is not suitable for direct preview reuse; create a distinct preview cycle.
- `.github/workflows/pro-safety-tests-manual.yml` (SHA `a6516c54dccdbd93227a76d59e253dccaa5f7f26`): existing workflow is manual-only, exact Pro branch guarded, checkout pinned to Pro, read-only, and has its own concurrency group `quran-video-pro-safety-tests`. It runs eight test modules and remains NOT RUN. Do not change its purpose or add secrets/write permissions to it.

### Proposed new files and focused tests
- `src/pro_preview_send_ledger.py`: schema parsing, validation, immutable candidate identity, state transitions, atomic save, local lock.
- `tests/test_pro_preview_send_ledger.py`: schema/type/hash/duplicate/transition/atomicity/lock tests; use temporary directories only.
- `src/persist_pro_preview_ledger.py`: exact Pro branch and preview-ledger-only Git persistence, fresh-state verification, no force push.
- `tests/test_persist_pro_preview_ledger.py`: mock `subprocess.run` in the existing persistence-test style; verify wrong branch, unrelated staged paths, push conflict, and exact path only.
- `src/pro_preview_delivery_cycle.py`: preflight→reserve→persist→verify remote reservation→one send→persist delivered/uncertain. Inject persistence, sender, hash and clock dependencies for deterministic offline tests.
- `tests/test_pro_preview_delivery_cycle.py`: order assertions, no send on preflight/persist/verification failure, one send only, ambiguous outcomes, duplicate and hash-conflict blocks, final persistence failure.
- Future workflow file (name not selected): separate `workflow_dispatch` only; do not add delivery steps to `pro-safety-tests-manual.yml`. Static workflow checks can live in a dedicated test such as `tests/test_pro_preview_workflow_security.py`, parsing YAML with an already available dependency only if confirmed; otherwise use robust text/structure checks without introducing a new runtime dependency.

### Specific current coverage gaps confirmed by test-name inventory
- Existing preview sender tests cover explicit confirmation, lifecycle guard, preview filename/private numeric chat, manifest filename match, warning caption, one successful request/no production side effects, and no retry after transport error. They do not cover durable duplicate prevention, manifest/video hash binding, or a second invocation/concurrent invocation.
- Existing production ledger tests cover duplicate reservation, run/type binding, receipt requirement, uncertain blocking/reconciliation, terminal delivered state, invalid type and boolean message ID. These are patterns only; they do not test the new preview schema.
- Existing persistence tests cover wrong branch, pre-staged changes, ledger-only commit/push, push failure, and unexpected staged paths. They target the production ledger path only.
- Existing delivery-cycle tests cover first persistence failure, no-op persistence, persisted path rejection, ambiguous sender→uncertain, uncertainty persistence failure, happy-path ordering, and final persistence failure. They do not exercise preview preflight/hash verification/remote reservation re-fetch.
- Current safety workflow's concurrency group serializes only safety-test runs; a future preview-send workflow must have its own single fixed send concurrency group. Do not confuse the two groups.

### Boundaries reaffirmed
This mapping is static inspection only. No source/test/workflow implementation, test execution, workflow dispatch, render, Telegram request, TikTok publish, secret/Cron/bot setting, production branch, or original Quran engine was changed. Original Telegram workflow remains untouched. The eight-suite safety workflow remains NOT RUN.


## 2026-11-06 — First isolated preview-ledger implementation (not executed)

### Files created on `feature/quran-video-pro`
- `src/pro_preview_send_ledger.py`: schema v1, strict top-level structure, candidate ID validation, content/state/hash/run/timestamp/message-ID validation, atomic JSON save, local process lock, unique candidate reservation, and constrained state transitions. Uncertain→delivered requires explicit `recovered_receipt=True`; there is no release/expiry operation.
- `src/persist_pro_preview_ledger.py`: exact Pro branch only; fetches origin and refuses stale local HEAD; refuses pre-staged changes; stages only `data/pro_preview_send_ledger.json`; rejects any other staged path; normal push only (no force); fetches and verifies remote branch HEAD equals the committed local HEAD.
- `src/pro_preview_delivery_cycle.py`: fixed-root manifest/output preflight; rejects symlink/non-regular/out-of-root inputs; validates candidate lifecycle via existing preview caption/manifest validation; enforces safe candidate ID and exact PREVIEW-ONLY filename; checks MP4 size and configuration; hashes manifest and MP4; reserves and persists before send; verifies reservation; re-hashes artifacts immediately before send; calls injected sender once; records uncertain on exceptions and delivered only with a positive integer message ID.
- New offline test files:
  - `tests/test_pro_preview_send_ledger.py`
  - `tests/test_persist_pro_preview_ledger.py`
  - `tests/test_pro_preview_delivery_cycle.py`
  These cover ledger schema/identity/transitions, persistence branch/path/push boundaries, and cycle ordering/failure cases. They have NOT been run.

### Latest verified file blobs
- `src/pro_preview_send_ledger.py`: `4165e0b9fcf12d5666a867511392bf2f361583ad`
- `src/persist_pro_preview_ledger.py`: `11e128186ca0c7ec87cd416f8ccfc59b89384869`
- `src/pro_preview_delivery_cycle.py`: `4b564f139597261052a968f7c68c3fa610e9f79b`
- `tests/test_pro_preview_send_ledger.py`: `2762f1b366f6ec75674a011c26f1b3c5cfc3ada1`
- `tests/test_persist_pro_preview_ledger.py`: `9cb9d729436af9501840ac0a08e9c790fab818df`
- `tests/test_pro_preview_delivery_cycle.py`: `8cf87814ce6abe798a765f6a1f815de9a8075957`

### Important limits / remaining work
- Static implementation only. No tests were executed and no workflow was created or dispatched.
- The cycle accepts an injected persistence function; the real persistence helper performs remote HEAD verification. A future workflow must provide authenticated checkout/push credentials to that exact Pro-only step and a single fixed concurrency group. This has not been configured.
- Telegram private-chat type is not independently proven by a numeric chat ID. Destination verification must be an explicit pre-send gate in a later approved step.
- The sender still reads the MP4 from disk after the cycle's final hash check; a narrow filesystem race remains possible if another process mutates the artifact at that exact moment. The future workflow should run in an isolated workspace with no concurrent artifact writer; stronger file-descriptor/hash binding can be added before activation.
- The new modules are not wired into any workflow or CLI delivery command. No Telegram request can be initiated by these files as committed unless a caller explicitly invokes the cycle.
- No production delivery ledger, rotation history, original Telegram workflow/bot, production branch, Cron, secrets, renderer, TikTok publishing, or original Quran engine was changed. Existing eight-suite safety workflow remains NOT RUN.
- Next: static review the newly added code and test logic, correct any issues found, then request separate approval before running offline tests. Workflow creation and any Telegram preview send remain separately gated.


### 2026-11-06 — Static hardening pass after initial implementation
- Required explicit `recovered_receipt=True` for uncertain→delivered transitions; the offline ledger test now asserts that a plain message ID is insufficient for this recovery path.
- Persistence now fetches the exact remote branch refspec into `refs/remotes/origin/feature/quran-video-pro` before comparing local/remote HEAD, avoiding ambiguity about which remote-tracking ref was refreshed.
- Preview path preflight now rejects symlinked fixed input directories, symlink path components, paths resolving outside the repository/fixed directories, and a symlinked `data` directory or preview ledger.
- Added a cycle test for artifact mutation after reservation: the second hash check must block Telegram and leave the reservation in its blocking reserved state.
- Added a cycle test for final persistence failure: the first persisted reservation remains the remote duplicate-send boundary; no retry is attempted.
- These changes are static source/test edits only. Tests remain NOT RUN.


### 2026-11-06 — Final static review corrections
- Persistence now refreshes the exact remote-tracking ref both before freshness comparison and after push verification.
- Corrected escaped newline literals in the new persistence test fixtures; tests still have not been executed.
- Re-fetched current code/test blobs after these corrections:
  - `src/pro_preview_send_ledger.py`: `4165e0b9fcf12d5666a867511392bf2f361583ad`
  - `src/persist_pro_preview_ledger.py`: `97cea2e30230aa2ab03f1aba2cefa620543a540d`
  - `src/pro_preview_delivery_cycle.py`: `a96c1b624ba11178413e599020f6327fdb5f946a`
  - `tests/test_pro_preview_send_ledger.py`: `2762f1b366f6ec75674a011c26f1b3c5cfc3ada1`
  - `tests/test_persist_pro_preview_ledger.py`: `ebc9e66e4b191065d70e906cd49b8832e544661d`
  - `tests/test_pro_preview_delivery_cycle.py`: `8cf87814ce6abe798a765f6a1f815de9a8075957`
- Static limitations remain: no workflow/caller exists; Telegram private-chat type is not proven by numeric ID; the final hash-to-file-read interval in the existing sender leaves a narrow local mutation race; complete per-asset media-rights evidence is not enforced by the shared manifest validator. These must be closed before any real preview send.
- No tests run, workflow created/dispatched, render, Telegram request, TikTok publish, secrets/Cron/bot settings, production branch, or original engine changed.


## 2026-11-06 — Static review: bind exact bytes sent + test fixture correction

### Issues found and corrected
- The first persistence test fixture omitted the mocked `git add` subprocess result, shifting subsequent mock outputs. Corrected both success and unrelated-staged-path fixtures; tests remain NOT RUN.
- Closed the previously identified hash-to-file-read race: `send_preview()` now reads the manifest and MP4 bytes once, verifies each against the reserved SHA-256 values passed by the preview cycle, and builds the Telegram multipart request from those exact in-memory bytes. A mismatch fails before `urlopen`.
- `pro_preview_delivery_cycle.py` passes the reserved manifest/video digests into the sender.
- Added sender test coverage asserting either hash mismatch causes no Telegram request.

### Activation limitations still open
- No dedicated preview workflow/caller exists yet; do not invoke the cycle manually.
- Numeric Telegram chat ID does not prove `chat.type == private`; destination verification remains a separate pre-send requirement.
- The shared content validator checks source/approval flags but does not enforce the complete per-asset rights evidence record required by `MEDIA_RIGHTS_POLICY.md`. A separate strict Pro preview rights gate is still needed before any preview send.
- No tests were run. No workflow dispatch, render, Telegram request, TikTok publish, secrets/Cron/bot changes, production branch or original Quran engine changes.


### Rights-gate contract prepared for next static implementation pass
Before any preview can be sent, each exact media file must have a linked per-asset record; a platform-wide license URL or boolean `rights_verified` is insufficient.

**Visual asset record:** exact asset page URL and asset ID where available; creator/uploader; source platform; download date; exact license name and saved license evidence/URL; intended use (editing, synchronization, private review, public social posting, and monetization if applicable); edits made; third-party people/logos/artwork/property/privacy review and resolution; reviewer and checked date.

**Audio recording record:** exact recording/file URL; performer; recording owner; source platform; download date; exact permission/license evidence; explicit permission for download/editing, video synchronization, public social posting, commercial/monetized use if applicable, territories and duration; attribution wording; reviewer and checked date. Any missing scope or unclear ownership must fail closed.

The strict gate should bind each rights record to the exact media file SHA-256 and manifest asset reference, reject generic platform-level evidence, and reject expired/limited permissions outside their stated scope. Silent videos must not be forced to have an audio rights record; any declared audio file must have one. No individual asset is approved by writing this contract.


## 2026-11-06 — Static activation-gate review of preview delivery

### Re-fetched implementation evidence
- `src/pro_preview_send_ledger.py`: blob `4165e0b9fcf12d5666a867511392bf2f361583ad`.
- `src/persist_pro_preview_ledger.py`: blob `97cea2e30230aa2ab03f1aba2cefa620543a540d`.
- `src/pro_preview_delivery_cycle.py`: blob `ca07c7e5289a09cfb3888115b2fb697b721539b4`.
- `src/send_pro_preview_telegram.py`: blob `0e816cb3d1668571117220179a8ca72da30d1764`.
- `src/validate_content_manifest.py`: blob `5146070fea6ab8ed65cd6d192e8a255472260ba1`.
- Focused test blobs: ledger `2762f1b366f6ec75674a011c26f1b3c5cfc3ada1`, persistence `63effcc8037e28795e0e285769c2bb065e2e3fce`, cycle `8cf87814ce6abe798a765f6a1f815de9a8075957`.

### Confirmed safeguards
- Preview ledger has versioned schema, safe candidate IDs, SHA-256 format checks, candidate-ID uniqueness, explicit reserved/delivered/uncertain states, and positive non-boolean Telegram message IDs for delivered state.
- Persistence is exact-Pro-branch only, rejects stale local branch and unrelated staged paths, stages only the preview ledger, uses normal push, and verifies remote HEAD.
- Cycle confines inputs to fixed Pro directories, rejects symlinks/out-of-root files, checks exact preview filename and size, hashes both inputs, persists reservation before sender, verifies reservation, and re-hashes before send.
- Sender reads manifest and video bytes once, checks them against reserved hashes, and constructs the Telegram request from those same bytes. No automatic retry is implemented.
- No delivery workflow/caller exists in the repository state reviewed here; the preview cycle is not automatically invoked.

### Activation blockers / precise limitations
1. A positive numeric Telegram chat ID is not proof that Telegram reports `chat.type == "private"`. Sender and cycle currently do not perform an independent `getChat` verification. Require an explicit pre-send private-chat verification gate before any approved preview.
2. Shared manifest validation checks selected approval/rights booleans and source metadata, but it does not enforce the full per-asset evidence record in `content/pro/MEDIA_RIGHTS_POLICY.md`. Add a strict Pro rights validator binding each exact visual/audio asset record to the actual file SHA-256, source/creator, download date, exact license/permission evidence, intended-use scope, attribution, third-party rights review, reviewer and date. Missing/unclear evidence must fail closed. Silent videos need no audio-file record.
3. A future delivery workflow must serialize all preview sends under one fixed concurrency group with `cancel-in-progress: false`, use an exact Pro ref guard and pinned Pro checkout, and scope write permission/secrets to only the necessary guarded steps. No such workflow exists yet.
4. Current focused tests are authored but have not been executed. Add tests for chat-type verification and strict per-asset rights validation before any send workflow is considered.

### Change boundary
- This checkpoint is static review and documentation only. No source, test, workflow, or manifest file was changed in this pass; no test, dispatch, render, Telegram API call, or TikTok publish occurred.
- No secrets, Cron, original bot/workflow, production ledger/rotation history, `main`, `feature/telegram-review-notifications`, or original Quran engine was changed.
- Existing eight-suite Pro safety workflow remains NOT RUN.

### Next safe step
- Design and review the strict per-asset rights schema and independent Telegram private-chat verification contract, then request explicit approval before implementing them. Keep preview sending disabled until both gates and workflow isolation are independently reviewed.


## 2026-11-06 — Defined strict preview activation contracts (documentation only)

### Per-asset media rights
- Extended `content/pro/MEDIA_RIGHTS_POLICY.md` with a machine-checkable, versioned per-asset rights-record contract.
- Each exact media file must be linked to one stable asset ID and a rights JSON record under `content/pro/rights/`; the record binds the exact local file path and SHA-256 to its source page, creator/performer, rights owner, platform, download date, exact license/permission evidence, intended-use permissions, territory/time scope, attribution, third-party rights review, reviewer/date, and explicit approved decision.
- Audio records additionally distinguish performer from recording owner and require explicit rights for download/edit, video sync, public social posting, and commercial/monetized use where relevant. Silent output does not require an audio record.
- Future validator must reject missing/duplicate/orphaned records, symlinks/path escapes, invalid or mismatched hashes, absent evidence, ambiguous/expired scope, and missing human approval. Boolean flags alone are insufficient.

### Telegram private-chat verification
- Defined a mandatory pre-send Telegram Bot API `getChat` check using the same bot token and configured chat ID as the subsequent `sendVideo`.
- Proceed only when API success is explicit, returned chat ID exactly matches configured ID, and `result.type == "private"`; reject all other/malformed/error responses before `sendVideo`.
- Do not log token or unnecessary personal metadata. Add offline mocked tests for success, ID mismatch, non-private types, malformed/API-error responses, and zero upload calls on failure.
- Official API reference: https://core.telegram.org/bots/api#getchat . The Bot API defines Chat.type values including private, group, supergroup and channel.

### Verification and boundaries
- Policy file update committed on `feature/quran-video-pro`: `4a705b4185cba8f76f08a9c36f1bf2345bb93d03`; blob `ec171000b57fc03d14681a8edddb1f4c30e7bb12`.
- This is a design/policy checkpoint only. No validator code, sender code, tests, workflow, manifests, or rights records were created/changed in this pass.
- No test run, workflow dispatch, render, Telegram API request, or TikTok publish occurred. No secrets, Cron, original bot/workflow, production ledger/rotation, `main`, `feature/telegram-review-notifications`, or original Quran engine was changed.
- Existing focused preview tests and eight-suite safety workflow remain NOT RUN.
- Next: implement the rights-record validator and Telegram getChat preflight only after separate explicit approval; add mocked offline tests, then statically review workflow isolation before any delivery activation.


## 2026-11-07 — Implemented media-rights and Telegram private-chat gates (offline tests authored; NOT RUN)

### Per-asset media-rights validator
- Added `src/validate_pro_media_rights.py` with a version-1 per-asset JSON evidence contract. Manifest `media_assets` must exactly match its visual background and any spoken/ambient audio asset IDs.
- Each record binds the exact local file under `assets/pro/media/` to SHA-256 and an asset-specific HTTPS source page. Rights records are read from `content/pro/rights/{asset_id}.json`; optional saved license evidence is confined to `content/pro/rights/evidence/` and hash-checked.
- Enforced: exact asset/source identifiers, creator/performer, rights owner, platform, download/review dates, license name/evidence, explicit intended-use booleans, worldwide territory, active validity dates, attribution declaration, complete third-party review notes, reviewer, and `decision=approved`.
- Preview use is deliberately held to eventual public-use standard: download/edit/sync/private review/public social posting/commercial monetization must all be explicitly permitted. Silent output must not declare audio. Audio requires separate performer and recording-owner fields.
- Required attribution is blocked until the renderer/caption can inject it; missing, ambiguous, expired, mismatched, symlinked, traversal, out-of-root, or hash-mismatched evidence fails closed.

### Renderer and delivery integration
- `src/render_dua_video.py` now validates per-asset rights before rendering and consumes the exact local approved visual/audio files returned by the validator. It no longer downloads a background URL at render time; the previous approved-URL override mismatch is avoided.
- `src/pro_preview_delivery_cycle.py` validates rights before creating a reservation and checks Telegram private-chat identity before reservation.
- `src/send_pro_preview_telegram.py` independently revalidates rights and artifact-root confinement, then calls Bot API `getChat` immediately before `sendVideo`. It requires `ok=true`, exact returned chat ID match, and `type=private`; group/supergroup/channel/mismatch/malformed/API failures block upload. Token-bearing network exceptions are redacted.
- The cycle repeats `getChat` after the reservation and immediately before upload. A definite pre-upload failure leaves the durable reservation in `reserved` (duplicate-blocking) rather than incorrectly labelling it `uncertain`; ambiguous sendVideo transport outcomes become `uncertain`, with no retry.

### Focused tests authored (not executed)
- Added `tests/test_validate_pro_media_rights.py` for valid silent media, missing record, hash mismatch, asset-reference mismatch, absent public/commercial permission, expired license, unresolved third-party rights, generic root URL, unsupported required attribution, and recording-owner requirements.
- Expanded `tests/test_send_pro_preview_telegram.py` with mocked private getChat success, group/supergroup/channel rejection, returned-ID mismatch, malformed/API/network failures, no upload on failed verification, redacted errors, and single upload/no retry.
- Expanded `tests/test_pro_preview_delivery_cycle.py` with pre-reservation chat verification failure and definite pre-upload rejection state handling.
- Updated `tests/test_render_dua_video.py` to assert the renderer consumes rights-cleared local media and does not fetch background URLs.
- All tests are authored only. No Python test command or GitHub Actions workflow was run. Existing eight-suite Pro safety workflow remains NOT RUN.

### Current activation state and boundaries
- No per-asset rights records or actual media assets were approved/created. Until valid records and exact local files are supplied, preview rendering/delivery correctly fails closed.
- No Pro delivery workflow was created or dispatched. No render, Telegram request, TikTok publish, secrets/Cron/bot settings change occurred.
- Original Telegram bot/workflow, production delivery ledger/rotation, `main`, `feature/telegram-review-notifications`, and original Quran engine remain untouched.
- Next: inspect workflow isolation/concurrency/secret scoping statically, then review all new source/tests and run only approved offline tests before considering any preview workflow. A Telegram send still requires a separate explicit approval.


### Static workflow boundary review after gate implementation
- Re-listed the current Pro branch workflow directory: 21 workflow files; there is still no Pro preview delivery workflow or automatic caller.
- Re-fetched `.github/workflows/pro-safety-tests-manual.yml`: manual `workflow_dispatch` only, exact Pro ref guard, checkout pinned to `feature/quran-video-pro`, `contents: read`, no secrets, no render/send steps, and fixed test-only concurrency with `cancel-in-progress: false`.
- The existing safety workflow already runs the updated `test_send_pro_preview_telegram.py` and `test_render_dua_video.py`, but does not yet include the new `test_validate_pro_media_rights.py` or `test_pro_preview_delivery_cycle.py`. Do not claim those suites are covered by the current workflow.
- No workflow was changed. Adding these two test commands to the manual read-only safety workflow is a separate workflow edit and remains pending approval. Creating a delivery workflow is also not authorized by the gate-code approval.
- Corrected current verified sender-test blob SHA: `2a1606744f83d1721d1fbd5c1c24f9cacbae7a1f` (older intermediate SHA in the previous checkpoint is superseded).
- All focused tests remain NOT RUN; the eight-suite workflow remains NOT RUN. No dispatch, render, Telegram, TikTok, secrets, Cron, bot settings, production branch, or original Quran engine operation occurred.


### 2026-11-07 — Offline safety workflow dependency fix
- Inspected failed GitHub Actions run `42314108213` on `feature/quran-video-pro` (commit `336bbcd3f304add7a186491a3e6c28d6b5065d08`). The earlier eight suites passed through `test_validate_content_manifest.py`; `test_pro_orchestrator.py` then failed during import because `PIL` was unavailable (`ModuleNotFoundError: No module named 'PIL'`).
- Updated only `.github/workflows/pro-safety-tests-manual.yml` to install `Pillow` with pip after Python setup and before the offline test command. Workflow remains manual-only, exact-Pro-branch guarded, read-only permissions, and has no render or Telegram send steps.
- Workflow fix commit: `e5d13045afc8a2425f287aed78ae070fc38dc0b4`.
- The failed run is not a passing result. A rerun is still required to verify whether Pillow resolves the import and whether later suites pass. No workflow dispatch, render, Telegram send, TikTok publish, secret/Cron/bot-setting change, or production/original Quran engine change was made in this fix.

### 2026-11-07 — Safety workflow run #3: Pillow fixed; orchestrator test assertion mismatch
- Run `42318772835` on `feature/quran-video-pro`, commit `f8e0d76a151e7241901f21b9c257de1d0a7a97fb`, failed overall.
- `Install offline test dependency` (Pillow) succeeded. The earlier missing-`PIL` import failure is resolved.
- First eight suites passed: 75 tests total (6, 10, 13, 10, 8, 5, 7, 16).
- In `test_pro_orchestrator.py`, 6/7 tests passed. The one error is `test_candidate_preview_is_separate_from_rotation_and_production`: the fixture deliberately sets `rotation_approved=false`; `build_plan` correctly finds no eligible approved Dua manifest and raises `FileNotFoundError`. The test incorrectly expects `SystemExit`. Keep the production fail-closed rotation logic; fix the test's expected exception type/message only.
- `test_render_dua_video.py` was not reached due to `set -e`; its result remains unverified.
- No render or Telegram/TikTok action occurred. No secrets, Cron, bot settings, original Quran engine, `main`, or `feature/telegram-review-notifications` were touched.
- Next: after explicit approval, adjust the single test assertion and run the manual offline safety workflow again; do not claim green until all suites, including renderer tests, complete successfully.

### 2026-11-07 — Pro offline safety workflow PASS after assertion-only fix
- Updated only `tests/test_pro_orchestrator.py` so `test_candidate_preview_is_separate_from_rotation_and_production` expects `FileNotFoundError` containing `No eligible non-recent dua manifest`. This matches the existing fail-closed rotation behavior when the only manifest is an unapproved candidate preview. No production logic was relaxed.
- Test-fix commit: `17b537e78a8052c374afcc40368ba9164bf32430`; verified test file blob SHA: `b86fb7dec3ec16f47b6eed51ab6d520fec5b36da`.
- Re-ran the failed job in workflow run `42318772835`; latest attempt job ID `128245228932` completed SUCCESS. Workflow explicitly checked out `feature/quran-video-pro`, installed Pillow, and executed all ten configured suites.
- All 90 tests passed: ledger (6), Telegram sender (10), preview Telegram sender (13), media rights (10), preview delivery cycle (8), ledger persistence (5), delivery cycle (7), content manifest (16), orchestrator (7), renderer (8).
- Renderer suite passed, including duration cap <=40 seconds, audio duration mismatch fail-closed, candidate preview gate, no silent audio padding, and overlay/source validation.
- Test-only/offline scope: no rendering, no Telegram API request/send/upload, no TikTok publishing, no production workflow. Original Quran engine/bot, secrets, Cron, `main`, and `feature/telegram-review-notifications` untouched.
- Overall Pro offline safety workflow is now GREEN for the configured ten suites. This does not establish real-world media license validity or authorize production preview delivery.

### 2026-11-07 — Readiness checkpoint after 90/90 offline tests
- Re-read the Pro project status, media-rights policy, content-intake policy, renderer, rights validator, preview sender, preview delivery cycle, and manual safety workflow on `feature/quran-video-pro`.
- Confirmed the safety workflow is tests-only: manual `workflow_dispatch`, exact Pro branch guard, checkout pinned to the Pro branch, `contents: read`, fixed test-only concurrency, and no render/send step.
- Confirmed the offline suite is green (90/90 across ten suites; run `42318772835`, successful latest job attempt `128245228932`).
- Current product readiness remains BLOCKED for real preview creation/delivery: no reviewed production Dua/Dhikr manifest, no individually approved local media asset/rights bundle, and no Pro delivery workflow or schedule are in place.
- The original Telegram bot reuse goal is documented but not enabled or verified for Pro. The separate preview sender requires Pro-scoped token/chat-ID inputs and performs exact private-chat verification before upload; no secret mapping or credential setting was changed.
- Cross-run preview idempotency must be verified in the actual delivery workflow design, not inferred from passing unit tests alone. No real workflow currently persists the preview ledger and sends a preview.
- Updated `PRO_PROJECT_STATUS.md` current validation/readiness and next steps to remove stale statements that tests remain unrun. Status update commit: `c4eeffed47a4feca9e3d9a53dbb58e81352a3867`.
- No source code, workflow, media asset, rights record, manifest, secret, Cron, or bot setting changed in this checkpoint. No render, Telegram request/send/upload, or TikTok publishing occurred. No changes to `main`, `feature/telegram-review-notifications`, or original Quran engine.

### 2026-11-07 — Read-only preview-ledger identity audit
- Reviewed `src/pro_preview_delivery_cycle.py`, `src/pro_preview_send_ledger.py`, `src/persist_pro_preview_ledger.py`, `src/send_pro_preview_telegram.py`, the cross-run persistence design, and `tests/test_pro_preview_delivery_cycle.py`.
- Positive checks: persistence helper pins the exact Pro branch, refuses stale local HEAD and unrelated staged changes, commits only the Pro preview ledger, pushes normally, and verifies the remote HEAD; ledger writes are atomic and locally locked; sender performs private-chat verification immediately before its one upload request and redacts token-bearing transport errors; delivery cycle persists a reservation before send and never auto-retries ambiguous outcomes.
- Hardening gap: after reservation persistence, the coordinator verifies `state == reserved` and both artifact hashes, but does not explicitly compare the persisted entry's `workflow_run_id`, `candidate_id`, and `content_type` to the current invocation/selected manifest. The design requires the reservation to belong to the current workflow run. Add those identity assertions and a focused mismatch test before any delivery workflow is considered.
- This is a static-review finding, not a confirmed exploit or observed duplicate send. No code or test was changed in this checkpoint; no render or Telegram request occurred.
- Status finding recorded in `PRO_PROJECT_STATUS.md`, commit `03bb67e0f8f17cd3c1d10e2f35cc7d2ee5ad2f63`.

### 2026-11-07 — Reservation identity guard implementation
- Added explicit post-persistence identity checks in `src/pro_preview_delivery_cycle.py`: persisted entry must match the selected candidate ID, manifest content type, current workflow run ID, `reserved` state, and both artifact SHA-256 values before sender invocation.
- Added three negative tests in `tests/test_pro_preview_delivery_cycle.py` for mismatched workflow run ID, candidate ID, and content type. Each mutates the ledger after the persistence callback and verifies no send callback occurs.
- Commits: implementation `c205935e485563ba3b10abb242cb2f9590dbc793`; tests `6eac3e6b5672c0338d595633ea27e98699edd446`.
- Re-fetched both files from the Pro branch and verified the guard and all three tests are present.
- Test execution is pending: this session's GitHub connector does not expose a workflow-dispatch action. No workflow was dispatched; no test pass is claimed for this patch. The previous 90/90 offline suite was run before these additions.
- No render, Telegram request/send, TikTok publish, secret/Cron/bot setting change, or production/original-branch change.


## 2026-11-07 — Reservation identity test expectation correction and execution blocker
- Corrected the candidate-ID mismatch test to expect the ledger validator's actual early `ValueError` (key/candidate_id mismatch), rather than a later `RuntimeError`. This is a test-only correction; the production reservation identity guard was not weakened or changed.
- Correction commit: `347768732f8ac09ca355bbab0b8905b5d181bb56`. Re-fetched Pro branch head and confirmed it points to this commit.
- Updated `PRO_PROJECT_STATUS.md` with the correction and accurate validation state. Status update commit: `27343e5d7a042b4162a9aba839d6324231fc82e8`.
- The three new/updated identity mismatch tests are still NOT RUN. Prior 90/90 success (run `42318772835`, latest job attempt `128245228932`) predates these changes and does not validate them.
- Checked the available GitHub Actions operations: workflow/job inspection and rerun are available, but no workflow-dispatch operation is exposed in this session. Re-running the previous successful run would use its older commit, not the current Pro head, so it was deliberately not attempted. A fresh manual dispatch of `.github/workflows/pro-safety-tests-manual.yml` against `feature/quran-video-pro` remains required.
- No code, workflow YAML, render, Telegram API request/send/upload, TikTok publish, secrets, Cron, bot settings, production branch, or original Quran engine was changed in this checkpoint.

## 2026-11-07 — Read-only consistency and validation review

- Re-fetched the current Pro status, development log, content rotation implementation, manifest validator, and their focused tests from `feature/quran-video-pro`.
- Documentation consistency finding: `PRO_PROJECT_STATUS.md` describes the active product correctly as Dua & Adhkar Pro and says the development-log scope title was corrected, but the current `PRO_DEVELOPMENT_LOG.md` still contains a historical opening section titled/worded as a Quran video-engine goal. Later entries clearly record the Dua & Adhkar scope pivot. This is historical content, not evidence that Quran production is currently in Pro scope; a future documentation cleanup should label the opening audit as historical and make the current scope unmistakable. No documentation was edited in this review.
- Content-rotation robustness finding: `src/content_rotation.py` catches unreadable/invalid JSON, but assumes every successfully parsed JSON root and nested `publishing` value is an object. A valid JSON list/scalar or malformed nested shape can raise `AttributeError` rather than being skipped or rejected with a controlled fail-closed result. `choose_manifests` also re-reads the selected file and assumes its `id` remains present/string-shaped. This is a static robustness gap; no exploit or runtime failure was observed.
- Test-coverage finding: `tests/test_content_rotation.py` covers approved/recent/type-separated selection and all-or-nothing batch selection, but has no malformed-root or malformed-`publishing` cases. `tests/test_validate_content_manifest.py` covers the principal Pro content gates; the current validator explicitly checks the manifest root and nested source/visual/audio/publishing objects.
- Validation boundary: the prior 90/90 run remains valid for the ten suites and commit it tested, but does not include the later reservation-identity guard tests. Those three tests remain NOT RUN; the available GitHub connector still does not expose a fresh workflow-dispatch action, and rerunning an older workflow would not validate the latest branch state.
- Next safe work: (1) review the complete Pro test-workflow suite list against all newly added safety tests; (2) prepare a small, explicit documentation-only cleanup proposal for the historical opening section; (3) propose focused content-rotation shape-validation tests and a fail-closed behavior before any code change. Each edit or execution still requires the relevant explicit approval.
- This checkpoint was read-only until this log entry was appended. No source code, tests, workflow, manifest, media, rights record, render, Telegram request/send/upload, TikTok publish, secret, Cron, bot setting, original Quran engine, `main`, or `feature/telegram-review-notifications` was changed or operated.


## 2026-11-07 — Safety workflow test-coverage inventory (read-only)

### Branch and source verification
- Repository: `samiouess-ux/IslamicTikTokAutomation`; branch: `feature/quran-video-pro`.
- Branch head observed before this documentation update: `2406394c03d40895405ee730e24fc5aa1c792c10`.
- Re-fetched `.github/workflows/pro-safety-tests-manual.yml` and enumerated Python test files in `tests/` from the exact Pro branch.
- The workflow currently invokes ten suites:
  1. `test_pro_delivery_ledger.py`
  2. `test_send_pro_telegram.py`
  3. `test_send_pro_preview_telegram.py`
  4. `test_validate_pro_media_rights.py`
  5. `test_pro_preview_delivery_cycle.py`
  6. `test_persist_pro_ledger.py`
  7. `test_pro_delivery_cycle.py`
  8. `test_validate_content_manifest.py`
  9. `test_pro_orchestrator.py`
  10. `test_render_dua_video.py`

### Pro-related test modules present but not explicitly invoked by this workflow
- `tests/test_persist_pro_preview_ledger.py` — preview-ledger persistence, exact branch/freshness checks, staging-path restrictions, and remote-head verification.
- `tests/test_pro_preview_send_ledger.py` — isolated preview ledger schema, candidate identity, duplicate prevention, state transitions, and receipt recovery.
- `tests/test_prepare_pro_telegram_caption.py` — rejects a non-Pro manifest in the caption preparation path.
- `tests/test_content_rotation.py` — deterministic selection, approval/type filtering, non-repetition, and all-or-nothing batch selection.
- `tests/test_content_rotation_repository_safety.py` — repository catalogue must fail closed while there is no eligible approved Quran manifest.
- The similarly named `test_persist_pro_ledger.py` currently in the workflow is not a substitute for `test_persist_pro_preview_ledger.py`; they exercise different persistence paths.

### Interpretation and limitations
- This is a static coverage inventory only. It does not establish that any omitted suite passes or fails.
- No tests were run; the three reservation identity tests remain NOT RUN.
- The historical 90/90 result in run `42318772835` covers the ten suites configured at that run's commit only. It does not cover the five modules listed above unless they were separately invoked, and it predates the later reservation identity guard/tests.
- Suggested next review: inspect whether each omitted module is safe and appropriate to add to the manual offline safety workflow, paying particular attention to repository-dependent rotation assumptions and persistence tests that mock Git operations. Do not change workflow YAML without separate approval.
- Documentation consistency remains open: the beginning of this log still contains the pre-pivot Quran-engine baseline as historical material, while the current Pro scope is Dua & Adhkar. The historical section should be explicitly labeled as superseded/historical in a later documentation-only cleanup; no such cleanup was made here.

### Change and safety record
- This entry is documentation-only. No source code, tests, workflow YAML, manifests, rights records, or media were changed.
- No workflow dispatch/rerun, test execution, render, Telegram API request/send/upload, or TikTok publish occurred.
- No secrets, Cron, original Telegram bot/settings, production ledger/rotation, `main`, `feature/telegram-review-notifications`, or original Quran engine were touched.


## 2026-11-07 — Malformed content-rotation manifest hardening

### Change
- Updated `src/content_rotation.py` to skip syntactically valid JSON manifests whose top-level value is not an object, and manifests whose `publishing` field is not an object.
- This prevents malformed manifest shapes (for example a JSON list, `null`, or a list-valued `publishing`) from raising an incidental `AttributeError` during rotation.
- Eligibility requirements remain unchanged: supported content type, explicit `rotation_approved`, `publishing.approval_required`, `auto_publish` disabled, stable non-recent ID.
- Added two regression tests in `tests/test_content_rotation.py`: non-object top-level JSON is skipped; non-object `publishing` is skipped. Both tests include a valid eligible manifest to verify selection continues safely.

### Verification status
- Source update commit: `5e21ce4e249c71265b40080af7887405820fcfb0`; source blob: `6ace18562114e7630f02c9579535e9e4fbe99a86`.
- Test update commit: `555afba89d3fc296b695a7317f5f306e05db602f`; test blob: `b4ec822ea6e65eacc883a56949815e4a73f46ad2`.
- Both files were fetched again from `feature/quran-video-pro` and their updated blob SHAs confirmed.
- Tests were NOT RUN. No claim is made that the new tests pass.
- The manual workflow YAML was not changed and no workflow was dispatched or rerun.

### Safety boundary
- Only `src/content_rotation.py` and `tests/test_content_rotation.py` were changed in this code fix.
- No manifests, media, rights records, ledger data, secrets, bot settings, Cron, Telegram, TikTok, render, or production workflows were touched.
- `main`, `feature/telegram-review-notifications`, and the original Quran engine remain outside this change.


## 2026-11-07 — Batch rotation revalidation after selection

### Change
- Hardened `choose_manifests()` against a manifest changing between initial selection and its subsequent read.
- The selected file is now re-read under error handling and revalidated for JSON-object shape, requested content type, explicit rotation approval, manual-review requirement, disabled auto-publish, and a non-empty ID not already in the batch/recent set.
- Added two regression tests simulating a selected file becoming invalid JSON and losing its ID before the batch re-read.
- Changes are limited to `src/content_rotation.py` and `tests/test_content_rotation.py`; no workflow configuration was changed.

### Verification
- Source commit: `ad9762a1772376c5bc8ae13941569d5a3125bc96`; source blob: `2ad7ca31cf8b5c54edc362c64f845fb4412fbb6a`.
- Test commit: `a676cee0922a9a26cd612d0c3e197ffe5c42c23c`; test blob: `67fbba0ebd8099831c02a4b37ae52c0922251b80`.
- Tests were added but NOT RUN. No workflow dispatch or rerun occurred.
- No rendering, Telegram request/send, TikTok publishing, production ledger/history update, secrets, Cron, original bot, original Quran engine, `main`, or `feature/telegram-review-notifications` was touched.


## 2026-11-07 — Scope private-review media rights to the actual delivery territory

### Change
- Updated `src/validate_pro_media_rights.py` so `private_review` no longer requires worldwide territory coverage by default.
- Private review now requires an explicit `review_delivery_territory` value in the manifest. The rights record must either list that territory (case-insensitive exact match) or grant worldwide/global/all coverage.
- Public-social and monetized-social uses continue to require worldwide/global/all territory coverage, independently of their separate intended-use permissions.
- Passed the manifest's declared review territory through the renderer, isolated Telegram preview sender, and preview delivery-cycle preflight so all three gates apply the same check.
- Updated rights, sender, and preview-cycle test fixtures to declare Tunisia as the review delivery territory. Added tests that reject missing or unlicensed private-review territories and confirm that non-worldwide permissions remain blocked for public use.

### Verification
- Source commits:
  - `validate_pro_media_rights.py`: `8a4ffbcc37142305f605d67bfe58a43f3f10f8cd`; blob `9f6e8f5d1fd1ef0aa2ca9fca66f6a0f0371ce014`.
  - `render_dua_video.py`: `f829c35af0ac557068a6c15d49d86fd2af1dbc47`; blob `533c04b71d6ec85fcdee5133407f1307ce805b62`.
  - `send_pro_preview_telegram.py`: `cfd7217f338f05c8cb0d4f6c1fe3c5c8e28d7e3e`; blob `072cd2d4facbae696c40ec94d0d499a6aeb339fd`.
  - `pro_preview_delivery_cycle.py`: `9fd42c615751eb185c28929d96f3ad593657f732`; blob `a09fb972d455b9ac077035074d30e43e110e4d50`.
- Test commits:
  - `test_validate_pro_media_rights.py`: `779dd876d7a13f464bfd9026c090d45b008350cd`; blob `36fa0acabf981e5709e333b6b72627d69df111df`.
  - `test_pro_preview_delivery_cycle.py`: `c5de460bdc6dfb689fea14ab72c320f2d0d97fc2`; blob `60299ef19cd78683bc530d4c11288479bca26ae7`.
  - `test_send_pro_preview_telegram.py`: `c3b16bb035afb28fa2b7e41e276e31e6f84ff150`; blob `6844c2549223f95942552b740026010be5acc475`.
- Re-fetched all six source/test files and confirmed their current blob SHAs on `feature/quran-video-pro`; branch HEAD at that verification point was `c3b16bb035afb28fa2b7e41e276e31e6f84ff150`.
- Tests were NOT RUN. No workflow dispatch/rerun occurred; no test-pass claim is made.
- The territory string is an explicit manifest declaration; this code validates it against the rights record but does not independently geolocate the Telegram recipient or prove legal interpretation of the license.

### Safety boundary
- Only the Pro rights validator, Pro preview renderer/sender/delivery-cycle code, their relevant offline test fixtures, and this development log were changed.
- No manifest, media, rights record, preview artifact, ledger, secret, bot setting, Cron, Telegram API request/send/upload, TikTok publish, or render was executed or changed.
- The original Quran engine, `main`, and `feature/telegram-review-notifications` were not touched.


## 2026-11-07 — Pro video duration cap raised to 65 seconds
- Per the user's instruction, changed the dedicated Pro dua/dhikr renderer target and hard maximum from 40.0 to 65.0 seconds in `src/render_dua_video.py`. The orchestrator imports the renderer's hard cap, so its preflight inherits the 65-second ceiling without a separate hard-coded limit.
- Updated `tests/test_render_dua_video.py` to assert the 65-second constants and reject a 66-second slideshow.
- Renderer commit: `89ed5d5cc0b03d11325da604d95b23135b510e60`; renderer blob: `74b769e3309ea1ae8334701d5ec68e11ad1aaee7`.
- Test commit: `ddb994ba2218466e3c217d6d200a089e02199a1d`; test blob: `685937e838567c28c480262fc807268e28bde7f8`.
- Tests have NOT been run; the updated assertions are not a passing result. No workflow dispatch/rerun, render, Telegram request/send/upload, or TikTok publish occurred.
- No changes to the original Quran engine, original Telegram bot/workflow, `main`, `feature/telegram-review-notifications`, secrets, Cron, or publishing settings.


## 2026-11-07 — Static review: duration validation and audio boundary

### Findings (review only; no code changes)
- Confirmed the dedicated Pro renderer and the orchestrator's imported hard cap are both 65 seconds. The renderer test asserts 65 seconds and rejects a 66-second item; however, its test function name still says `test_duration_policy_enforces_the_40_second_cap`, which is stale naming only.
- Found a duration-validation gap: Python `NaN` is a float and passes the current `value <= 0` checks; summing NaN then makes `total > 65` false. This affects the renderer item validator and both normal/preview orchestrator preflight paths. Positive infinity is rejected by the cap comparison, but NaN is not. Proposed safe hardening: explicitly require finite numeric durations (for example, `math.isfinite`) at each validation boundary, with regression tests for NaN and infinities.
- Found an audio-boundary concern requiring a product decision: audio duration differences up to 0.75 seconds are accepted, but FFmpeg is still given `-t <video duration>`. Accepted longer audio is therefore cut at the video boundary; accepted shorter audio can end before the video, leaving a silent tail. This is not consistent with the function's stated refusal to pad or truncate. The exact acceptable tolerance should be decided before changing behavior; tests currently accept 9.0 seconds for a 9.5-second target and do not test both sides of the tolerance boundary.

### Verification and safety
- Re-fetched `src/render_dua_video.py`, `src/pro_orchestrator.py`, and `tests/test_render_dua_video.py` from `feature/quran-video-pro`. Current blob SHAs at review time: renderer `74b769e3309ea1ae8334701d5ec68e11ad1aaee7`; orchestrator `a76c75e72bdc030575652f9a76f105ee91865675`; tests `685937e838567c28c480262fc807268e28bde7f8`.
- No source or test code was changed. No tests were run; no workflow dispatch/rerun, render, Telegram request/send/upload, or TikTok publish occurred.
- Next safe code proposal, pending explicit approval: add finite-number checks and tests for NaN; separately agree an audio-duration policy and test short/long audio behavior before changing FFmpeg arguments.
- No production branch, original Telegram bot/settings, secrets, Cron, `main`, `feature/telegram-review-notifications`, or original Quran engine was touched.


## 2026-11-07 — Static review: malformed manifest field types

### Findings (review only; no code changes)
- `validate_content_manifest.py` checks membership in Python sets before verifying that several fields are strings. A JSON list/object supplied as `content_type`, `audio.kind`, `visual.template`, or a dua/dhikr item's `kind` raises an uncaught `TypeError` rather than the validator's normal controlled rejection. The orchestrator's blocked-result handlers catch `SystemExit`, `ValueError`, and `LookupError`, but not `TypeError`, so malformed manifests can produce an unstructured traceback. This still stops the path; no side effect was identified, but it weakens predictable fail-closed reporting.
- `repeat_count` currently accepts JSON boolean `true` because Python treats bool as a subclass of int. If repeat_count is intended to be a strict positive integer, reject bool explicitly.
- Recommended limited hardening: type-check these enum-like fields as strings before set membership, reject bool for repeat_count, and add table-driven malformed-shape tests asserting controlled validation errors and structured orchestrator blocking. No implementation was made pending explicit code-change approval.

### Verification and safety
- Re-fetched `src/validate_content_manifest.py`, `src/pro_orchestrator.py`, and `tests/test_validate_content_manifest.py` from `feature/quran-video-pro`. Blob SHAs: validator `5146070fea6ab8ed65cd6d192e8a25547260ba1`; orchestrator `a76c75e72bdc030575652f9a76f105ee91865675`; validator tests `7914f2c7f0eacc298379b87687377e935cff19d6`.
- Read-only inspection only. No tests were run, no source/test files changed, and no workflow, render, Telegram, TikTok, production bot, or production branch was touched.


## 2026-11-07 — Static review: media-rights record type robustness

### Finding (review only; no code changes)
- The per-asset rights validator correctly checks many fields and verifies media/evidence hashes, fixed-root paths, permissions, and territory. However, two enum-like fields are tested for set membership without first confirming they are strings: `asset_ref.media_type` and `license_evidence.kind`. A malformed JSON list/object in either field can raise `TypeError` instead of the validator's intended `ValueError` rejection. The current top-level callers may therefore report an unstructured failure for malformed rights metadata. This is a robustness/reporting gap; it does not bypass the approval checks or establish that an unapproved asset would be accepted.
- Recommended narrow hardening: require `media_type` and evidence `kind` to be strings before enum membership, and add malformed-list/object regression tests. No implementation was made pending explicit approval.

### Verification and safety
- Re-fetched `src/validate_pro_media_rights.py` (blob `9f6e8f5d1fd1ef0aa2ca9fca66f6a0f0371ce014`), `src/pro_preview_delivery_cycle.py` (blob `a09fb972d455b9ac077035074d30e43e110e4d50`), and `src/send_pro_preview_telegram.py` (blob `072cd2d4facbae696c40ec94d0d499a6aeb339fd`) from `feature/quran-video-pro`.
- Read-only review. No tests or workflows were run; no rendering, Telegram request/send/upload, TikTok publish, or production-path operation occurred.


## 2026-11-07 — Static review: preview-ledger malformed enum values

### Finding (review only; no code changes)
- The isolated preview ledger validates its structure, hashes, identity, timestamps, and delivered message IDs. However, enum membership checks in `_validate_entry` and `reserve` do not first require `content_type` and `state` to be strings. A corrupted JSON list/object in either field, or a non-string argument passed to `reserve`/`transition`, can raise `TypeError` instead of the intended controlled `ValueError`. The malformed ledger still blocks the flow, but the failure can escape the orchestrator's normal blocked-result handling.
- Recommended narrow hardening: type-check content type/state before set membership in entry validation and public ledger operations; add tests for list/object values in persisted entries and non-string API arguments. No code change made pending approval.
- Persistence helper review: branch/ref checks, clean staging precondition, exact ledger-only staging check, and post-push remote-head verification are present. No commit/push helper was executed.

### Verification and safety
- Re-fetched `src/pro_preview_send_ledger.py` (blob `4165e0b9fcf12d5666a867511392bf2f361583ad`), `src/persist_pro_preview_ledger.py` (blob `97cea2e30230aa2ab03f1aba2cefa620543a540d`), `src/pro_delivery_ledger.py` (blob `6466ba9faee6c8c76dec47a216aac9818f4f5314`), `tests/test_pro_preview_send_ledger.py` (blob `2762f1b366f6ec75674a011c26f1b3c5cfc3ada1`), and `tests/test_persist_pro_preview_ledger.py` (blob `63effcc8037e28795e0e285769c2bb065e2e3fce`) from `feature/quran-video-pro`.
- Read-only inspection only. No tests/workflows, ledger persistence execution, render, Telegram request/send/upload, or TikTok publishing occurred. No production branch or original engine/bot was touched.


## 2026-11-07 — Static review: preview caption boundary coverage

### Finding (test-coverage gap; no code changes)
- `build_preview_caption` enforces `MAX_CAPTION_CHARS = 1024` using Python `len(caption)`, and the Telegram multipart request sends the caption as UTF-8 plain text without a `parse_mode` field.
- Existing sender tests verify the preview-only warning text, but do not exercise the exact 1024-character acceptance boundary or rejection at 1025 characters. This leaves the boundary contract unprotected against future edits. Recommended follow-up: add focused boundary tests using otherwise-valid preview manifests, while keeping the current production limit unchanged unless separately verified against Telegram's current Bot API behavior.
- Caption construction is also performed during preview-cycle preflight before ledger reservation, so a too-long caption is rejected before any reservation or Telegram request. No bypass was observed in the inspected path.

### Verification and safety
- Re-fetched `src/send_pro_preview_telegram.py` (blob `072cd2d4facbae696c40ec94d0d499a6aeb339fd`), `src/pro_preview_delivery_cycle.py` (blob `a09fb972d455b9ac077035074d30e43e110e4d50`), and `tests/test_send_pro_preview_telegram.py` (blob `6844c2549223f95942552b740026010be5acc475`) from `feature/quran-video-pro`.
- Read-only inspection only. No source/test changes, test execution, workflow, render, ledger persistence, Telegram request/send/upload, or TikTok publishing occurred. No production branch or original engine/bot was touched.


## 2026-11-07 — Static review: preview artifact path check/use window

### Finding (defense-in-depth concern; no code changes)
- Both `pro_preview_delivery_cycle._inside_regular_file` and `send_pro_preview_telegram._safe_pro_file` resolve and validate an artifact path, then later reopen/read it by pathname. In the direct sender CLI path, expected SHA-256 values are optional; therefore, if an untrusted local process can replace the resolved file between path validation and `read_bytes()` (or replace it with a symlink), the later read may follow a changed target outside the intended Pro directory. The orchestrated cycle additionally supplies expected hashes, which detects changed bytes before upload, but pathname validation alone is not race-free.
- This is a local time-of-check/time-of-use race requiring concurrent filesystem modification; no evidence of exploitation or an ordinary workflow bypass was found. Recommended hardening for a future approved patch: open files with no-follow semantics where supported, validate the opened file descriptor (regular-file type and resolved location/inode), then hash and upload bytes read from that same descriptor. Add focused symlink-swap/path-race tests where portable.

### Verification and safety
- Re-fetched `src/pro_preview_delivery_cycle.py` (blob `a09fb972d455b9ac077035074d30e43e110e4d50`), `src/send_pro_preview_telegram.py` (blob `072cd2d4facbae696c40ec94d0d499a6aeb339fd`), and `tests/test_pro_preview_delivery_cycle.py` (blob `60299ef19cd78683bc530d4c11288479bca26ae7`) from `feature/quran-video-pro`.
- Read-only inspection only. No source/test changes, test execution, workflow, render, ledger persistence, Telegram request/send/upload, or TikTok publishing occurred. No production branch or original engine/bot was touched.


## 2026-11-07 — Static review: timezone normalization in rights dates

### Finding (date-boundary correctness; no code changes)
- `validate_pro_media_rights._date` accepts ISO-8601 timestamps with offsets, but returns `datetime.fromisoformat(...).date()` without converting an aware timestamp to UTC first. The caller compares that date with `datetime.now(timezone.utc).date()`.
- For timestamps near midnight with a non-UTC offset, the recorded calendar date can differ from its UTC calendar date. This can shift the effective comparison by one day for `downloaded_at`, `reviewed_at`, and validity start/end checks. It is a narrow boundary issue, not a general rights-check bypass.
- Recommended hardening: distinguish date-only values from timezone-aware datetimes; normalize aware datetimes to UTC before taking the date; define an explicit policy for naive datetime strings (reject them or treat them as date-only only if the schema permits). Add tests for positive and negative offsets crossing UTC midnight, including validity start/end boundaries. No change made pending approval.

### Verification and safety
- Re-fetched `src/validate_pro_media_rights.py` (blob `9f6e8f5d1fd1ef0aa2ca9fca66f6a0f0371ce014`) and `tests/test_validate_pro_media_rights.py` (blob `36fa0acabf981e5709e333b6b72627d69df111df`) from `feature/quran-video-pro`.
- Read-only inspection only. No source/test changes, test execution, workflow, render, ledger persistence, Telegram request/send/upload, or TikTok publishing occurred. No production branch or original engine/bot was touched.


## 2026-11-07 — Static review: media-rights file verification TOCTOU

### Finding (local concurrent-file race; no code changes)
- `validate_pro_media_rights._safe_file` resolves/checks the asset or evidence path and returns a pathname. The validator subsequently reopens that pathname with `read_bytes()` to hash it, and the renderer later consumes the returned asset pathname in FFmpeg.
- A concurrent local process able to replace a validated file/path between resolution, hashing, and renderer open could cause the bytes ultimately consumed to differ from the bytes whose digest was checked. The same pattern applies to saved license-evidence files. This is a local TOCTOU hardening concern; no ordinary-flow rights bypass was demonstrated.
- Recommended hardening: open files with no-follow semantics where supported, validate the opened file descriptor (regular file and fixed-root identity), hash from that descriptor, and ensure the exact verified bytes/file identity are what the renderer consumes. Add controlled race/symlink replacement tests. Coordinate this with the previously logged preview-artifact TOCTOU finding rather than applying inconsistent path fixes. No implementation made pending explicit approval.

### Verification and safety
- Re-fetched `src/validate_pro_media_rights.py` (blob `9f6e8f5d1fd1ef0aa2ca9fca66f6a0f0371ce014`), `src/render_dua_video.py` (blob `74b769e3309ea1ae8334701d5ec68e11ad1aaee7`), and `src/pro_preview_delivery_cycle.py` (blob `a09fb972d455b9ac077035074d30e43e110e4d50`) from `feature/quran-video-pro`.
- Static inspection only. No source/test changes, test execution, workflow, render, ledger persistence, Telegram request/send/upload, or TikTok publishing occurred. No production branch or original engine/bot was touched.

## 2026-11-07 — Static review: renderer workspace isolation and concat path encoding

### Findings (review only; no code changes)
- `render_dua_video.main()` uses the shared fixed workspace `build/dua` for every invocation. `build_slideshow()` writes deterministic names (`item_000.png`, etc.) and one shared `overlays.ffconcat` there. Two concurrent renders can overwrite each other's overlays or playlist while FFmpeg is consuming them, potentially producing a mixed or incorrect candidate. The current renderer tests use separate temporary directories for direct slideshow tests and do not exercise concurrent `main()` invocations or workspace isolation.
- The concat playlist embeds absolute overlay paths inside single-quoted `file '…'` records without escaping FFconcat-special characters. A checkout/workspace path containing an apostrophe or backslash can make the playlist parse incorrectly; if such a path is attacker-controlled, concat syntax may also be interpreted unexpectedly. Current tests only assert ordinary filenames and do not cover special-character paths.
- Recommended hardening: allocate a unique per-invocation temporary workspace (and clean it safely after FFmpeg completes), then use a documented FFconcat-safe path-escaping routine or a safer generated relative-path scheme. Add tests for concurrent workspace separation and paths containing apostrophes/backslashes. Keep output destinations separately constrained/validated according to the caller's intended output directory.
- These are renderer isolation/path-encoding concerns. Static inspection did not establish an ordinary-flow approval bypass or prove that a malicious path has been exploited.

### Verification and safety
- Re-fetched `src/render_dua_video.py` (blob `74b769e3309ea1ae8334701d5ec68e11ad1aaee7`), `tests/test_render_dua_video.py` (blob `685937e838567c28c480262fc807268e28bde7f8`), and `src/pro_orchestrator.py` (blob `a76c75e72bdc030575652f9a76f105ee91865675`) from `feature/quran-video-pro`.
- Read-only inspection only. No source/test changes, tests, workflow, render, ledger persistence, Telegram request/send/upload, or TikTok publishing occurred. No production branch, original Quran engine/bot, secrets, or Cron was touched.

## 2026-11-07 — Static review: Pro manual safety workflow test-suite omissions

### Finding (coverage gap; no code changes)
- The current `pro-safety-tests-manual.yml` runs ten offline suites, but does not invoke three existing tests that directly cover active Pro paths: `test_pro_preview_send_ledger.py` (candidate identity/state transitions and duplicate blocking), `test_persist_pro_preview_ledger.py` (exact-branch/clean-staging/ledger-only persistence and remote-head verification), and `test_content_rotation.py` (the selector used by the Pro orchestrator, including approval/type/non-repeat/batch behavior).
- These test files are present on `feature/quran-video-pro`, but their existence is not evidence that they pass; none was run during this review. Their omission means the advertised manual Pro safety workflow currently does not protect those behaviors against regression.
- `test_content_rotation_repository_safety.py` is intentionally not recommended for this Pro workflow: it asserts behavior of the real Quran catalogue and belongs to the separate Quran path. `test_prepare_pro_telegram_caption.py` covers a legacy helper, not the isolated preview sender's caption builder; whether it belongs in the suite should depend on whether that helper remains an active Pro entry point.
- Recommended follow-up: add the three directly relevant suites to the manual Pro workflow, after confirming their dependencies remain offline and their fixtures do not invoke real Git/network/Telegram operations (the persistence test mocks subprocess calls). Add a clear workflow-level test inventory so new Pro safety suites are not silently omitted. No workflow edit was made pending explicit approval.

### Verification and safety
- Re-fetched `.github/workflows/pro-safety-tests-manual.yml` (blob `eecd19bbd74199d7b0657a64128768ecba268b39`), `tests/test_pro_preview_send_ledger.py` (blob `2762f1b366f6ec75674a011c26f1b3c5cfc3ada1`), `tests/test_persist_pro_preview_ledger.py` (blob `63effcc8037e28795e0e285769c2bb065e2e3fce`), `tests/test_content_rotation.py` (blob `67fbba0ebd8099831c02a4b37ae52c0922251b80`), `tests/test_content_rotation_repository_safety.py` (blob `82113f72300dd5b62c506406544536e70c63ee66`), and `tests/test_prepare_pro_telegram_caption.py` (blob `e483679cb22a64e091e9b8199de0a19032fed353`) from `feature/quran-video-pro`.
- Read-only inspection only. No workflow edit or dispatch/rerun, no tests, render, ledger persistence, Telegram request/send/upload, or TikTok publishing occurred. No production branch, original Quran engine/bot, secrets, or Cron was touched.


## 2026-11-07 — Static review: production Pro output filename component validation

### Finding (output-path containment; no code changes)
- In `pro_orchestrator.build_plan()`, the manifest `id` is checked only as a non-empty string. The shared manifest validator does not impose a safe filename-component format on the top-level manifest ID.
- `render_plan()` interpolates that ID directly into `output_dir / f"{content_type}-{content_id}.mp4"`. A crafted ID containing path separators or traversal segments can therefore resolve outside the intended output directory and cause FFmpeg's `-y` option to overwrite a different path. This is a path-construction risk if untrusted or malformed manifest content reaches the normal render path; the normal repository content may be trusted, but the guard is not enforced at this boundary.
- The candidate-preview path already applies a restrictive ASCII filename-component regex to its manifest ID, so the normal render path is inconsistent. Recommended hardening: apply the same or a shared strict filename-component validator to production manifest IDs before planning/output construction, and add tests for slash, backslash, dot-segment, absolute-path-like, and valid boundary IDs. Optionally resolve the final output and assert it remains inside the fixed output directory before invoking FFmpeg. No implementation made pending explicit approval.

### Verification and safety
- Re-fetched `src/pro_orchestrator.py` (blob `a76c75e72bdc030575652f9a76f105ee91865675`) and `src/validate_content_manifest.py` (blob `5146070fea6ab8ed65cd6d192e8a25547260ba1`) from `feature/quran-video-pro`.
- Static inspection only. No source/test changes, tests, workflow, render, ledger persistence, Telegram request/send/upload, or TikTok publishing occurred. No production branch, original Quran engine/bot, secrets, or Cron was touched.


## 2026-11-07 — Static review: non-finite ffprobe audio duration

### Finding (media-duration validation gap; no code changes)
- `probe_duration()` converts ffprobe output with `float()` and rejects only values `<= 0`. Python accepts the strings `nan` and `inf` as floats; the comparison with NaN is false, so a reported `nan` duration is returned as if valid.
- `validate_audio_duration()` then computes `abs(actual - expected)`; if `actual` is NaN, the difference is NaN and `difference > tolerance` is also false. Thus a non-finite ffprobe duration can pass the audio-duration gate. This is separate from the previously logged NaN gap in manifest item durations: this issue is at the ffprobe parsing boundary.
- Recommended hardening: require `math.isfinite(duration)` in `probe_duration()` before accepting it, and add tests for ffprobe outputs `nan`, `inf`, `-inf`, malformed text, zero, and a valid positive duration. Also test that non-finite mocked probe results cannot pass `validate_audio_duration()`. No implementation made pending explicit approval.

### Verification and safety
- Re-fetched `src/render_dua_video.py` (blob `74b769e3309ea1ae8334701d5ec68e11ad1aaee7`) and `tests/test_render_dua_video.py` (blob `685937e838567c28c480262fc807268e28bde7f8`) from `feature/quran-video-pro`.
- Static inspection only. No source/test changes, tests, workflow, render, ledger persistence, Telegram request/send/upload, or TikTok publishing occurred. No production branch, original Quran engine/bot, secrets, or Cron was touched.

## 2026-11-07 — Static review: renderer output symlink handling

### Finding (local output-path hardening; no code changes)
- `render_dua_video.main()` creates the requested output parent and passes the output pathname directly to FFmpeg with `-y`. It does not reject an output path that already exists as a symlink, nor does it inspect symlinked parent components. FFmpeg may therefore write through a pre-existing output symlink rather than creating the intended MP4 at the visible path.
- The ordinary Pro preview orchestrator uses a predictable path under `output/pro_preview`, while the renderer CLI also accepts a caller-selected `--output`. This is a local filesystem/path-integrity concern that requires a symlink to be present; it is not evidence of a remote or approval bypass.
- Recommended hardening: reject symlink output targets and, for the fixed Pro preview destination, verify the resolved parent remains within the intended Pro output directory before invoking FFmpeg. Add tests for a symlinked output file and symlinked output parent. Keep the general CLI's explicitly configurable destination semantics documented. No implementation made pending explicit approval.

### Verification and safety
- Re-fetched `src/render_dua_video.py` (blob `74b769e3309ea1ae8334701d5ec68e11ad1aaee7`) and `src/pro_orchestrator.py` (blob `a76c75e72bdc030575652f9a76f105ee91865675`) from `feature/quran-video-pro`.
- Static inspection only. No source/test changes, tests, workflow, render, ledger persistence, Telegram request/send/upload, or TikTok publishing occurred. No production branch, original Quran engine/bot, secrets, or Cron was touched.

## 2026-11-07 — Static review: audio tolerance versus final mux duration

### Finding (audio synchronization policy; no code changes)
- The renderer accepts an audio duration within ±0.75 seconds of the requested video duration. However, the final FFmpeg command always applies `-t <video duration>` to the mux.
- If accepted audio is longer than the video by up to the tolerance, FFmpeg truncates the audio at the video endpoint. If accepted audio is shorter, the output can end with a silent tail because no audio padding is applied. This behavior conflicts with the validator/docstring and error text implying that accepted audio will not be silently padded or truncated.
- The existing unit test explicitly accepts audio of 9.0 seconds for a 9.5-second video, demonstrating that shorter audio within tolerance passes; it does not test the resulting mux behavior or the positive tolerance boundary.
- This is a product-policy decision as well as a technical gap: choose whether audio must match exactly (within a much smaller codec/probe tolerance), whether short audio may leave silence, or whether controlled padding/trimming is acceptable. Then align validation, user-facing error text, FFmpeg behavior, and boundary tests. No change made pending that decision.

### Verification and safety
- Re-fetched `src/render_dua_video.py` (blob `74b769e3309ea1ae8334701d5ec68e11ad1aaee7`), `tests/test_render_dua_video.py` (blob `685937e838567c28c480262fc807268e28bde7f8`), and this log from `feature/quran-video-pro`.
- Static inspection only. No source/test changes, tests, workflow, render, ledger persistence, Telegram request/send/upload, or TikTok publishing occurred. No production branch, original Quran engine/bot, secrets, or Cron was touched.


## 2026-11-07 — Static review: HTTPS evidence URL syntax validation

### Finding (metadata-validation gap; no code changes)
- `validate_pro_media_rights._https()` checks that `urlparse()` reports the HTTPS scheme, a non-empty netloc, a non-root path, and no parsed username/password. It does not validate the parsed hostname or port, nor reject whitespace/backslashes in the authority.
- Static probes confirmed malformed values such as `https://stock.example bad/path`, `https://stock.example\\evil/path`, `https://stock.example:abc/path`, and `https://stock.example:99999/path` pass the current predicate. Accessing `.port` would raise `ValueError` for the invalid-port cases, but the validator never accesses it.
- These values can be stored as source-page or license-evidence references despite not being well-formed HTTPS URLs. This is a record-quality/validation gap, not an SSRF finding: the inspected validator does not fetch these URLs, and no permission bypass was demonstrated.
- Recommended hardening: reject control/whitespace and backslash characters, require a non-empty parsed hostname, force validation of the parsed port (catching `ValueError`), and add malformed-authority/invalid-port regression tests. Do not add an arbitrary domain allowlist unless the product's evidence policy explicitly requires one. No implementation made pending approval.

### Verification and safety
- Re-fetched `src/validate_pro_media_rights.py` (blob `9f6e8f5d1fd1ef0aa2ca9fca66f6a0f0371ce014`) and `tests/test_validate_pro_media_rights.py` (blob `36fa0acabf981e5709e333b6b72627d69df111df`) from `feature/quran-video-pro`.
- Static URL-parser probes only; no repository tests were run. No source/test changes, workflow, render, ledger persistence, Telegram request/send/upload, or TikTok publishing occurred. No production branch, original Quran engine/bot, secrets, or Cron was touched.


## 2026-11-07 — Static review: malformed Telegram sendVideo response handling

### Finding (ambiguous-outcome reporting gap; no code changes)
- In `send_pro_preview_telegram.send_preview()`, the HTTP response is JSON-decoded inside the transport `try`, but the code then calls `result.get("ok")` without first confirming that the decoded top-level JSON value is a dictionary.
- A valid JSON response whose top-level value is `null`, a list, or a string therefore raises an unhandled `AttributeError` instead of the sender's explicit `RuntimeError` stating that the send outcome may be uncertain. Since this happens after the single sendVideo request, a caller may not receive the important do-not-retry warning even though Telegram may already have accepted the upload.
- The sender does not automatically retry, and the orchestrated delivery cycle is designed to treat send exceptions as uncertain; this finding concerns the direct sender's malformed-response reporting and consistency, not an observed duplicate-send bypass.
- Recommended hardening: require `isinstance(result, dict)` before accessing response fields, and raise the same explicit uncertain-outcome error for any malformed top-level or nested sendVideo response. Add tests for JSON `null`, list, and string responses after the upload request; assert exactly one sendVideo call and an explicit uncertain-outcome message. No implementation made pending approval.

### Verification and safety
- Re-fetched `src/send_pro_preview_telegram.py` (blob `072cd2d4facbae696c40ec94d0d499a6aeb339fd`) and `tests/test_send_pro_preview_telegram.py` (blob `6844c2549223f95942552b740026010be5acc475`) from `feature/quran-video-pro`.
- Static inspection only. No repository tests were run. No source/test changes, workflow, render, ledger persistence, Telegram request/send/upload, or TikTok publishing occurred. No production branch, original Quran engine/bot, secrets, or Cron was touched.


## 2026-11-07 — Static review: shared manifest enum types and repeat_count booleans

### Finding (malformed-manifest handling; no code changes)
- `validate_content_manifest()` performs set-membership checks on several JSON-controlled values before checking that they are strings: top-level `content_type`, `visual.template`, `audio.kind`, and dua/dhikr item `kind`. If any of these fields is a JSON array or object, Python raises `TypeError` ("unhashable type") rather than the validator's intended controlled `SystemExit`.
- The Pro orchestrator catches `FileNotFoundError`, `ValueError`, `LookupError`, and `SystemExit`, but not `TypeError`. Consequently, such malformed candidate/production metadata can escape the normal structured `blocked` result and produce a traceback. It still stops before rendering; no approval bypass was identified.
- A separate strict-type issue exists for `repeat_count`: the validator uses `isinstance(repeat_count, int)`, which accepts JSON booleans because Python's `bool` subclasses `int`. Thus `true` is accepted as repeat count 1, although the schema says a positive integer. This is a data-contract correctness issue, not a render/approval bypass.
- Recommended hardening: require strings before enum/set membership; reject booleans explicitly for integer-only `repeat_count`; add regression tests with list/object enum values and `repeat_count: true/false`. Keep the orchestrator's fail-closed behavior and return a structured blocked result for malformed input. No implementation made pending approval.

### Verification and safety
- Re-fetched `src/validate_content_manifest.py` (blob `5146070fea6ab8ed65cd6d192e8a25547260ba1`), `tests/test_validate_content_manifest.py` (blob `7914f2c7f0eacc298379b87687377e935cff19d6`), and `src/pro_orchestrator.py` (blob `a76c75e72bdc030575652f9a76f105ee91865675`) from `feature/quran-video-pro`.
- Static inspection only. No repository tests were run. No source/test changes, workflow, render, ledger persistence, Telegram request/send/upload, or TikTok publishing occurred. No production branch, original Quran engine/bot, secrets, or Cron was touched.


## 2026-11-07 — Static review: unvalidated Arabic title type in dua renderer

### Finding
- Re-inspected `src/render_dua_video.py` (blob `74b769e3309ea1ae8334701d5ec68e11ad1aaee7`) and `src/pro_orchestrator.py` (blob `a76c75e72bdc030575652f9a76f105ee91865675`).
- The renderer passes `data.get("title_ar", ...)` directly to `create_overlay()`, which passes it to Pillow's `draw.text()`. The shared manifest validator does not require `title_ar` to be a string.
- A malformed JSON value such as an array/object can therefore raise an uncaught `TypeError` during rendering instead of producing the orchestrator's structured blocked result. This is a fail-closed reliability/reporting gap; it does not bypass approval or publishing safeguards.

### Recommendation
- Validate `title_ar` as a non-empty string (or apply a deliberate safe default) before rendering.
- Add regression coverage for array/object title values and confirm malformed manifests produce a structured blocked result without starting FFmpeg.
- Keep the earlier enum-type `TypeError` finding in scope; both point to hardening manifest type checks and the orchestrator's error boundary.

### Validation status and restrictions
- Static source inspection only; no code or test files changed and no tests were run.
- No render, workflow, ledger persistence, Telegram send, TikTok publish, bot/secret/Cron change, or production-branch change was performed.
- This entry was recorded on `feature/quran-video-pro` only.


## 2026-11-07 — Static review: single-token Arabic line can exceed safe width

### Finding
- Re-inspected `src/render_dua_video.py` (blob `74b769e3309ea1ae8334701d5ec68e11ad1aaee7`) and `tests/test_render_dua_video.py` (blob `685937e838567c28c480262fc807268e28bde7f8`).
- In `create_overlay()`, when a word by itself is wider than 900 pixels, the wrapping loop assigns it to `current` without checking that single-word width. The later acceptance condition checks only line count and total line height, not the width of every completed line.
- A long unbroken Arabic token can therefore be accepted and drawn beyond the intended safe text width, even after the font is reduced to its minimum size. Existing renderer tests cover missing/empty and overlong multiword text, but not a single token wider than the available line width.

### Recommendation
- After wrapping, measure every completed line and fail closed if any line exceeds the safe width; preserve exact Arabic wording and do not silently truncate or rewrite it.
- Add a regression test with a single token whose measured width remains above 900 pixels at the minimum font size.

### Validation status and restrictions
- Static source/test inspection only; no code or test files changed and no tests were run.
- No render, workflow, ledger persistence, Telegram send, TikTok publish, bot/secret/Cron change, or production-branch change was performed.
- This entry was recorded on `feature/quran-video-pro` only.


## 2026-11-07 — Static review: malformed rotation history entries can escape preflight

### Finding
- Re-inspected `src/pro_orchestrator.py` (blob `a76c75e72bdc030575652f9a76f105ee91865675`), `src/content_rotation.py` (blob `2ad7ca31cf8b5c54edc362c64f845fb4412fbb6a`), and `tests/test_pro_orchestrator.py` (blob `b86fb7dec3ec16f47b6eed51ab6d520fec5b36da`).
- `load_history()` validates only that `history["content"]` is a list. It does not validate that each entry is a manifest ID string.
- `choose_manifests()` / `choose_manifest()` convert the history entries to a set. A JSON list or object nested inside the history list is unhashable and raises `TypeError`.
- The orchestrator's preflight exception handlers do not catch `TypeError`, so malformed persisted history can escape the structured `blocked` response. No render or send is triggered by this path; this is a preflight robustness/reporting issue.

### Recommendation
- Validate every history entry as a non-empty string before rotation selection; reject malformed history with a controlled validation error rather than silently coercing values.
- Add tests for list/object entries in the history array and assert the orchestrator returns a structured blocked result with no render attempt.

### Validation status and restrictions
- Static source/test inspection only; no code or test files changed and no tests were run.
- No render, workflow, ledger persistence, Telegram send, TikTok publish, bot/secret/Cron change, or production-branch change was performed.
- This entry was recorded on `feature/quran-video-pro` only.


## 2026-11-07 — Static review: dua source URLs are checked only by HTTPS prefix

### Finding
- Re-inspected `src/validate_content_manifest.py` (blob `5146070fea6ab8ed65cd6d192e8a25547260ba1`) and `tests/test_validate_content_manifest.py` (blob `7914f2c7f0eacc298379b87687377e935cff19d6`).
- For each dua/dhikr item, source validation currently uses `str(item.get("source_url", "")).startswith("https://")` rather than parsing and validating the URL.
- Values such as `https://` or `https:///path` satisfy this prefix check despite lacking a valid hostname. The current test covers an empty URL but not malformed HTTPS URLs.
- This can allow a malformed religious-source reference through manifest validation. It does not establish source authenticity; the validator already documents that it does not authenticate religious wording.

### Recommendation
- Require a string and parse it with `urlparse`; require scheme `https`, a valid non-empty hostname, and a non-empty asset/article path where appropriate. Consider consistent URL rules with the media-rights validator while keeping source-specific requirements explicit.
- Add regression tests for `https://`, `https:///path`, whitespace/invalid authority, and a valid HTTPS source.

### Validation status and restrictions
- Static source/test inspection only; no code or test files changed and no tests were run.
- No render, workflow, ledger persistence, Telegram send, TikTok publish, bot/secret/Cron change, or production-branch change was performed.
- This entry was recorded on `feature/quran-video-pro` only.

## 2026-11-07 — Static review: renderer output can collide with an input file

### Finding (destructive output-path collision; no code changes)
- Re-fetched `src/render_dua_video.py` from `feature/quran-video-pro` (blob `74b769e3309ea1ae8334701d5ec68e11ad1aaee7`) and re-inspected the CLI/render path.
- The renderer accepts a caller-controlled `--output` path, creates its parent directory, then passes that path to FFmpeg with `-y`, which permits overwriting an existing file.
- Before invoking FFmpeg, the renderer does not compare the resolved output path with the manifest path or the validated background/audio input paths. If a caller accidentally or deliberately supplies one of those input paths as `--output`, FFmpeg may overwrite an input asset (or the manifest) while using it as an input.
- This is a local CLI path-integrity/destructive-overwrite risk. It is not evidence of remote exploitation or an approval/publishing bypass.

### Recommendation
- Resolve the manifest, output, background, and optional audio paths before rendering; reject the operation if the output resolves to any input path.
- Consider also rejecting symlink output targets and validating the resolved output location against the intended Pro output directory when invoked through the orchestrator.
- Add regression tests proving collisions with the manifest, background, and audio are rejected before FFmpeg is invoked. No implementation made pending explicit approval.

### Verification and safety
- Re-fetched `src/render_dua_video.py` from `feature/quran-video-pro` (blob `74b769e3309ea1ae8334701d5ec68e11ad1aaee7`) immediately before recording this finding.
- Static source inspection only. No source/test changes, tests, workflow, render, ledger persistence, Telegram request/send/upload, or TikTok publishing occurred.
- No production branch, original Quran engine/bot, secrets, or Cron was touched.

## 2026-11-07 — Static review: caption output can overwrite its source manifest

### Finding (destructive CLI output-path collision; no code changes)
- Re-fetched `src/prepare_pro_telegram_caption.py` (blob `9551f47852d1460b962b266870952a44bf920e4a`) and `tests/test_prepare_pro_telegram_caption.py` (blob `e483679cb22a64e091e9b8199de0a19032fed353`) from `feature/quran-video-pro`.
- The caption CLI accepts independent `--manifest` and `--output` paths, reads the manifest, then writes the generated caption JSON directly to the output path. It does not reject the case where both arguments resolve to the same file.
- If the same path is supplied for both arguments, the command replaces the original validated content manifest with the caption payload. The current test covers rejection of a non-Pro manifest but does not cover output/manifest path collision.
- This is a local operator-error/destructive-overwrite risk; it is not a Telegram send or publishing bypass.

### Recommendation
- Resolve both paths and reject equality (including equivalent relative paths and symlink-resolved aliases) before writing.
- Consider refusing an existing symlink output target, and add tests asserting a collision fails without changing the manifest bytes. No implementation made pending explicit approval.

### Verification and safety
- Static source/test inspection only; no tests or caption-generation command were run.
- No source/test changes, workflow, render, ledger persistence, Telegram request/send/upload, or TikTok publishing occurred.
- No production branch, original Quran engine/bot, secrets, or Cron was touched.


## 2026-11-07 — Static review: malformed Pro delivery metadata and ledger types

### Findings (documentation only; no code changes)

1. **Rotation batch count accepts a boolean**
   - In `src/content_rotation.py`, `choose_manifests()` checks `isinstance(count, int)` and `count < 1`. Since Python booleans are integers, `count=True` is accepted as a batch size of one, despite the positive-integer contract.
   - Recommended hardening: reject booleans explicitly (or require `type(count) is int`) and add `True`/`False` regression cases.

2. **Local delivery ledger has weak JSON type guards**
   - In `src/pro_delivery_ledger.py`, `load_ledger()` checks `data.get("version") != 1`; JSON `true` compares equal to integer 1 and is accepted as a schema version.
   - The entry-state check uses set membership without first requiring a string. A JSON list/object in `state` is unhashable and raises `TypeError` instead of the intended controlled `ValueError`.
   - Recommended hardening: require an exact integer schema version (excluding booleans) and a string state before membership validation; add malformed-type regression cases.

3. **Caption JSON root is not checked in the standard delivery path**
   - `src/pro_delivery_cycle.py` parses the caption JSON and immediately calls `.get()` on the root value. `null`, arrays, or scalar JSON values therefore raise `AttributeError` rather than a controlled input-validation error.
   - `src/send_pro_telegram.py` has the same root-shape assumption: `build_caption()` calls `.get()`, and the sender later reads fields from the same decoded value. The malformed input is rejected only accidentally by an exception, not by an explicit schema check.
   - Recommended hardening: require the decoded caption root to be a dictionary in both entry points before accessing fields; add null/list/scalar tests and verify no reservation or Telegram request occurs for malformed captions.

4. **Malformed Telegram sendVideo JSON root is not normalized to an uncertain outcome**
   - In `src/send_pro_telegram.py`, the decoded sendVideo response is accessed with `.get("ok")` without checking that the top-level JSON value is a dictionary.
   - A valid JSON response such as `null`, a list, or a string raises `AttributeError` after the upload request. The exception path does move the ledger to `uncertain` and does not auto-retry, so the duplicate-send protection remains; the gap is the missing explicit, consistent ambiguous-outcome diagnostic.
   - Recommended hardening: check the response root type and raise a clear uncertain-outcome error; test malformed roots while asserting exactly one sendVideo request and an uncertain ledger state.

5. **Candidate-preview manifest root is not checked before field access**
   - In `src/pro_preview_delivery_cycle.py::preflight()`, manifest JSON is decoded and `data.get("id")` is called immediately. A JSON null/list/scalar root raises `AttributeError` instead of the preflight's controlled `ValueError`.
   - Recommended hardening: require a dictionary immediately after decoding and add malformed-root tests that assert no reservation, persistence, or Telegram request is attempted.

6. **Preview ledger enum fields can raise TypeError on malformed JSON types**
   - In `src/pro_preview_send_ledger.py::_validate_entry()`, `content_type` and `state` are checked with set membership without explicit string type checks. A list/object value in either field raises `TypeError` instead of the validator's controlled `ValueError`.
   - The existing ledger tests cover unsupported schema versions and hashes, but do not cover list/object enum values.
   - Recommended hardening: require strings before set membership and add list/object regression cases for both fields.

### Source verification
- Re-fetched the reviewed files from `feature/quran-video-pro`: `src/content_rotation.py` (blob `2ad7ca31cf8b5c54edc362c64f845fb4412fbb6a`), `src/pro_delivery_ledger.py` (blob `6466ba9faee6c8c76dec47a216aac9818f4f5314`), `src/pro_delivery_cycle.py` (blob `f84580d8b58cf3debc959946ff7284be5fb3734c`), `src/send_pro_telegram.py` (blob `4d232e5fdeb947b977dc099ca610178beb01fd93`), `src/pro_preview_delivery_cycle.py` (blob `a09fb972d455b9ac077035074d30e43e110e4d50`), and `src/pro_preview_send_ledger.py` (blob `4165e0b9fcf12d5666a867511392bf2f361583ad`).
- Relevant tests were re-fetched for static comparison: `tests/test_pro_delivery_cycle.py`, `tests/test_send_pro_telegram.py`, `tests/test_pro_preview_delivery_cycle.py`, and `tests/test_pro_preview_send_ledger.py`. No tests were executed.

### Safety and status
- These are input-validation and error-reporting robustness findings; no approval bypass, automatic retry, or TikTok publishing path was demonstrated.
- Static review only. No source/test files changed, no tests or workflows were run, no render or ledger persistence was performed, and no Telegram request/send/upload or TikTok publishing occurred.
- Only `feature/quran-video-pro` was updated. The production branch, original Quran engine/bot, secrets, and Cron were not touched.


## 2026-11-07 — Repair 1: reject boolean content-rotation batch counts

### Code changes
- `src/content_rotation.py`: changed the `count` guard to require `type(count) is int`, so Python booleans (`True`/`False`) no longer pass as integer batch sizes.
- `tests/test_content_rotation.py`: added regression coverage proving both boolean values raise the documented `ValueError`.

### Verification
- Source, test, and log updates were committed to `feature/quran-video-pro` only.
- GitHub refetch verification and test execution are pending; no passing test result is claimed here.
- No workflow, render, ledger persistence, Telegram request/send/upload, or TikTok publishing was run.
- Production branch, original Quran engine/bot, secrets, and Cron remain untouched.


## 2026-11-07 — Repair 2: fail-closed Pro manifest enum and repeat-count validation

### Code changes
- `src/validate_content_manifest.py`: validate JSON-controlled `content_type`, visual `template`, audio `kind`, and item `kind` as strings before set membership. This converts malformed list/object enum values into the validator's controlled `SystemExit` path instead of leaking `TypeError`.
- The same validator now requires `repeat_count` to be an exact integer, rejecting JSON booleans.
- `tests/test_validate_content_manifest.py`: added malformed enum and `true/false` repeat-count regression cases.

### Verification
- Source and test changes were committed to `feature/quran-video-pro` only.
- Automated test execution and workflow validation are still pending; no passing result is claimed.
- No rendering, Telegram request/send/upload, or TikTok publishing was performed. Production branch, original Quran engine/bot, secrets, and Cron remain untouched.


## 2026-11-07 — Repair 3: reject non-finite timings and unsafe single-line text

### Code changes
- `src/render_dua_video.py`: ffprobe durations and item durations now reject NaN and positive/negative infinity, in addition to existing invalid values.
- Arabic overlay rendering now requires a non-empty string title and checks the measured width of every wrapped line before accepting a font size. A single oversized Arabic token can no longer bypass the line-width limit.
- `tests/test_render_dua_video.py`: added NaN/infinity item-duration cases and ffprobe non-finite duration regression cases.

### Verification
- Source and test changes were committed to `feature/quran-video-pro` only.
- Automated tests have not yet been executed; no passing test result is claimed.
- No render, Telegram request/send/upload, or TikTok publishing was performed. Production branch, original Quran engine/bot, secrets, and Cron remain untouched.


## 2026-11-07 — Repair 4: harden both Pro delivery ledgers against malformed JSON types

### Code changes
- `src/pro_delivery_ledger.py`: schema version must be an exact integer (JSON `true` no longer aliases version 1); entry states and transition names must be strings before membership checks; content type is also type-checked.
- `src/pro_preview_send_ledger.py`: content type/state are checked as strings before enum membership, and transition/content-type inputs are type-checked.
- Added regression tests for boolean schema version, list/object states, and list/object enum fields.

### Verification
- Both ledger source files and their regression tests were committed to `feature/quran-video-pro` only.
- GitHub refetch verification and execution of the test suite remain pending; no test pass is claimed.
- No Telegram call, media render, or publishing was performed. Production branch and original Quran system remain untouched.


## 2026-11-07 — Repair 5: reject malformed Pro caption, manifest, and Telegram JSON

### Source changes
- `src/pro_delivery_cycle.py`: reject caption JSON roots that are not objects before reading manifest/content fields or reserving a delivery.
- `src/send_pro_telegram.py`: validate caption data is an object; validate Telegram's decoded sendVideo response is an object before reading confirmation fields. A malformed response is treated as an unconfirmed/uncertain send, not as success.
- `src/pro_preview_delivery_cycle.py`: reject non-object preview manifest JSON before candidate lookup or reservation.

### Regression tests added
- `tests/test_pro_delivery_cycle.py`: non-object caption JSON roots (`null`, array, string) are rejected before reservation and sender invocation.
- `tests/test_send_pro_telegram.py`: caption builder rejects non-object inputs; a Telegram `null` response is rejected and the ledger is advanced to `uncertain`.
- `tests/test_pro_preview_delivery_cycle.py`: non-object manifest JSON roots are rejected before private-chat verification, reservation, persistence, or send.

### Verification status and safety boundary
- Source and test updates were committed to `feature/quran-video-pro`; the files must be refetched to verify the committed content.
- Tests have **not** been executed in this repair step; no passing test result is claimed.
- No Telegram request, production render, TikTok publish, production workflow, or other branch was triggered.


## 2026-11-07 — Repair 6: finite duration validation and preview-sender JSON guards

### Source changes
- `src/pro_orchestrator.py`: centralize positive-duration validation and reject NaN, positive/negative infinity, booleans, non-numeric values, and integer-to-float overflow for both rotation plans and candidate-preview plans. This closes the NaN comparison gap where `value <= 0` and a total-duration cap comparison can both be false.
- `src/send_pro_preview_telegram.py`: require preview manifest input to be a JSON object before field access; require Telegram sendVideo response to be an object before reading its confirmation status.

### Regression tests added
- `tests/test_pro_orchestrator.py`: rotation and preview planning reject NaN and both infinities.
- `tests/test_send_pro_preview_telegram.py`: preview caption validation rejects non-object manifests; a Telegram `null` send response is treated as unconfirmed, not success.

### Verification and safety
- Changes were committed on `feature/quran-video-pro`; content refetch verification is still required.
- Tests have not been executed in this repair step; no passing result is claimed.
- No production render, Telegram send, TikTok publish, or other-branch write was performed.


### Follow-up verification (2026-11-07)
- Refetched the Repair 5 and Repair 6 source/test files from `feature/quran-video-pro`; confirmed the expected guards and regression-test methods are present in the committed branch files.
- The latest visible successful Pro safety workflow run (#3, commit `f8e0d76a151e7241901f21b9c257de1d0a7a97fb`) predates these new commits, so it is historical evidence only and does **not** validate the current branch head.
- No workflow dispatch/test-run action is available in the connected GitHub operations used here. Therefore the new tests remain unexecuted and the current head is not certified by CI.

## 2026-11-07 — Repair 7: close gaps in the Pro offline safety workflow

### Changes
- Updated `.github/workflows/pro-safety-tests-manual.yml` to include the existing Pro-specific suites that were previously omitted: `test_pro_preview_send_ledger.py`, `test_persist_pro_preview_ledger.py`, `test_content_rotation.py`, and `test_prepare_pro_telegram_caption.py`.
- Kept the workflow manual-only, restricted to the exact `feature/quran-video-pro` branch, with read-only repository permissions and no Telegram or TikTok actions.
- Deliberately excluded `test_content_rotation_repository_safety.py`, which is tied to the Quran production repository path rather than this Pro dua/dhikr workflow.

### Validation
- Workflow source was fetched before editing and updated using its current blob SHA.
- The workflow has not been dispatched; these test suites have not yet been executed. No passing CI result is claimed.
- No production render, Telegram send, TikTok publish, secret change, or other-branch write was performed.

## 2026-11-07 — Repair 8: reject malformed preview content types before set membership

### Finding and fix
- Review of the candidate-preview sender found that an untrusted manifest with a list/dict `content_type` could raise an uncaught `TypeError` during set membership rather than a controlled validation error.
- Added explicit string-type validation in `src/send_pro_preview_telegram.py` before checking allowed values.
- Applied the same defensive check in `src/pro_orchestrator.py` candidate-preview preflight, so malformed manifests fail closed with the intended `SystemExit` message.
- Added regression tests covering list, object, integer and boolean content types in both modules.

### Validation and safety
- Source and test files were updated on `feature/quran-video-pro` only.
- Changes were fetched from GitHub before editing and will be refetched for verification.
- Tests have not been executed; no pass result is claimed.
- No production rendering, Telegram request, TikTok publishing, secret change, or write to another branch was performed.


## Repair 9 — reject malformed media-rights enum values
- Hardened `validate_pro_media_rights.py` against untrusted JSON values that are lists/objects where enum strings are required: manifest audio kind, manifest asset media type, rights-record media type, and license-evidence kind. These now fail closed with the validator's controlled `ValueError` instead of leaking an uncaught `TypeError` from set membership.
- Added defensive validation for the planned-use selector and a regression test matrix covering list/object values across those fields.
- Updated files: `src/validate_pro_media_rights.py`, `tests/test_validate_pro_media_rights.py`.
- Tests: added but not executed in this session; no passing result claimed.
- Safety: Pro branch only; no production render, Telegram request, TikTok publication, or secret changes.


## Repair 10 — guard public Pro content-type inputs
- Added explicit string-type validation at the Pro rotation planner and persisted-reservation sender boundary. List/object/number/boolean inputs now produce the intended controlled ValueError instead of a set-membership TypeError.
- Added regression coverage for malformed values in both entry points.
- Updated files: `src/pro_orchestrator.py`, `src/pro_delivery_ledger.py`, `tests/test_pro_orchestrator.py`, `tests/test_pro_delivery_ledger.py`.
- Tests added but not executed in this session; no passing result claimed.
- Pro branch only; no render, Telegram send, TikTok publication, or secret changes.


## Repair 11 — validate content-rotation inputs
- Hardened `content_rotation.py` against non-string content types, malformed recent-history identifiers (including unhashable list/object entries), and non-string rotation keys. Invalid values now fail with explicit ValueError rather than uncaught TypeError/AttributeError.
- Added regression tests for list/object/number/boolean content types, malformed recent IDs, and invalid rotation keys.
- Updated files: `src/content_rotation.py`, `tests/test_content_rotation.py`.
- Tests added but not executed in this session; no passing result claimed.
- Pro branch only; no rendering, Telegram delivery, TikTok publication, or secret changes.


## Repair 12 — validate delivery-ledger identifiers
- Added a shared manifest-ID guard before ledger lookup/mutation in reservation verification, state transitions, and human reconciliation. Empty, non-string, list, object, numeric, and boolean identifiers now fail with a clear ValueError rather than causing unhashable-key failures or ambiguous lookups.
- Added regression coverage for all three ledger operations.
- Updated files: `src/pro_delivery_ledger.py`, `tests/test_pro_delivery_ledger.py`.
- Tests added but not executed in this session; no passing result claimed.
- Pro branch only; no render, Telegram send, TikTok publication, or secret changes.

### Repair 13: Validate preview-ledger transition identifiers
- `src/pro_preview_send_ledger.py`: `transition` now validates candidate_id with the same safe 1–80 character identifier rule used by reservation before loading or looking up the ledger entry.
- Added regression coverage for list, object, number, boolean, and empty identifiers; malformed values now fail with controlled ValueError rather than leaking TypeError or ambiguous lookup behavior.
- Source, tests, and this log entry were committed on `feature/quran-video-pro` only. Test execution remains unconfirmed; no Telegram send or production render was performed.

### Repair 14: Reject invalid recent-history containers
- `src/content_rotation.py`: centralized recent identifier validation for single and batch selection. Non-iterable values (including null/numbers), scalar strings/bytes, and collections containing non-string identifiers now fail with a controlled ValueError.
- Added regression coverage for both selection APIs so malformed history cannot leak a TypeError or be interpreted character-by-character.
- Source, tests, and development log committed on `feature/quran-video-pro` only. Tests have not been executed in this environment; no production render or Telegram send was performed.

### Repair 15: Validate persisted production-ledger entry fields
- `src/pro_delivery_ledger.py`: ledger loading now validates each entry's content type, run ID, timestamps, and Telegram receipt consistency in addition to its state. Delivered entries require a positive non-boolean message ID; reserved/uncertain entries cannot carry a receipt.
- Added malformed persisted-ledger regression coverage for collection-valued enums/IDs, missing or malformed timestamps, and boolean Telegram message IDs.
- Source, tests, and log committed on `feature/quran-video-pro` only. No test execution, production render, or Telegram send is claimed.

### Repair 16: Reject symlinked production-ledger persistence paths
- `src/persist_pro_ledger.py`: production ledger persistence now rejects a symlinked `data/` directory or symlinked ledger file before staging, matching the stricter preview-ledger persistence boundary.
- Added offline regression tests for both symlink cases. This prevents a ledger-only Git operation from following an unexpected filesystem target.
- Source, tests, and log committed on `feature/quran-video-pro` only. Tests were not executed here; no production render or Telegram send was performed.


### Repair 17: verify production-ledger persistence against the remote branch
- `src/persist_pro_ledger.py`: before staging, fetch the exact Pro branch and require local HEAD to match `origin/feature/quran-video-pro`. This prevents a stale local checkout from creating a ledger commit on top of outdated history.
- After committing and pushing the ledger-only change, fetch again and verify local HEAD equals the remote-tracking HEAD. A successful push command alone is no longer treated as proof of remote persistence.
- `tests/test_persist_pro_ledger.py`: added regression coverage for stale local HEAD rejection and post-push remote mismatch; updated the expected Git command sequence and retained the exact-path, symlink, and push-failure checks.
- Verification: source and tests were committed to `feature/quran-video-pro` and are being refetched for content verification. Tests have not been executed; no passing result is claimed.
- Safety: no workflow was dispatched, no render or Telegram request/send occurred, and no production branch, original Quran engine/bot, secrets, Cron, or TikTok publishing setting was touched.


### Repair 18: redact Telegram bot tokens from production-sender errors
- `src/send_pro_telegram.py`: transport/response exceptions are no longer re-raised with their original messages or chained causes. urllib exceptions can include the token-bearing Telegram API URL; the sender now reports only the exception class and a generic uncertain-outcome message, while preserving the ledger's blocking `uncertain` state and no-retry behavior.
- `tests/test_send_pro_telegram.py`: updated the transport-failure regression to inject a fake token-bearing URL and assert the token is absent from the surfaced exception and no cause is chained. The test also confirms the ledger remains uncertain.
- Source and regression test committed on `feature/quran-video-pro` only. Files were fetched before edits; final refetch verification follows.
- Tests have not been executed in this session. No Telegram request/send, production render, TikTok publication, or secret change was performed.


### Repair 19: cover token redaction when ledger recovery itself fails
- `tests/test_send_pro_telegram.py`: added a failure-path regression where both the Telegram transport exception and the attempt to mark the reservation `uncertain` contain a fake bot token. The test asserts the surfaced error contains no token and has no chained cause.
- This closes the secondary exception path introduced by Repair 18: failure to update the ledger must still keep the reservation blocking without leaking a secret-bearing transport or filesystem error.
- Test and log committed on `feature/quran-video-pro` only. Test execution is not available/has not been performed in this session; no Telegram request, render, TikTok publication, or secret change occurred.


### Test-suite consistency correction after Repair 18
- Review found one pre-existing assertion in `tests/test_send_pro_telegram.py` still expected the raw `TimeoutError`, while Repair 18 intentionally converts transport failures to a generic redacted `RuntimeError`.
- Updated that test to assert the new safe error contract, including that the original timeout text is not exposed and no exception cause is chained. This prevents a predictable failure in the sender test suite.
- Test and log committed on `feature/quran-video-pro` only. Tests have not yet been executed.


### Repair 20: regression coverage for invalid Telegram delivery receipts
- Added sender tests for Telegram responses whose `message_id` is boolean, zero, negative, a string, or null.
- Each malformed receipt must be rejected and the delivery ledger must remain `uncertain`, preventing the workflow from treating an unverified response as a confirmed delivery or retrying blindly.
- Test and log committed on `feature/quran-video-pro` only. Tests have not yet been executed; this is regression coverage, not a passing test claim.


### Repair 21: redact delivery-cycle exception messages and causes
- `src/pro_delivery_cycle.py` no longer propagates arbitrary sender exception messages through the orchestration boundary. It reports only the exception class and a safe generic outcome; it does not chain the original error.
- If persisting the uncertain outcome fails, the cycle reports only the persistence exception class and does not chain the underlying Git/transport error, which could contain credential-bearing remote URLs. The already-persisted reservation remains the duplicate-send barrier.
- Updated cycle regressions to check sender-error redaction and a fake credential-bearing remote URL in persistence failure.
- Changes are committed on `feature/quran-video-pro` only. Tests have not yet been executed.


### Repair 22: refuse symlinked delivery-ledger lock files
- Hardened `src/pro_delivery_ledger.py` so the inter-process lock is opened without following symlinks where the platform supports `O_NOFOLLOW`, and the opened descriptor must be a regular file.
- Added a regression test proving a symlinked lock path is rejected before the ledger is created and the external target remains untouched.
- Kept the existing cross-platform Windows/POSIX locking behavior.
- Committed on `feature/quran-video-pro` only. Tests have not been executed; syntax and runtime remain unverified until the Pro safety suite can run on the current HEAD.


### Repair 23: avoid rewriting an existing Windows lock byte
- Corrected the Windows lock-file initialization check in `src/pro_delivery_ledger.py`: inspect the file length by seeking to end before writing the initial lock byte. The previous seek-to-zero followed by `tell()` always returned zero and rewrote byte zero on every lock acquisition.
- The change preserves the existing cross-platform locking mechanism and avoids modifying an already initialized lock file unnecessarily.
- Source committed on `feature/quran-video-pro` only. Tests remain unexecuted; no workflow, render, Telegram send, or TikTok publication was run.


### Repair 24: reject symlinked delivery-ledger paths before resolution
- Review found that `run_delivery_cycle` called `Path.resolve()` before checking whether the supplied ledger file or its `data/` directory was a symlink. Resolving first can hide the symlink and make an external target appear to be the expected path.
- The cycle now checks the expected and supplied ledger file/parent for symlinks before resolving and comparing paths. It fails before reserving, persisting, or calling Telegram.
- Added regression coverage for both a symlinked ledger file and a symlinked `data/` directory; tests assert persistence and sender callbacks are not invoked and the external file is unchanged.
- Source, tests, and this log committed on `feature/quran-video-pro` only. Tests have not been executed; no workflow, render, Telegram send, or TikTok publication was run.


### Repair 25: refuse symlinked preview-ledger lock files
- Review found the isolated candidate-preview ledger still opened its lock path with `Path.open("a+b")`, which follows a pre-existing symlink. This left the preview ledger less protected than the production delivery ledger.
- Updated `src/pro_preview_send_ledger.py` to reject a symlinked lock path, use `O_NOFOLLOW` where available, and verify the opened descriptor is a regular file. Also corrected Windows empty-lock initialization to check file length at end-of-file before writing its initial byte.
- Added a regression test proving a symlinked lock is rejected without changing its external target or creating the ledger.
- Source, test, and log committed on `feature/quran-video-pro` only. Tests remain unexecuted; no workflow, render, Telegram send, or TikTok publication was run.


### Repair 26: harden preview-ledger persistence path checks
- The preview cycle already rejected a symlinked `data/` directory and the preview lock primitive rejected a symlinked lock file, but the standalone Git persistence helper did not independently enforce those checks before staging.
- Updated `src/persist_pro_preview_ledger.py` to reject a symlinked `data/` directory and a symlinked preview lock file before adding the ledger to Git.
- Added regression tests for both storage-path cases; they assert the helper stops before staging and the external lock target remains unchanged.
- Source, tests, and log committed on `feature/quran-video-pro` only. Tests remain unexecuted; no workflow, render, Telegram send, or TikTok publication was run.


### Repair 27: redact ambiguous preview-delivery exceptions
- Review found that `run_preview_cycle` marked unexpected sender failures uncertain but then re-raised the original exception, potentially exposing arbitrary transport details or token-bearing URLs. It also ignored a false return from the uncertainty persistence callback.
- The cycle now returns a generic, non-chained uncertainty error after successfully persisting the uncertain state. If transition or persistence cannot be confirmed, it returns a separate generic non-chained error and never leaks the underlying exception.
- Added regression tests for token-bearing sender exception redaction and failed uncertainty persistence.
- Source, tests, and log committed on `feature/quran-video-pro` only. Tests remain unexecuted; no workflow, render, Telegram send, or TikTok publication was run.


### Repair 28: align preview-cycle timeout regression with redacted errors
- After Repair 27, review found one older preview-cycle test still expected the raw `TimeoutError`, even though the cycle now deliberately converts ambiguous sender failures into a generic, non-chained `RuntimeError` after persisting `uncertain`.
- Updated the older regression to assert the safe uncertainty message, absence of the original timeout detail, and absence of an exception cause. This removes a known stale expectation and makes the test suite's intended error contract consistent.
- Test and log committed on `feature/quran-video-pro` only. Tests have not been executed; no workflow, render, Telegram send, or TikTok publication was run.


### Repair 29: redact preview-ledger Git diagnostics
- Review found the isolated preview-ledger persistence helper embedded raw Git stderr/stdout and command arguments in raised exceptions. Git diagnostics can contain credential-bearing remote URLs, and initial reservation persistence errors occur outside the sender's uncertainty-redaction boundary.
- Changed the helper to raise a generic Git-operation failure with the exit code only and no chained cause. Added a regression using a fake credential-bearing GitHub remote URL and asserted that neither the token nor host/URL detail escapes.
- Source, test, and log committed on `feature/quran-video-pro` only. Tests have not been executed; no workflow, render, Telegram send, or TikTok publication was run.


### Repair 30: refuse symlinked preview-ledger reads and writes
- Review found the preview ledger cycle checked for a symlink before loading the ledger, but the ledger primitive itself still followed a symlink when called independently (or if the path changed between the cycle check and open). This could make a local read consume an external file.
- Hardened `load_ledger` to reject symlink paths, open with `O_NOFOLLOW` where supported, and verify the opened descriptor is a regular file. Hardened `save_ledger` to reject symlinked parent/file paths before replacing the ledger.
- Added a regression proving both read and write reject a symlinked ledger and leave its external target unchanged.
- Source, test, and log committed on `feature/quran-video-pro` only. Tests have not been executed; no workflow, render, Telegram send, or TikTok publication was run.


### Repair 31: reject symlinked parent directories in preview-ledger primitives
- Follow-up review found the earlier symlink checks covered the ledger and its immediate parent, but a symlink higher in the path (or the lock file's parent path) could still redirect filesystem operations when the ledger primitive was called directly.
- Added one path-component guard and applied it before creating/opening the lock, reading the ledger, or writing/replacing it. The guard walks the absolute path and all existing ancestors.
- Added a regression that points the ledger's parent directory through a symlink and verifies reservation fails before creating any file in the external target.
- Source, test, and log committed on `feature/quran-video-pro` only. Tests have not been executed; no workflow, render, Telegram send, or TikTok publication was run.


### Repair 32: safely report post-send receipt-finalization failures
- Review found that after Telegram returned a confirmed positive `message_id`, a local `transition(..., delivered)` exception could escape with a raw filesystem diagnostic. The remote send had already succeeded, so the error needed to clearly prevent a resend.
- Wrapped the delivered-state transition and final persistence in a post-send reconciliation boundary. Failures now raise a generic message stating Telegram accepted the preview, the earlier reservation remains blocking, and the user must not resend until ledger reconciliation. Original exception text and cause are suppressed.
- Added a regression test injecting a local transition failure after a confirmed send and asserting the safe message, absent cause, and exactly one send call.
- Source, test, and this log committed on `feature/quran-video-pro` only. Tests were not executed; no workflow, render, Telegram send, or TikTok publication was run.


### Repair 33: normalize invalid UTF-8 preview-ledger reads
- Review found `load_ledger` converted filesystem and JSON syntax failures into a controlled validation error, but invalid UTF-8 bytes escaped as a raw `UnicodeDecodeError`.
- Added `UnicodeDecodeError` to the guarded read failures so corrupt/non-UTF-8 ledger content fails closed with the same generic error and no chained cause.
- Added a regression test using invalid UTF-8 bytes and asserting the safe error contract.
- Source, test, and log committed on `feature/quran-video-pro` only. Tests have not been executed; no workflow, render, Telegram request/send, TikTok publication, or secret change was performed.


### Repair 34: harden the Pro delivery ledger against symlinked ancestors and invalid UTF-8
- Review found the production delivery-ledger primitives had weaker path checks than the isolated preview ledger: direct calls could follow a symlinked ancestor, and corrupt non-UTF-8 ledger bytes escaped as a raw decoder error.
- Added a shared path-component guard before lock creation/open, ledger reads, and ledger writes. Ledger reads now use O_NOFOLLOW where supported and verify the opened descriptor is a regular file.
- Invalid UTF-8 and malformed JSON now fail closed with a generic read error without exposing decoder/parser details or chaining the original exception.
- Added regressions for invalid UTF-8 and a symlinked parent directory, asserting no ledger/lock is created in the external target.
- Source, tests, and log committed on feature/quran-video-pro only. Tests have not been executed; no workflow, render, Telegram request/send, TikTok publication, or secret change was performed.


### Repair 35: make invalid-UTF-8 ledger regressions exercise real invalid bytes
- Review found the invalid-UTF-8 regression tests added for the preview and production ledgers used a double-escaped byte literal. They wrote the printable ASCII characters `\\xff\\xfe{` rather than the invalid byte sequence `0xff 0xfe 0x7b`, so the tests did not reach the intended `UnicodeDecodeError` path.
- Corrected both tests to write actual invalid UTF-8 bytes. The production and preview ledger read guards can now be meaningfully exercised by the safety suite.
- Updated files: `tests/test_pro_delivery_ledger.py`, `tests/test_pro_preview_send_ledger.py`, and this log, on `feature/quran-video-pro` only.
- Tests have not been executed in this session; no passing result is claimed. No workflow dispatch, render, Telegram request/send, TikTok publication, or secret change was performed.


### Repair 36: require Telegram's success flag to be the boolean true
- Review found both Pro Telegram senders accepted any truthy `ok` value. A malformed response such as `{"ok":"true","result":{"message_id":77}}` could therefore be misclassified as a confirmed delivery.
- Both production and isolated-preview senders now require `result["ok"] is True` before accepting the result or message ID.
- Added regression tests for truthy non-boolean success flags. The production sender must leave its reservation uncertain; the preview sender must reject the response rather than report a confirmed preview.
- Updated files: `src/send_pro_telegram.py`, `src/send_pro_preview_telegram.py`, `tests/test_send_pro_telegram.py`, `tests/test_send_pro_preview_telegram.py`, and this log, on `feature/quran-video-pro` only.
- Tests have not been executed in this session; no passing result is claimed. No workflow dispatch, render, Telegram request/send, TikTok publication, or secret change was performed.



### Repair 37: redact production post-send receipt persistence failures
- Review found the production delivery cycle handled Telegram send ambiguity safely, but a failure while pushing the final `delivered` receipt could still expose raw persistence diagnostics. Telegram may already have accepted the MP4 at that point, so the error must not imply that another send is safe.
- Wrapped final outcome persistence in a non-chained generic error. It now states that Telegram accepted the review video, the earlier reservation remains blocking, and the ledger must be reconciled before any resend.
- Updated the regression to inject a credential-bearing Git remote URL, assert that the secret and exception cause are absent, and verify the local confirmed message receipt remains recorded while the previously pushed reservation remains the remote duplicate-send boundary.
- Updated files: `src/pro_delivery_cycle.py`, `tests/test_pro_delivery_cycle.py`, and this log, on `feature/quran-video-pro` only.
- Tests have not been executed; no workflow dispatch, render, Telegram request/send, TikTok publication, or secret change was performed.



### Repair 38: redact production ledger Git command diagnostics
- Review found `persist_pro_ledger.py` still embedded raw Git stderr/stdout and command arguments in exceptions. A failed push can include a credential-bearing remote URL, and the production helper is callable directly as well as through the delivery cycle.
- Changed the production helper to emit only a generic Git-operation failure and numeric exit code, with no chained subprocess exception and no raw command, stdout, or stderr.
- Added a regression that injects a credential-bearing GitHub remote URL into a simulated push rejection and asserts the secret, host, and exception cause are not exposed.
- Updated files: `src/persist_pro_ledger.py`, `tests/test_persist_pro_ledger.py`, and this log, on `feature/quran-video-pro` only.
- Tests have not been executed; no workflow dispatch, render, Telegram request/send, TikTok publication, or secret change was performed.



### Repair 39: correct the production Git-redaction regression fixture
- Follow-up source review caught an over-escaped newline in Repair 38's simulated staged-path output. The fixture would have supplied a literal backslash-n instead of a line terminator, so it would not model Git's actual `--name-only` output.
- Corrected the fixture to contain a real newline escape in the Python test string. No production code changed in this follow-up.
- Updated the test and this log on `feature/quran-video-pro` only.
- Tests have not been executed; no workflow dispatch, render, Telegram request/send, TikTok publication, or secret change was performed.



### Repair 40: reject symlinked production ledger lock paths
- Review found the production Git persistence helper checked the ledger file and immediate data directory but did not independently reject a symlinked lock file. A lock-path link can redirect lock operations performed by the ledger primitives, and persistence should enforce the same storage boundary.
- Added a component walk for the production ledger, data directory, and sibling lock path beneath the resolved repository root. Any symlink component now blocks persistence before Git staging.
- Added a regression that creates a symlinked production lock file and verifies persistence stops before staging and leaves the external target unchanged.
- Updated files: `src/persist_pro_ledger.py`, `tests/test_persist_pro_ledger.py`, and this log, on `feature/quran-video-pro` only.
- Tests have not been executed; no workflow dispatch, render, Telegram request/send, TikTok publication, or secret change was performed.



### Repair 41: distinguish confirmed Telegram acceptance from local receipt failure
- Review found a critical outcome-classification edge case: the production sender could receive Telegram's positive `ok: true` response and valid `message_id`, then fail while writing the local delivered receipt. The outer delivery cycle previously treated every sender exception as an ambiguous transport outcome and could label it uncertain, obscuring the fact that Telegram had already accepted the video.
- Added a dedicated `TelegramAcceptedLedgerError` raised only after confirmed Telegram acceptance when local receipt finalization fails. The outer cycle now reports a confirmed-acceptance reconciliation condition, does not attempt an uncertain transition, and does not resend; the previously persisted reservation remains blocking.
- Added sender-level and delivery-cycle regressions verifying the positive-acceptance path is kept distinct, diagnostics are redacted, and no second persistence/uncertain transition is attempted.
- Updated files: `src/send_pro_telegram.py`, `src/pro_delivery_cycle.py`, `tests/test_send_pro_telegram.py`, `tests/test_pro_delivery_cycle.py`, and this log, on `feature/quran-video-pro` only.
- Tests have not been executed; no workflow dispatch, render, Telegram request/send, TikTok publication, or secret change was performed.



### Repair 42: treat unchanged preview ledger as a successful no-op
- Review found the preview-ledger persistence helper staged the ledger and then required the staged-path list to contain exactly that file before checking whether anything had changed. When the ledger was unchanged, Git correctly returned an empty staged-path list, but the helper raised an error; its later no-change branch was unreachable.
- Changed the helper to return `False` when staging produces no changed paths, while retaining the pre-existing staged-change guard and the exact-path restriction for actual commits.
- Added a regression verifying an unchanged ledger returns a clean no-op and does not commit or push.
- Updated files: `src/persist_pro_preview_ledger.py`, `tests/test_persist_pro_preview_ledger.py`, and this log, on `feature/quran-video-pro` only.
- Tests have not been executed; no workflow dispatch, render, Telegram request/send, TikTok publication, or secret change was performed.



### Repair 43: synchronize production-ledger guard tests and cover unchanged state
- Review found two production persistence tests still expected the older, more specific symlink error messages after Repair 40 consolidated path-component rejection into one generic storage-path error. Those assertions would fail despite the intended fail-closed behavior.
- Updated both symlink regressions to assert the current generic error and added a production-ledger no-op regression verifying an unchanged ledger returns `False` without commit or push.
- Updated files: `tests/test_persist_pro_ledger.py` and this log, on `feature/quran-video-pro` only.
- Tests have not been executed; no workflow dispatch, render, Telegram request/send, TikTok publication, or secret change was performed.



### Repair 44: align push-failure regression with redacted Git errors
- Review found the production ledger push-failure test still expected raw Git stderr (`remote rejected push`), while Repair 38 intentionally replaced all raw Git diagnostics with a generic, non-chained error to prevent credential-bearing remote URL leakage.
- Updated the regression to expect the generic Git-operation failure and verify the raw stderr and exception cause are not exposed.
- Updated files: `tests/test_persist_pro_ledger.py` and this log, on `feature/quran-video-pro` only.
- Tests have not been executed; no workflow dispatch, render, Telegram request/send, TikTok publication, or secret change was performed.



### Repair 45: reject malformed Telegram configuration types before preview delivery
- Review found preview sender configuration validation called string methods before checking input types. A non-string token or chat ID therefore failed with an incidental `AttributeError` instead of a controlled pre-network validation error.
- Added explicit string-type checks for the preview sender and private-chat verifier; added a regression covering null and numeric token/chat values and asserting that no Telegram request is made.
- Updated files: `src/send_pro_preview_telegram.py`, `tests/test_send_pro_preview_telegram.py`, and this log, on `feature/quran-video-pro` only.
- Tests have not been executed; no workflow dispatch, render, Telegram request/send, TikTok publication, or secret change was performed.



### Repair 46: normalize malformed HTTPS URLs in media-rights validation
- Review found `urllib.parse.urlparse` / parsed-authority access can raise `ValueError` for malformed URL authorities (for example an unterminated IPv6 literal). The rights gate failed closed, but leaked a raw parser exception instead of its controlled validation error.
- Wrapped URL parsing and authority/port validation, require a hostname, and added a malformed-IPv6 source URL regression.
- Updated files: `src/validate_pro_media_rights.py`, `tests/test_validate_pro_media_rights.py`, and this log, on `feature/quran-video-pro` only.
- Tests have not been executed; no workflow dispatch, render, Telegram request/send, TikTok publication, or secret change was performed.



### Repair 47: constrain production manifest IDs before constructing MP4 paths
- Review found production `build_plan` only checked that a manifest ID was a non-empty string, then `render_plan` interpolated it into an output filename. A slash/traversal-bearing ID could influence the output path outside the intended filename shape.
- Applied the same strict 1-80 ASCII filename-component allowlist already used by candidate preview IDs, and added a regression rejecting a traversal-style production manifest ID before rendering.
- Updated files: `src/pro_orchestrator.py`, `tests/test_pro_orchestrator.py`, and this log, on `feature/quran-video-pro` only.
- Tests have not been executed; no workflow dispatch, render, Telegram request/send, TikTok publication, or secret change was performed.



### Repair 48: validate asset-rotation catalog and argument shapes
- Review found asset rotation assumed the JSON catalog root and per-kind entries were dictionaries/lists, and attempted set construction on unvalidated recent IDs. Malformed inputs could leak incidental exceptions instead of controlled fail-closed errors.
- Added explicit validation for asset kind, rotation key, recent-ID iterable/string members, UTF-8 JSON, catalog object shape, and per-kind list shape. Asset URL fields must be strings before HTTPS-prefix checks.
- Added regressions for malformed catalog roots/entries and invalid rotation arguments.
- Updated files: `src/asset_rotation.py`, `tests/test_asset_rotation.py`, and this log, on `feature/quran-video-pro` only.
- Tests have not been executed; no workflow dispatch, render, Telegram request/send, TikTok publication, or secret change was performed.



### Repair 49: require literal boolean approval for audio rights gates
- Review found dua/dhikr audio approval, rights, exact-recording review, and ambient user-approval checks accepted arbitrary truthy values (for example the string `"false"`). Quran rights-candidate parsing also assumed a list and string status values.
- Changed approval gates to require literal `true`; Quran license research candidates must be a list and only string statuses can establish an approved status.
- Added regressions for string-valued false flags, malformed candidate collection shape, and non-string candidate status; corrected the fixture so the malformed candidate path is actually exercised.
- Updated files: `src/validate_content_manifest.py`, `tests/test_validate_content_manifest.py`, and this log, on `feature/quran-video-pro` only.
- Tests have not been executed; no workflow dispatch, render, Telegram request/send, TikTok publication, or secret change was performed.


### Repair 50: require literal boolean review for exact Quran recordings
- Follow-up review of Repair 49 found the Quran exact-recording review check still accepted truthy non-boolean values in the top-level audio field or per-candidate records. It also iterated the candidate field before validating that it was a list, so a malformed null value could leak a raw type error.
- Candidate-list shape is now validated before iteration, and exact-recording review is accepted only when the top-level or candidate flag is literally `true`.
- Added regressions for string-valued `"false"` review flags at both locations and a null candidate collection.
- Updated `src/validate_content_manifest.py`, `tests/test_validate_content_manifest.py`, and this log on `feature/quran-video-pro` only. Tests have not been executed; no workflow dispatch, render, Telegram request/send, TikTok publication, or secret change was performed.


### Repair 51: handle invalid UTF-8 manifest files consistently
- Review found content rotation skipped malformed JSON but did not handle invalid UTF-8, and its batch re-read path could leak a raw decoder exception. The Pro orchestrator had the same gap when loading manifests/history.
- Rotation now treats invalid UTF-8 files as unreadable/ineligible; if a selected manifest becomes invalid UTF-8 during batch selection, it returns the controlled changed/unreadable error. The orchestrator also converts invalid UTF-8 into its normal controlled JSON-read failure.
- Added regressions for initial rotation scans, mid-selection corruption, and direct Pro orchestrator reads.
- Updated `src/content_rotation.py`, `tests/test_content_rotation.py`, `src/pro_orchestrator.py`, `tests/test_pro_orchestrator.py`, and this log on `feature/quran-video-pro` only. Tests have not been executed; no workflow dispatch, render, Telegram request/send, TikTok publication, or secret change was performed.


### Repair 52: align Pro renderer with the 40-second video limit
- Review found the renderer still declared both its target and hard duration limits as 65 seconds, while its regression test was named as a 40-second policy test but asserted 65 seconds. This allowed longer candidate videos contrary to the intended Pro limit.
- Changed both target and hard maximum duration to 40 seconds. Updated the regression to accept exactly 40 seconds and reject 40.01 seconds with the hard-limit error.
- The orchestrator imports the renderer's hard limit, so its preflight inherits the same 40-second ceiling.
- Updated `src/render_dua_video.py`, `tests/test_render_dua_video.py`, and this log on `feature/quran-video-pro` only. Tests have not been executed; no render, workflow dispatch, Telegram request/send, TikTok publication, or secret change was performed.


### Repair 53: raise the Pro dua/dhikr duration ceiling to 45 seconds
- User clarified that dua/dhikr may need a little more time, so the 40-second hard cap was too restrictive.
- Raised both the target and hard maximum to 45 seconds. The renderer accepts exactly 45 seconds and rejects durations above 45 seconds; the orchestrator inherits the same shared hard limit.
- Updated `src/render_dua_video.py`, `tests/test_render_dua_video.py`, and this log on `feature/quran-video-pro` only. Tests have not been executed; no render, workflow dispatch, Telegram request/send, TikTok publication, or secret change was performed.


### Repair 54: validate dua/dhikr source URL hosts and source names
- Review found a malformed value such as `https://` or a non-string source name could pass the prior truthiness/prefix check for a dua/dhikr religious source.
- Added a fail-closed HTTPS URL check requiring a real hostname and rejecting embedded URL credentials; source names must be non-empty strings. Added regressions for empty/malformed hosts, non-HTTPS URLs, non-string URLs, malformed IPv6, and invalid source names.
- Updated `src/validate_content_manifest.py`, `tests/test_validate_content_manifest.py`, and this log on `feature/quran-video-pro` only. Tests have not been executed; no render, workflow dispatch, Telegram request/send, TikTok publication, or secret change was performed.


### Repair 55: align Pro content guidance with the approved 45-second ceiling
- A final documentation sweep found the Pro content README still instructed reviewers to keep videos at 40 seconds, contradicting the approved renderer/orchestrator hard ceiling of 45 seconds.
- Updated the content intake guidance to 45 seconds. This is documentation-only; no renderer behavior changed. No tests, render, workflow dispatch, Telegram request/send, TikTok publication, or secret change was performed.


### Repair 56: include asset-rotation regressions in the Pro safety workflow
- Workflow audit found `tests/test_asset_rotation.py` was not invoked by the manual Pro safety workflow, despite the asset selector having fail-closed approval and repeat-protection logic.
- Added the missing explicit unittest-discovery step on the exact Pro branch. The workflow remains manual-only with read-only repository permissions and no Telegram/TikTok actions. This change has not been executed; no workflow dispatch, render, Telegram request/send, TikTok publication, or secret change was performed.


### Repair 57: align human review template with the 45-second ceiling
- Follow-up documentation audit found `content/pro/REVIEW_TEMPLATE.md` still stated a 40-second ceiling, conflicting with the renderer's current 45-second hard limit and the README corrected in Repair 55.
- Updated the review checklist to 45 seconds. Documentation-only; no tests, render, workflow dispatch, Telegram request/send, TikTok publication, or secret change was performed.



### Repair 58: verify actual Pro preview inputs and isolate legacy background candidates
- Re-audited the exact Pro branch tree at HEAD `dc743033340b28b051846420c3a32eaa3b572d0e`, the candidate research record, media-rights policy/validator, preview delivery cycle, and manual safety workflow.
- Confirmed there are still no Pro dua/dhikr manifest files, no `assets/pro/media/` directory or media files, and no `content/pro/rights/` per-asset evidence records in the branch tree. The three research candidates (Al-Baqarah 2:201, the Abu Dawud/Tirmidhi morning-evening wording variants, and Sayyid al-Istighfar) remain research-only with human text/context review and media clearance pending.
- Confirmed the existing `data/background_candidates.json` contains four previously user-approved Quran-engine background candidates, but these are not Pro rights records or Pro-local media files. They cannot satisfy the Pro validator's exact-file SHA-256, per-asset license evidence, explicit private-review permission, territory/validity, attribution, and third-party-review requirements. They must not be silently promoted or reused as Pro-cleared assets.
- Confirmed the Pro preview cycle has strong preflight gates (candidate-only manifest, private Telegram destination verification, per-asset rights validation, hash-bound ledger reservation, and explicit send confirmation), but there is no real manifest/media/video input to exercise it.
- Confirmed the manual safety workflow includes 15 test suites and remains `workflow_dispatch`-only. No dispatch action is available through the connected GitHub tools in this session, so no current-HEAD test result is claimed. The prior 90/90 result recorded in `PRO_PROJECT_STATUS.md` predates subsequent changes and does not validate HEAD `dc743033`.
- No code, candidate approval, rights record, media asset, workflow, secret, Telegram configuration, or production branch was changed in this audit. No render, Telegram request/send, or TikTok publication occurred.
- Next real prerequisites: (1) human-review one exact dua/dhikr source and wording from its primary reference; (2) obtain and review a suitable spoken recording or explicitly choose a silent preview; (3) obtain one background file with exact per-asset rights evidence; (4) create one candidate-only manifest and run the full safety workflow on that exact HEAD; (5) only after a separately authorized run, render and verify a private preview. No production approval is implied.


### Repair 59: record meaning-matched backgrounds for each dua/dhikr item
- Added a binding Pro visual-selection rule: choose a background for the meaning and emotional context of each specific dua/dhikr item, not one generic background for all duas or merely by broad content category.
- Added illustrative topic mappings (forgiveness/istighfar, morning adhkar, evening adhkar, provision/gratitude, and protection), with an explicit instruction not to force a mapping that misrepresents the exact wording.
- Required avoidance of consecutive repeats, practical rotation among eligible assets, calm composition and text contrast, and fail-closed behavior when no semantically suitable, individually rights-cleared asset exists.
- Clarified that thematic suitability does not confer media rights: each exact Pro background still needs its own file/hash/source/license evidence and required approvals. No existing Quran background candidate was promoted or reused.
- Updated `content/pro/README.md` and this log on `feature/quran-video-pro` only. This is a documentation/policy change; no assets, manifests, code, workflows, rights approvals, Telegram settings, or production branch were changed.
- No tests, render, workflow dispatch, Telegram request/send, or TikTok publication were performed. The known blockers from Repair 58 remain.


### Repair 60: enforce reviewed meaning-matched backgrounds in dua/dhikr manifests
- Code review found the renderer consumes one manifest-level background for each video, but the content validator did not require any metadata proving that this background was selected for the meaning of the exact dua/dhikr item. The new policy was therefore documented but not yet enforced at manifest intake.
- Updated `src/validate_content_manifest.py` so every dua/dhikr manifest must include a non-empty `visual.background_theme`, a non-empty `visual.background_meaning_rationale` tied to the exact item's meaning, and literal `visual.background_meaning_reviewed: true`. Quran manifest validation is unchanged.
- Updated the dua test fixture and added regressions for missing theme, missing rationale, missing human review, and a valid topic-specific reviewed background.
- Updated `src/validate_content_manifest.py`, `tests/test_validate_content_manifest.py`, and this log on `feature/quran-video-pro` only.
- Tests have not been executed because no local checkout or current-HEAD workflow dispatch is available in this session. The changes are source-committed but unvalidated. No render, Telegram request/send, TikTok publication, media approval, or production-branch change occurred.


## 2026-11-07 — Repair 61: prevent same background video within a Pro batch

- Source review found that Repair 60 enforced an item-specific, human-reviewed background theme and rationale, but the Pro batch orchestrator still accepted two different dua/dhikr manifests that pointed to the exact same background video.
- Updated `src/pro_orchestrator.py` to track exact `visual.background_candidate.direct_video_url` values during one production batch and fail closed if a later video reuses one.
- Added regression tests in `tests/test_pro_orchestrator.py` proving duplicate background URLs are rejected and distinct URLs remain accepted.
- Scope is deliberately limited to the same batch. Cross-day background history/rotation is not claimed as implemented; the current history contract stores content IDs and there is no verified background-history persistence path yet.
- Tests were authored but not executed: no local checkout is available in this session and no GitHub Actions workflow-dispatch action is exposed. No preview render, Telegram delivery, TikTok publication, media approval, secret change, or production-branch change was performed.


## 2026-11-07 — Repair 62: align Pro orchestrator fixtures with semantic-background validation

- Follow-up review after Repairs 60–61 found the shared `tests/test_pro_orchestrator.py` manifest factory had not been updated for the newly mandatory dua/dhikr fields `visual.background_theme`, `visual.background_meaning_rationale`, and `visual.background_meaning_reviewed: true`.
- This would cause existing orchestrator tests (including the new duplicate-background regression tests) to fail at manifest validation before exercising their intended assertions.
- Updated the shared test fixture with explicit meaning-matched background metadata so tests reach the orchestrator behavior they are intended to cover. This is test-fixture alignment only; it does not approve any real media asset or manifest.
- Tests remain authored but unexecuted because this session has no local checkout and no GitHub Actions dispatch capability. No render, Telegram delivery, TikTok publication, media approval, secrets, or production branch were changed.


## 2026-11-07 — Repair 63: validate background URLs before orchestration

- Code review found the shared manifest validator only checked that background `source_url` and `direct_video_url` were truthy. The Pro orchestrator subsequently calls `.strip()` on `direct_video_url`, so malformed non-string values could escape the intended controlled fail-closed validation path; non-HTTPS or hostless links were also not rejected at this boundary.
- Updated `src/validate_content_manifest.py` to require both background URLs to be valid HTTPS URLs with a host, using the existing strict URL helper.
- Added regression coverage for empty, HTTP, hostless HTTPS, numeric, and null values for both URL fields in `tests/test_validate_content_manifest.py`.
- This is metadata validation only; it does not establish ownership, licensing, rights, or media approval. Those remain separate required gates.
- Tests were authored but not executed. No render, Telegram delivery, TikTok publication, secret change, media approval, or production-branch change was performed.


## 2026-11-07 — Repair 64: prevent duplicate background themes within a Pro batch

- Extended the batch-level background uniqueness guard beyond exact media URL reuse: two videos in the same Pro batch may not declare the same meaning-matched `visual.background_theme` (case-insensitive after trimming), even if their direct video URLs differ.
- Added a regression test that uses different background video URLs but repeats the same theme and confirms the batch is rejected. Existing distinct-background test continues to cover different URLs with different themes through the fixture defaults only if the theme is changed; the current fixture theme is shared, so this test also documents that distinct theme metadata is required for a multi-video batch.
- This is intentionally fail-closed: if two supplications genuinely require the same topic, a future reviewed manifest should still provide individually differentiated visual themes/scenes rather than silently recycling one theme in the same batch.
- Tests were authored but not executed. No media rights were granted, no render or Telegram send occurred, no TikTok publication occurred, and no production branch was modified.


## 2026-11-07 — Repair 65: align preview sender and delivery-cycle fixtures with background review gates

- Re-audit after Repair 60 found two independent test manifest factories had not been updated for the mandatory dua/dhikr background fields: `tests/test_send_pro_preview_telegram.py` and `tests/test_pro_preview_delivery_cycle.py` omitted `background_theme`, `background_meaning_rationale`, and `background_meaning_reviewed: true`.
- Those fixtures would be rejected by the shared validator before sender/delivery-cycle assertions could reach their intended code paths. Added explicit meaning-specific test metadata to both fixtures; this does not approve a real background or grant media rights.
- Tests remain unexecuted on current HEAD. No Telegram API call, render, real media approval, TikTok publication, secret change, or production-branch change occurred.


## 2026-11-07 — Repair 66: correct Pro preview delivery documentation

- Updated `content/pro/README.md` to distinguish implemented code from an enabled end-to-end workflow: isolated preview sender and two-phase delivery-cycle code exist, but no connected/enabled Pro preview workflow or real candidate render/send has been verified.
- Reworded the delivery restriction so it accurately requires the workflow, passing current-HEAD tests, a reviewed real candidate/media-rights package, and explicit authorization for the individual send.
- No workflow, manifest, media asset, rights record, secret, Telegram setting, render, or send was created or changed.


## 2026-11-07 — Repair 67: reject malformed preview Telegram configuration at preflight

- Hardened `src/pro_preview_delivery_cycle.py::preflight` to type-check bot token and chat ID before calling string methods. Previously non-string values could escape as an uncontrolled `AttributeError` instead of a deliberate fail-closed `ValueError`.
- Added a focused preflight regression test for null and numeric token/chat values, confirming rejection occurs before private-chat verification.
- This is a validation-only change; no secrets were read or changed and no Telegram network request, render, or publication occurred. Test authored but not executed on current HEAD.


## 2026-11-07 — Pro asset intake review: first meaning-matched background lead (not approved)

- Re-checked the exact Pro branch head before intake work: `05023dfea14d301d118cd3d1a20454978613b03d`. The last visible Pro Safety Tests run remains `42318772835` on older SHA `f8e0d76a151e7241901f21b9c257de1d0a7a97fb`; it is not evidence that current HEAD passed. No newer run was found in the branch run list.
- Re-read `content/pro/CANDIDATE_RESEARCH_001.md`: QD-001 (Qur'an 2:201) remains a research candidate; exact-text/context human review is pending. PD-001 has source wording variants that must not be merged; PD-002 (Sayyid al-Istighfar) still needs full context and duration review. No candidate was promoted to a manifest.
- Searched for a possible topic-appropriate, no-person sunrise/mountain background lead for QD-001. Found Pixabay asset page: https://pixabay.com/videos/ai-generated-sunrise-dawn-mountains-367404/ (page describes an AI-generated golden sunrise/mountain landscape, MP4 3840x2160, and states Pixabay Content License). This is a discovery lead only: the exact file has not been downloaded, inspected, hashed, or checked for embedded third-party elements; current license terms and per-asset permissions have not been independently captured; no Pro rights record exists. It is NOT approved for rendering or delivery.
- A second Pixabay mountain sunrise result (https://pixabay.com/videos/sunrise-nature-dawn-scenic-296969/) is also only a lead; its creator page includes a commercial-use caveat/request to message the creator, so it is not treated as cleared.
- Next actual gates: obtain and inspect one selected source file under `assets/pro/media/`, capture exact license evidence and asset metadata, create a SHA-256-bound rights record only after review, then prepare the candidate manifest and run current-HEAD tests. The GitHub connector still exposes no workflow-dispatch action, so manual current-HEAD test execution remains blocked from this session.
- No source file was downloaded or added, no rights approval was recorded, no manifest or renderer output was created, no Telegram API request/send occurred, no TikTok publication occurred, and no production branch or secret was changed.


## 2026-11-07 — Pro asset intake review: current Pixabay terms checked

- Opened the exact QD-001 sunrise/mountain lead page again. The page identifies the item as AI-generated, MP4, 3840×2160, 30 FPS, published 2026-07-29, and displays the Pixabay Content License. Creator profile describes the work as rights-free, but that statement is not independent proof of all underlying rights.
- Read the current Pixabay Content License Summary and Terms of Service (terms page states last updated 2026-10-20). The license grants broad commercial/non-commercial use and adaptation subject to prohibited uses; combining video with text/media/editing can qualify as a new creative work rather than standalone redistribution. However, Pixabay explicitly places responsibility for checking additional third-party rights on the user and disclaims warranties that consents/licenses have been obtained. The terms also prohibit misleading presentation and standalone distribution.
- Decision: keep asset 367404 as a research lead only. No exact MP4 file was downloaded or inspected, no third-party-rights assessment was completed, and no SHA-256-bound Pro rights record can yet be truthfully created. The AI-generated label is recorded as a relevant property, not as a clearance defect by itself.
- The next gate remains exact-file acquisition through the normal download route, visual/audio inspection (including any embedded elements), hash capture, and a documented per-asset decision. Do not set rights approval flags or render from this lead before those steps.
- No code, candidate manifest, media asset, rights record, workflow, secret, Telegram configuration, or production branch was changed. No tests, render, Telegram request/send, or TikTok publication occurred.


## 2026-11-07 — Pro background sourcing: Mixkit Free License candidates

- Expanded background sourcing beyond the first Pixabay lead to Mixkit, and checked both the exact asset pages and the official Mixkit Stock Video Free License modal.
- Candidate lead MK-001: https://mixkit.co/free-stock-video/beautiful-sunrise-landscape-1944/ — page describes a sunrise over mountain silhouettes with clear sky; offers a free download explicitly for commercial or personal use under the Mixkit Stock Video Free License; 55 seconds, 24 fps, 15.75 MB; listed download resolutions include 1080x720, 1920x1080, and 4096x2160. Semantically plausible for QD-001 (Qur'an 2:201) as a calm, hopeful landscape, subject to actual visual inspection and final content review.
- Candidate lead MK-002: https://mixkit.co/free-stock-video/forest-during-the-morning-3012/ — page describes morning sunlight through a forest; offers a free download explicitly for commercial or personal use under the Mixkit Stock Video Free License; 24 seconds, 60 fps, 6.76 MB; listed resolutions 1080x720 and 1920x1080. This is a separate visual direction suitable for later meaning-matched rotation where morning/renewal imagery fits.
- Official Mixkit Free License page says items may be used in commercial and non-commercial projects for free, with rights to download, copy, modify, distribute, publicly perform and broadcast; attribution is not required. The license modal also points to User Terms for important limits. This is materially clearer for the stated social-video use than the previously considered Pixabay AI sunrise lead, but it does not itself prove that a specific downloaded file contains no third-party elements or resolve any separate rights that may attach to depicted content.
- Decision: both remain candidate leads, NOT approved Pro assets. The exact download bytes have not been acquired or inspected in this session, no SHA-256 hash has been captured, no media metadata/third-party-element review has been completed, and no rights record or approval flags have been created. MK-001 is the first candidate to acquire and inspect when a repository-side download path is available; MK-002 is retained as a distinct backup theme, not a same-video substitute.
- No user file upload was requested. No code, manifest, media file, rights record, workflow, secret, Telegram configuration, or production branch was changed. No tests, render, Telegram request/send, or TikTok publication occurred.
- Next step: use an authorized automated download path in the Pro CI environment (not a manual user upload), pin the exact source page and license evidence, inspect the downloaded file and embedded content, compute SHA-256, then make a documented per-asset decision. Do not mark either asset approved before those steps.


## 2026-11-07 — Document Mixkit as an additional Pro discovery source

- Updated `content/pro/MEDIA_RIGHTS_POLICY.md` to add Mixkit as an additional background-video discovery source, while explicitly distinguishing the commercial-use Free License from Restricted License downloads.
- Recorded the official Free License scope (including social-media video posts and commercial projects), no mandatory attribution, and the fact that Mixkit User Terms and all existing per-asset/third-party review gates still apply.
- Named MK-001 and MK-002 as example research leads only; no approval status or rights booleans were set. Exact downloaded bytes, file hashes, creator/owner confirmation, and visual third-party inspection are still outstanding.
- No runtime code, manifest, media bytes, rights record, workflow, secret, Telegram configuration, or production branch was changed. No tests, render, Telegram request/send, or TikTok publication occurred.


## 2026-11-07 — Mixkit User Terms caveat review

- Read the official Mixkit User Terms (last revised 2025-10-02). They clarify that download grants a non-exclusive license, not ownership; prohibit scripts/bots for mass downloads or scraping the library; and warn that individual Item components (including trademarks/brands) may be third-party material not cleared for the user's use.
- Refined the Pro policy: no Mixkit scraping or bulk downloads; acquisition must use the ordinary permitted individual download flow; exact file inspection and third-party review remain mandatory. This avoids building an automated scraper under the mistaken assumption that a general Free License authorizes it.
- Updated policy and this log only. No media file, rights record, manifest, code, workflow, secret, Telegram configuration, render, send, or production branch changed.


## 2026-11-07 — Isolated single-asset intake workflow for MK-001

- Added `.github/workflows/pro-background-intake-mk001.yml`, restricted to the exact `feature/quran-video-pro` branch and read-only repository permissions. It is triggered by changes to that workflow file (and supports manual dispatch when available).
- The workflow targets exactly one explicitly named Mixkit asset page (MK-001); it checks that the page still displays the Mixkit Stock Video Free License and commercial/personal-use wording before resolving one HTTPS MP4. It has a size ceiling, captures file SHA-256 and ffprobe metadata, extracts a nine-frame contact sheet, and uploads a short-retention review artifact. It does not write media or approval records back into the repository, does not send Telegram messages, and does not publish.
- The workflow was committed and the push-triggered run was observed. Initial run `42410110757` started on commit `1e359cd703995905734736ccd2c177a5cd7ccb95`; a regex/newline escaping defect was corrected in the workflow on commit `39b0995ada59edf536ecc520ab1fae82f0da8f61`, which triggered corrected run `42410120180`. At log time, the first run was still installing dependencies and the corrected run was pending behind the concurrency group. Neither run had completed; no download, metadata, hash, contact sheet, or artifact is claimed as produced yet.
- This is one individually listed candidate intake, not library scraping or bulk download. It is designed to avoid the Mixkit User Terms prohibition on bots/scripts used for mass downloading. If the asset page no longer proves the Free License, the workflow fails closed.
- Both candidate status and rights approval remain false. Even after artifact creation, exact visual inspection and review of third-party elements, rights owner/creator details, and applicable terms are required. No Pro rights record, manifest, renderer input, or delivery approval was created.
- No current-HEAD safety test, video render, Telegram request/send, or TikTok publication occurred. No original Quran production branch was changed.


## 2026-11-07 — QD-001 source corroboration

- Cross-checked Al-Baqarah 2:201 against Quran.com and the Quranic Arabic Corpus. Both identify the exact verse reference and show the intended Sahih/Saheeh International English translation; the Corpus also exposes word-by-word morphology and parallel translations.
- Added a source corroboration addendum to `content/pro/CANDIDATE_RESEARCH_001.md`. Status deliberately remains `source_checked_candidate`: human letter-by-letter Arabic review, context review, and all media rights remain pending. No manifest or approval flags were created.
- Sources: https://quran.com/al-baqarah/201?translations=131 ; https://corpus.quran.com/translation.jsp?chapter=2&verse=201 ; https://legacy.quran.com/2/201 .
- No render, Telegram request/send, or TikTok publication occurred.


## 2026-11-07 — MK-001 intake run results and contact-sheet repair

- First push run `42410110757` failed at direct-MP4 discovery because the regex was over-escaped. The workflow was corrected; this first failure did not download or retain media.
- Corrected run `42410120180` successfully resolved the individual asset page's Free License text and downloaded MK-001 inside the ephemeral GitHub runner. Logged facts: 16,515,983 bytes; MIME `video/mp4`; download host `assets.mixkit.co`; SHA-256 `9bbf623aa42493925e612659cf90a6e5a15762e22f0ba1f92c179265173fe27d`; ffprobe: H.264, 1280×720, 24000/1001 fps, duration 54.804750 seconds.
- That run failed during contact-sheet generation on the final frame (seeking too close to EOF and JPEG encoder range handling). Because artifact upload is after that step, no review artifact was created and the ephemeral runner workspace was not retained. The hash and metadata are evidence in the workflow logs only; do not treat this as a repository-local asset.
- Repaired the workflow on commit `787821cb77000eaafa1080bde39d9e476dc74ade`: frame extracts now use PNG and sample timestamps are clamped to at least one second before EOF. Push run `42410211663` was observed starting; at the time of this entry it had not completed. No success is claimed for this repair yet.
- Asset remains `candidate_only_not_approved`; no rights JSON, manifest, Pro media file, or approval flag exists. Visual inspection has not occurred. No render, Telegram request/send, or TikTok publication occurred.


## 2026-11-07 — MK-001 visual sample review completed

- Push-triggered intake run `42410280656` completed successfully on commit `a381ae31b10dcb233cb9831d7ac79ac2fd44f982`: exact page license check passed; one file downloaded; ffprobe and nine-frame contact sheet succeeded; contact sheet payload was emitted in job logs for visual inspection.
- Exact file metadata from the successful run: 16,515,983 bytes, MP4/H.264, 1280×720, 24000/1001 fps, 54.804750 seconds, SHA-256 `9bbf623aa42493925e612659cf90a6e5a15762e22f0ba1f92c179265173fe27d`.
- Visually inspected all nine sampled frames: calm sunrise, mountain silhouettes and open landscape; no people/logos/obvious artwork visible in those sampled frames. Central crop area retains the sun/mountain line; source is horizontal 16:9 and has a relatively dark foreground. Full-frame inspection is still required. Added a durable contact sheet at `content/pro/review_previews/MK-001-contact-sheet.jpg` (commit `f9eeeda123f758877756caa05dbaee6771083a77`).
- GitHub artifact upload was attempted in the prior run but failed because repository Actions artifact storage quota was exhausted. The workflow was changed to emit the small contact sheet into job logs instead; the successful run proves the new route works. No media file was persisted in the repo; the MP4 existed only in the ephemeral runner. Its hash and metadata are preserved in this log and candidate research note.
- Updated `content/pro/CANDIDATE_RESEARCH_001.md` with the sample review. Candidate remains unapproved: no full-file review, creator/rights-owner evidence, per-asset rights JSON, or user rights approval. No manifest or renderer input created.
- No current-HEAD safety test, video render, Telegram request/send, or TikTok publication occurred.


## 2026-11-07 — Final MK-001 intake workflow verification

- A subsequent push-triggered run `42410311973` completed with conclusion `success` on workflow commit `ebe3d7453b8f6501c1d79e51f77af893eb9618f6`, after the conditional ffmpeg-install optimization. It independently downloaded the same exact single candidate, probed the video, generated the contact sheet, and emitted it into job logs without relying on GitHub artifact storage.
- The run independently reproduced the exact byte count (16,515,983) and SHA-256 (`9bbf623aa42493925e612659cf90a6e5a15762e22f0ba1f92c179265173fe27d`). The workflow is therefore reproducible for this one allowlisted item. The successful run did not persist the MP4 to the repository; only the reviewed contact sheet is stored at `content/pro/review_previews/MK-001-contact-sheet.jpg`.
- Workflow currently remains review-only and single-item; no production manifest, media rights record, approval flag, render, Telegram send, or TikTok publication is enabled.


## 2026-11-07 — MK-002 distinct morning-forest background candidate

- Checked the exact Mixkit page for `forest-during-the-morning-3012`. It explicitly displays the Stock Video Free License and commercial/personal-use wording; page metadata lists 24 seconds, 60 fps, 6.76 MB, with 1080×720 and 1920×1080 options.
- Proposed this as a separate calm morning/renewal visual direction for a future Sayyid al-Istighfar item, distinct from MK-001's sunrise/mountain open landscape. No visual mapping is approved until the exact file is inspected.
- Added an isolated, exact-Pro-branch single-item intake workflow `.github/workflows/pro-background-intake-mk002.yml` and recorded the source in `content/pro/CANDIDATE_RESEARCH_001.md`. The first run `42410443005` started on the initial workflow commit; a filename correction was committed as `a60254931e40f907a04265457c7f835296c5ded0` and a corrected run was observed pending. No completion is claimed yet.
- No file/hash/contact sheet, rights record, manifest, approval, render, Telegram send, or TikTok publication is claimed for MK-002.


## 2026-11-07 — MK-002 morning forest intake and visual sample review

- Single-item intake run `42410443005` completed successfully: page Free License check passed; exact MP4 downloaded; ffprobe and nine-frame contact sheet succeeded; contact sheet was inspected.
- Exact file facts: 7,083,251 bytes, MP4/H.264, 1280×720, 60 fps, 23.550000 seconds, SHA-256 `6a39a371443cbed05f27a6a213e8905318186ac5086424d8e6a37f1d6ad1d462`.
- Sampled frames show a sunlit forest with morning rays between trees; no people/logos/obvious artwork visible in the nine sampled frames. It is visually distinct from MK-001 and a possible quiet renewal/istighfar theme. The central 9:16 crop is visually busy; text legibility will need a calm/darkened overlay. Full-file inspection remains outstanding.
- Saved durable contact sheet `content/pro/review_previews/MK-002-contact-sheet.jpg` in commit `2d03cc5103799a62f55c233545ea8c60dd0629bc`. The MP4 itself is not retained in the repository; it existed only in the ephemeral runner. No rights JSON, manifest, approval flag, render, Telegram send, or TikTok publication was created.
- Updated `content/pro/CANDIDATE_RESEARCH_001.md` with the exact metadata, visual sample findings, and remaining rights blockers. A second corrected filename run was observed pending at the time; no claim is made about its result.


## 2026-11-07 — MK-002 corrected intake workflow verified

- Corrected run `42410451486` completed successfully on workflow commit `a60254931e40f907a04265457c7f835296c5ded0`, confirming the same single forest item can be fetched and inspected using the corrected `MK-002-forest-during-the-morning.mp4` working filename. It reproduced the expected metadata/hash and contact-sheet output.
- Both the initial and corrected MK-002 intake runs succeeded; the earlier candidate note's pending status is superseded. No rights approval or persistent MP4 was created.


## 2026-11-07 — Pro push CI enabled; 192 offline safety tests pass

- Added `.github/workflows/pro-safety-tests-on-push.yml`, restricted to `feature/quran-video-pro`, read-only repository permissions, and offline suites only. It runs on changes to Pro source/tests/content and the workflow itself. The existing manual-only workflow was left intact.
- The first push-triggered CI runs exposed several pre-existing test/API mismatches. Repairs made on this branch:
  - `src/pro_preview_send_ledger.py`: precise symlink rejection messages for ledger file and lock file while retaining parent-component checks.
  - `src/pro_delivery_ledger.py`: check a symlinked lock file before generic ancestor scanning, preserving the lock-specific rejection.
  - `src/send_pro_telegram.py`: typed, fixed-message Telegram response validation errors are preserved after marking the ledger uncertain; arbitrary transport/decoder errors remain redacted.
  - `src/validate_pro_media_rights.py`: read the private-review delivery territory from the manifest when not passed separately, and validate territory scope before individual use flags so fail-closed errors identify the correct blocker.
  - `src/content_rotation.py`: reject mappings as invalid recent-ID inputs rather than silently iterating their keys.
  - `src/render_dua_video.py`: clarify the 45-second hard-cap error text.
  - Test fixtures/imports aligned with the current contracts in `test_pro_preview_delivery_cycle.py`, `test_persist_pro_preview_ledger.py`, and `test_validate_content_manifest.py`.
- Final CI run `42411028231` completed successfully on exact Pro branch commit `c5baa3937fa2f4e6255bf18b158a07f84ff28d7b`. All 14 offline test suites passed: 192 tests total, no failures or errors.
- This verifies the code/test state at that exact SHA. Subsequent log-only commits do not change runtime code. No renderer execution, actual candidate video render, Telegram request/send, or TikTok publication occurred. Both stock MP4 candidates remain research/visual-sample candidates only; the MP4 bytes are not stored in the repository and no rights records are approved.


## 2026-11-07 — Withdraw automated Mixkit intake prototype after terms review

- A temporary one-asset GitHub Actions intake prototype for MK-001 was added and its parser was corrected, but it was not observed executing and produced no artifact, download, metadata hash, or visual inspection.
- Re-evaluating Mixkit User Terms against the proposed page-parsing/direct-MP4 automation showed that this approach risks conflicting with the provider's restrictions on scripts/bots and scraping/bulk downloading. To avoid placing the project or account at risk, the prototype workflow `.github/workflows/pro-background-intake-mk001.yml` was removed before any asset download was performed.
- The Mixkit policy and two candidate leads remain documented as research-only; neither is approved. The next acquisition route must be explicitly allowed by the source provider (for example, a documented API or an expressly permitted individual download path), not a page scraper.
- The latest observed Pro push safety run during this work was run `42411028231`, success on commit `c5baa3937fa2f4e6255bf18b158a07f84ff28d7b`. This is an earlier SHA than the current branch head and is not evidence that the later intake-workflow changes were tested. No current-HEAD test or render is claimed.
- No Telegram delivery, TikTok publication, production manifest approval, or rights record was created.


## 2026-11-07 — Wikimedia Commons API and CC0 video candidate research

- Identified Wikimedia Commons as a potentially suitable alternative media source because it provides a documented MediaWiki Action API for retrieving exact file URLs and metadata (including license and author fields through `imageinfo` / `extmetadata`). Official docs: https://www.mediawiki.org/wiki/API:Imageinfo and https://commons.wikimedia.org/wiki/Commons:Machine-readable_data.
- Commons notes that license/author metadata is not universally structured and some fields remain free text; therefore an API result must not be treated as conclusive without opening and reviewing the exact file description page. The file page itself remains the controlling evidence for candidate-level license review.
- Research lead WC-001: https://commons.wikimedia.org/wiki/File:Sunrise_Glow_Over_Surf_Beach_with_Pink_Horizon_and_Vibrant_Sand_Tones.webm. Search result reports a 26.066-second, 1080x1920 vertical video and CC0 dedication by the copyright holder, categorized as a beach sunrise. This is a promising vertical candidate format, but exact page, author/source, original video content, and actual bytes have not yet been inspected; not approved.
- Research lead WC-002: https://commons.wikimedia.org/wiki/File:Spring_Morning_looking_up_from_the_base_of_Dilworth_Mountain.webm. Search result reports 42 seconds, 1280x720, and CC0 dedication by the copyright holder; page description notes birdsong and traffic, so it may not be suitable for a clean silent background without audio removal and inspection. Not approved.
- Other inspected sunrise videos on Commons were CC BY-SA 4.0 or CC BY 2.0, which introduce attribution/share-alike obligations and were not selected as first candidates. The exact file `Sunrise from mountains.webm` is only 478x850 and CC BY-SA 4.0; `Beauty of Sunrise.webm` is 1920x1080, 8 seconds, CC BY-SA 4.0, and its page identifies a Pexels source, so neither is preferred for the initial Pro test.
- No media was downloaded, no visual inspection of the actual video bytes occurred, and no hash or rights record was created. This is source research only.


## 2026-11-07 — Exact review of Wikimedia CC0 vertical sunrise candidate

- Opened the exact Commons file page for WC-001: https://commons.wikimedia.org/wiki/File:Sunrise_Glow_Over_Surf_Beach_with_Pink_Horizon_and_Vibrant_Sand_Tones.webm.
- The page identifies JaredMcKenzie as author, source as own work, date 29 March 2026, and explicitly states CC0 1.0 Universal Public Domain Dedication. It reports 26 seconds, 1080x1920 vertical, WebM VP9/Opus, 6.77 MB. This is a stronger candidate than the earlier Mixkit leads for Pro vertical output and commercial use.
- The Commons page provides a direct original-file URL and structured metadata including duration, dimensions, file size, and a SHA-1 checksum. That SHA-1 is source metadata only; it is not a substitute for computing SHA-256 from the exact acquired bytes.
- The exact media bytes could not be acquired in this session through the available runtime, so no actual playback/visual/audio inspection, file hash, or third-party review was completed. WC-001 remains a promising research lead only, not an approved asset.
- Updated `content/pro/MEDIA_RIGHTS_POLICY.md` to permit Commons discovery through its documented MediaWiki API rather than HTML scraping, while preserving exact-page review, attribution/share-alike checks, actual-byte SHA-256, and third-party clearance gates.
- No media file, rights record, manifest, runtime code, workflow, secret, Telegram configuration, render, or delivery was created or changed.


## 2026-11-07 — WC-001 single-file Commons intake workflow added

- Added `.github/workflows/pro-background-intake-wc001.yml` on `feature/quran-video-pro` in commit `b7862b83567a1663a072f8da7219d0224dfd5f8e`.
- The workflow is restricted to a push changing this exact workflow file on the Pro branch; it checks out only `feature/quran-video-pro`, uses read-only repository permissions, and has no Telegram or publishing secrets/steps.
- Acquisition uses one documented, read-only Wikimedia Commons Action API `imageinfo` request with a descriptive User-Agent, `maxlag=5`, sequential requests, bounded retry/backoff honoring `Retry-After`, and one exact original-file download from `upload.wikimedia.org`. It does not scrape HTML or search/download multiple assets.
- Fail-closed checks pin the exact file title, CC0 1.0 license metadata, author/source metadata, MIME, expected byte count, and Commons SHA-1 from the reviewed page. It computes SHA-256 from the downloaded bytes, then runs ffprobe and creates a nine-frame contact sheet only if the duration/dimensions match the reviewed 26-second 1080x1920 candidate.
- Output is a short-retention GitHub Actions review artifact (3 days), not a repository media commit. The workflow explicitly marks the item `candidate_only_not_approved`; it cannot create a rights record, manifest, approval, render, Telegram send, or TikTok publication.
- The workflow file was fetched back and its blob SHA verified as `19f14f06b9ecb5002860ac68274486776cdd0940`. The connector's commit-run lookup returned no workflow-run rows for this commit, so no successful intake, actual download, hash, probe, or contact sheet is claimed yet. A separate current-HEAD safety-test result is also not established by this commit.
- External policy basis: Wikimedia API etiquette/access guidance requires an informative User-Agent, considerate sequential request behavior, `maxlag` for non-interactive work, and compliance with rate-limit responses. This workflow is intentionally one low-volume, one-file review, not a crawler or ongoing bulk downloader.
- No rights approval, production manifest, renderer change, Telegram configuration, or user-facing delivery was made.


## 2026-11-07 — Harden WC-001 Commons metadata gates

- Updated the one-file intake workflow in commit `455e239bd2e02d90e600d887316bcf2ef5ea60d6` after checking the exact Commons page and official CommonsMetadata documentation.
- License URL validation now checks the canonical Creative Commons hostname and exact CC0 1.0 path independent of HTTP/HTTPS scheme, while still requiring the CC0 short name. It also requires the API's `Copyrighted` metadata to explicitly indicate false and fails closed if the API reports any reuse restrictions.
- Records the returned copyright/restrictions metadata in the candidate-only intake metadata. This is a technical preflight only; it does not replace exact-page or full-file human review and does not approve the asset.
- Verified exact page facts: 26.066 seconds, 1080x1920, 7,097,794 bytes, video/webm, Commons SHA-1 `f731168d29e287072ba2a5dded194b072fe79d2e`, uploader/author JaredMcKenzie, source Own work, and CC0 1.0 dedication. The page explicitly allows commercial reuse under CC0; see https://commons.wikimedia.org/wiki/File:Sunrise_Glow_Over_Surf_Beach_with_Pink_Horizon_and_Vibrant_Sand_Tones.webm.
- Official CommonsMetadata documentation explains that extmetadata includes LicenseShortName, LicenseUrl, Copyrighted, Restrictions, and Artist, while warning that some metadata may be unreliable (notably multi-licensed files) and that Artist can contain complex HTML. This is why the workflow pins one exact file and retains manual review gates.
- The updated workflow and this log entry were fetched back and verified. No successful intake run, downloaded file, SHA-256, playback inspection, rights approval, render, Telegram send, or TikTok publication is claimed.


## 2026-11-07 — Link intake workflow changes to Pro offline safety CI

- Updated `.github/workflows/pro-safety-tests-on-push.yml` in commit `ee5a4471948f23f21fb51c28ddbe1af3c6b7c98c` so changes to the exact WC-001 intake workflow also trigger the existing Pro-only offline safety suite.
- This keeps the Pro test suite running on the latest branch state whenever this candidate-intake workflow is changed. It does not claim to test GitHub Actions workflow semantics or execute the intake itself; it runs the existing Python offline safety suites.
- The push should trigger the suite because the changed path is now included. The run/result has not yet been observed through the available GitHub status interface; do not claim tests passed until a matching run and SHA are confirmed.
- No Telegram, publishing, secrets, media approval, manifest, or render behavior was enabled.


## 2026-11-07 — Correct Commons false-restrictions handling and trigger intake

- Updated `.github/workflows/pro-background-intake-wc001.yml` in commit `0b53d3711ad48043ad5d5e87b81d708983d69da0`.
- Exact Commons page metadata visibly reports CC0 and the two boolean-style values `false false` for copyright/restrictions. The intake gate now accepts an explicit false-like value (`false`, `no`, `0`) for Restrictions rather than incorrectly treating the literal string `false` as a restriction; unexpected non-false values still fail closed.
- Added a dated review comment to the workflow so the path-filtered one-file intake workflow is triggered by this push. The existing Pro offline safety workflow also includes this exact path in its push filter.
- Queried the connector for workflow runs immediately after the push; it returned no run rows. Therefore the workflow has not been verified as started or completed. Do not claim a successful download, hash, ffprobe, contact sheet, test pass, or media approval.
- Exact page evidence is available at https://commons.wikimedia.org/wiki/File:Sunrise_Glow_Over_Surf_Beach_with_Pink_Horizon_and_Vibrant_Sand_Tones.webm and shows CC0 1.0, author JaredMcKenzie, own work, video/webm, 26.066 seconds, 1080x1920, 7,097,794 bytes.
- No rights record, manifest, production render, Telegram send, or TikTok publication was created.


## 2026-11-07 — Diagnose first WC-001 intake run and correct CC0 deed URL gate

- Inspected GitHub Actions run `42416596552` on commit `0b53d3711ad48043ad5d5e87b81d708983d69da0`. Branch isolation, checkout, and tool installation passed. The metadata/download step failed before any binary download; ffprobe/contact sheet and artifact upload were skipped.
- Exact failure from the job log: `Commons API metadata does not confirm the expected CC0 1.0 license.`
- Rechecked the exact Commons file page. It displays the CC0 deed URL as `http://creativecommons.org/publicdomain/zero/1.0/deed.en`, not only the base `/publicdomain/zero/1.0` path. The previous URL-path gate was too strict.
- Corrected the gate in `.github/workflows/pro-background-intake-wc001.yml` in commit `ec1e03af716947b9ae576ee6bf55715912f5fa01` to accept either the canonical base path or the official `/deed.en` variant, while still requiring HTTPS-independent hostname validation and the exact CC0 path.
- This push should trigger the exact single-file intake workflow again. At the time of this log update, no run for commit `ec1e03af716947b9ae576ee6bf55715912f5fa01` was yet visible in the Actions run list.
- No video bytes were downloaded in the failed run; no SHA-256, ffprobe, contact sheet, artifact, rights record, approval, render, or Telegram send exists yet.


## 2026-11-07 — Diagnose WC-001 Copyrighted metadata omission

- Inspected completed GitHub Actions run `42416954567` on commit `ec1e03af716947b9ae576ee6bf55715912f5fa01`. Pro branch isolation, exact-branch checkout, and inspection-tool installation passed.
- The metadata/download step stopped before downloading any media. Exact log error: `Commons API does not explicitly mark the work as non-copyrighted/CC0.` The API response provided an empty/missing `Copyrighted` extmetadata value, rather than a positive copyright flag. ffprobe, contact-sheet generation, and artifact upload were skipped; the run produced no artifacts.
- Updated `.github/workflows/pro-background-intake-wc001.yml` in commit `7af4eedf1f3dc754c4396c4246ed90a033c25fd7`: a present `Copyrighted` value must still be explicitly false-like; a positive or unexpected non-empty value fails closed. An absent value is no longer treated as affirmative evidence of copyright, because the exact CC0 license metadata, canonical license URL, and empty restrictions gate remain mandatory. This is a metadata compatibility correction, not legal approval.
- The workflow remains pinned to the exact WC-001 file, creator/source, MIME, byte count, and Commons SHA-1. No broad download or scraper was introduced.
- This push should trigger the one-file intake again. Await the new run and inspect its actual logs/artifact before claiming download, SHA-256, ffprobe, contact sheet, or visual review.
- No rights record, manifest, media approval, production render, Telegram send, or TikTok publication was created.


## 2026-11-07 — Confirm latest WC-001 intake failure and add metadata diagnostics

- Retrieved the actual GitHub Actions run list for commit `7af4eedf1f3dc754c4396c4246ed90a033c25fd7`. The Pro-only offline safety run `42417082147` completed successfully; the WC-001 intake run `42417082133` completed with failure.
- Inspected intake job `128537405126`: Pro branch isolation, checkout of the exact commit, and inspection-tool installation passed. The metadata/download step failed with `Commons API reports a positive/unknown copyright flag; refusing intake.`; ffprobe, contact sheet, and artifact upload were skipped. No video was downloaded.
- This differs from the previous run where the API's `Copyrighted` field was absent: this run returned a non-empty value that the strict gate did not accept. The job log did not print the raw value, so its exact content is not yet established.
- Added a diagnostic print of the exact public Commons license name/URL and raw `Copyrighted`/`Restrictions` metadata immediately before the existing fail-closed gates, in commit `1c296be5b2cd10a77342dfa45398bb2640409b5b`. No acceptance condition was weakened and no media download can occur until the existing gates pass.
- The diagnostic commit should trigger another one-file intake run and the Pro offline safety suite. Await and inspect the actual run logs before deciding whether any metadata interpretation change is justified.
- No SHA-256, ffprobe result, contact sheet, artifact, rights record, approval, render, Telegram send, or TikTok publication is claimed.


## 2026-11-07 — Correct interpretation of Commons CC0 Copyrighted=True

- Inspected the completed intake run `42417436839` (job `128538462209`) on commit `1c296be5b2cd10a77342dfa45398bb2640409b5b`. Exact diagnostic output: `LicenseShortName=CC0`, `LicenseUrl=http://creativecommons.org/publicdomain/zero/1.0/deed.en`, `Copyrighted=True`, `Restrictions=` (empty). The workflow stopped before download because it incorrectly treated every `Copyrighted=True` as a reuse prohibition.
- Checked official CommonsMetadata documentation: `Copyrighted` is a boolean-like public-domain metadata field, but the documentation cautions that these fields can be unreliable for multi-licensed files. `Restrictions` is a separate field for reuse restrictions such as trademarks or personality rights. Source: https://www.mediawiki.org/wiki/Extension:CommonsMetadata.
- Checked Commons structured-data modeling: an own-work file can be recorded as “copyrighted, dedicated to the public domain by copyright holder” while also carrying the CC0 license. Source: https://commons.wikimedia.org/wiki/Commons:Structured_data/Modeling/Copyright (see the CC0 section). This resolves the apparent contradiction: `Copyrighted=True` does not itself negate the rights holder's CC0 dedication.
- Corrected the intake gate in commit `b0b4566d1739b982597da7ad3c54134b4fecd314`: retain the raw copyright flag for audit; accept recognized boolean values (true/false, yes/no, 1/0) when the separate exact CC0 name and canonical URL gates pass; continue to reject unknown non-boolean values. The separate Restrictions gate remains strict and rejects any non-empty value other than recognized false-like values. No general license relaxation or broad asset intake was introduced.
- The Pro-only offline safety suite passed on the preceding diagnostic commit `1c296be5b2cd10a77342dfa45398bb2640409b5b` (run `42417436787`). The new correction push should trigger both the safety suite and the exact one-file WC-001 intake; their results are pending.
- No video download, SHA-256, ffprobe, contact sheet, artifact, rights approval, render, Telegram send, or TikTok publication is claimed from the failed diagnostic run.


## 2026-11-07 — Diagnose exact Commons creator/source metadata mismatch

- Inspected the latest corrected intake run `42417577228` (job `128538881234`) on branch `feature/quran-video-pro`, commit `db4b0c51b724f838d3193d25af75d1b308b95cef`.
- Branch isolation, exact-branch checkout, and inspection-tool installation passed. The metadata/download step stopped at the creator/source check. The log confirms `LicenseShortName=CC0`, the canonical CC0 deed URL, `Copyrighted=True`, and empty `Restrictions`; the creator/source mismatch prevented any file download. ffprobe, contact sheet, and artifact upload were skipped.
- Updated the diagnostic output to include the exact raw `Artist` and `Source` API metadata values. The acceptance checks are unchanged; this is evidence collection only. The next push-triggered run must reveal the precise mismatch before any gate is changed.
- The Pro offline safety run `42417577272` completed successfully on the correction commit. This does not validate or approve the media candidate.
- No video download, SHA-256, ffprobe, contact sheet, artifact, rights record, media approval, render, Telegram send, or TikTok publication is claimed.

## 2026-11-07 — Resolve WC-001 Commons API source-field mismatch

- Inspected completed intake run 42417666249, job 128539149646, on commit e1f40c0ccd10a6c7e5e3763fbdd6480f2a87d187.
- Exact raw metadata: Artist is an HTML anchor linking to User:JaredMcKenzie; Source is an empty string. The earlier check incorrectly required the phrase “own work” in the API Source field, although the exact Commons file page had separately been reviewed and identifies it as own work.
- Updated the workflow to HTML-decode/strip the Artist markup and verify the linked creator name. The empty Source field remains recorded as empty; no API Source value is fabricated or inferred. All CC0 URL, restrictions, MIME, byte count, SHA-1, host, download, ffprobe, and artifact checks remain unchanged.
- Latest Pro offline safety run 42417666251 passed on commit e1f40c0ccd10a6c7e5e3763fbdd6480f2a87d187. The intake attempt did not download the video; ffprobe/contact-sheet/artifact steps were skipped.
- No asset approval, rights record, render, Telegram send, or TikTok publication is claimed.

## 2026-11-07 — WC-001 downloaded and probed; artifact quota blocks upload

- Intake run 42417807175 completed on commit d2955c564893c2c120d7a499efb51eb32e0f8973. Exact Commons metadata gates passed and the original file was downloaded: 7,097,794 bytes; SHA-1 f731168d29e287072ba2a5dded194b072fe79d2e; SHA-256 0e789ea0eaddb5b1e8a7999968143de7beb64f07ece25a918997073fe91072a6.
- ffprobe passed: 26.066 seconds, 1080x1920, VP9 video at 30 fps, Opus audio. Nine frames were extracted and a contact sheet was created.
- Artifact upload failed because GitHub Actions artifact storage quota was reached; logs explicitly say usage is recalculated every 6–12 hours. This is an infrastructure quota issue, not a media validation failure.
- Updated the workflow to emit a compact review contact sheet as base64 in the job log, so the preview can be retrieved without relying on artifact storage. Artifact upload is now non-blocking; the original video remains a candidate only and is not approved.
- No rights record, production render, Telegram send, or TikTok publication is claimed. Full visual review remains pending.

## 2026-11-07 — WC-001 visual contact sheet inspected; intake and safety runs pass

- Follow-up intake run 42417916186 completed successfully on commit b3eb8dd02acebaa3e0ce713142c4f831596806e6. The revised workflow emitted a compact contact sheet into its job log and the artifact-upload step no longer blocks the job.
- Retrieved and visually inspected the 9-frame contact sheet directly from the job log. The clip shows a calm beach shoreline at sunrise/sunset with pastel pink-blue sky, surf, wet sand and distant dark headland; scene is consistent across the sampled frames. It is a scenic beach, not a Quranic/architectural setting. Treat it as one possible calm background, not as a universal background for every dua.
- WC-001 technical checks remain passed: 26.066s, 1080x1920, VP9/Opus, 7,097,794 bytes; SHA-256 0e789ea0eaddb5b1e8a7999968143de7beb64f07ece25a918997073fe91072a6.
- Separate Pro safety workflow run 42417916241 completed successfully on the same commit. Intake run 42417916186 completed successfully including its artifact step.
- Status remains candidate-only / not approved. No actual production render, Telegram send, or TikTok publication. Human preference approval and rights record are still pending.

## 2026-11-07 — User explicitly requested one private test send; delivery remains blocked by required Pro gates

- User asked: send one test video to Telegram, then continue finding improvements. This is explicit intent for one test send, not production delivery or TikTok publishing.
- Rechecked Pro branch state. `content/pro/README.md` confirms there are no approved production manifests and no enabled end-to-end Pro preview workflow. `content/pro/CANDIDATE_RESEARCH_001.md` contains research-only religious candidates with human wording/context review pending and media rights/audio not reviewed. No Pro candidate manifest is present under `content/pro/`.
- `src/send_pro_preview_telegram.py` is an isolated candidate sender, but it requires a separate Pro preview bot token and chat ID, an exact candidate manifest, an MP4 under `output/pro_preview/`, matching asset rights records, and explicit CLI confirmation. The sender is not wired into a workflow. Existing original production Telegram workflow belongs to a different branch and must not be used as a shortcut.
- The reviewed WC-001 beach clip is a visual-only candidate, not an approved Pro rights-record asset; it cannot be used in a render/send. The Mixkit samples are also not cleared for this planned use.
- Therefore no Telegram request was made and no test was sent. Do not bypass source verification, audio/visual rights, private destination verification, or Pro isolation. Next work: complete one exact candidate's source review and per-asset rights clearance, configure/verify separate Pro preview credentials through the intended secure repo settings (never expose secrets), implement and test the Pro-only preview workflow, render one candidate, then use the user's already stated one-time test-send authorization only if all gates pass.
- TikTok auto-publishing remains disabled.


## 2026-11-07 — Review OpenDua as a possible Pro audio/text source

- Researched OpenDua / Ihsan Labs at the Human Development Fund as a possible source for a topic-specific dua preview.
- OpenDua's official developer/licensing page states that its independently authored English, transliteration, editorial metadata and dataset structure are CC BY 4.0, but its recitation recordings are covered by a separate written agreement and are **not** offered under the dataset licence. The page's attribution string names Muhammad Jumah, but attribution alone is not a reuse licence.
- Official sources checked: https://opendua.org/developers/ and https://opendua.org/; a representative entry also credits the collection Hisn al-Muslim and the reciter Muhammad Jumah: https://hdfund.org/resources/duas/visiting-the-sick-1/.
- Decision: do not download, embed, or use OpenDua audio for Pro until written permission covering editing, video synchronization, private review delivery, public social posting, commercial/monetized use, and territories is obtained and recorded. The CC BY 4.0 dataset licence must not be misapplied to the recording.
- This is a useful lead for locating exact dua wording and contextual metadata, but it does not remove the pending human exact-text/context review or the audio-rights gate. No manifest, rights record, render, Telegram send, or TikTok publication was created.
- Next: continue seeking an exact recording with explicit reusable permission or obtain direct written permission; keep candidate-only and fail closed meanwhile.


## 2026-11-07 — Reject IslamHouse audio for planned commercial/social reuse without permission

- Checked the published disclaimer for the Hisnul Muslim audio site at https://audio.islamihouse.com/p/disclaimer.html.
- The disclaimer says the site's content may be downloaded and used for personal use only, prohibits commercial use because some files have restrictions from publishers/reciters/production companies, and says RSS feeds require written permission for third-party app use.
- Decision: this source is not cleared for the planned Pro workflow, which may later publish/monetize social videos. Do not download, embed, edit, or synchronize its audio unless the relevant rights holder provides explicit written permission covering the intended uses.
- This is a useful negative rights finding, not an audio candidate. No file was downloaded; no rights record, manifest, render, Telegram send, or TikTok publication was created.
- Together with the OpenDua review, this confirms that freely accessible Islamic audio is not automatically reusable. Continue seeking explicit item-level permissions or a genuinely commercial-compatible recording licence.


## 2026-11-07 — SILMA TTS v1 identified as a conditional synthetic-voice route

- Researched the official SILMA TTS v1 model card: https://huggingface.co/silma-ai/silma-tts and vendor page https://silma.ai/open-source-arabic-tts-models.
- The model card identifies a 150M-parameter Arabic/English Fusha/MSA TTS model, accepts tashkeel, and states code is MIT while model weights are Apache-2.0. The card also says the model was trained on public and proprietary data and instructs users to disclose AI-generated audio; voice cloning requires explicit documented speaker consent.
- Important limitation: the demonstrated inference path uses a reference audio file and its transcription. No reusable rights evidence for the bundled reference voice sample was established in this review. Therefore do not assume the sample voice is cleared or clone a real reciter. The model's open licence is not a licence for any particular reference recording or a claim that synthetic output is religious recitation.
- Conditional decision: consider SILMA only for a clearly disclosed synthetic spoken-dua narration (not Quran recitation, not impersonation of a qari), after verifying a permitted reference voice or a non-cloning inference mode, Arabic pronunciation/tashkeel with human review, and output suitability. No model was downloaded or run, no audio generated, no manifest/rights record/render/Telegram send/TikTok publication was created.
- This is the first promising zero-upfront-cost model lead for synthetic narration, but it is not yet approved for the Pro test. Keep all production and delivery gates closed until a real audio sample has been checked.


## 2026-11-07 — 3arab-TTS VoiceDesign v2 researched as a no-reference Arabic narration candidate

- Inspected the model card for https://huggingface.co/sherif1313/3arab-TTS-500M-v2-VoiceDesign and its base model https://huggingface.co/sherif1313/3arab-TTS-500M-v2.
- The VoiceDesign card declares Apache-2.0, Arabic-only input, approximately 553M parameters, 48 kHz output, and says speaker style can be generated from natural-language descriptions without providing reference audio. This avoids cloning a real reciter or depending on an uncleared sample voice.
- The card describes MSA/Egyptian support and religious vocabulary/recitation-style training, but explicitly warns that pronunciation of rare words, names and religious texts may vary; it is not a dedicated Quran recitation system. Pro must never present synthetic speech as a named human reciter or as authentic Quran recitation.
- Material caveat: the author says a significant portion of training speech was collected from publicly available content; this review did not establish item-level consent/licensing for that training corpus. Apache-2.0 is the published model licence, not proof of perfect training-data provenance or guaranteed pronunciation.
- Conditional route: potentially test only as clearly labelled AI-generated spoken-dua narration (not Quran recitation), with fully vocalized text, native Arabic human listening review, exact output rights review, and explicit user review. Model is large; no inference/runtime or hardware test was performed, no files were downloaded, and no audio/video was generated.
- Decision: research candidate only; do not yet integrate into production or send to Telegram. Compare it with SILMA TTS v1, whose reference-voice sample rights remain unresolved. Keep current preview delivery gates unchanged.


## 2026-11-07 — 3arab-TTS executable path and compute review

- Inspected the upstream repository tree at `sherif1313/3arab-TTS`, default branch `main`, tree commit `ff242278c423d4cbb03920ab5e1dbb2d468ad26d`. It contains a real CLI (`infer.py`), a dedicated VoiceDesign UI (`app_voicedesign.py`), and the inference runtime modules; this is not merely a model card or a demo-only concept.
- The upstream README documents no-reference inference for VoiceDesign v2 using `--hf-checkpoint sherif1313/3arab-TTS-500M-v2-VoiceDesign`, `--caption`, `--no-ref`, and `--output-wav`. Therefore the candidate can be tested without a reference voice recording; do not provide or imitate any real reciter voice.
- The CLI downloads `model.safetensors` from Hugging Face and exposes device/precision options. Defaults use the runtime's detected device and FP32; sampling defaults to 40 steps. It also depends on a separate DACVAE repository (`facebookresearch/dacvae`) and the Arabic codec checkpoint repository `sherif1313/DACVAE-Arabic-32dim`.
- `pyproject.toml` declares project license MIT and requires Python >=3.10; the repository tree inspected did not include a standalone LICENSE file. This is a repository metadata/documentation gap to resolve against the model card and upstream owner before redistributing or vendoring code. It does not change the VoiceDesign model card's separate Apache-2.0 declaration for the model checkpoint.
- Dependencies are substantial: PyTorch >=2.10, torchaudio, torchcodec, Transformers <5, DACVAE, PEFT, SentencePiece, SilentCipher (pinned Git commit), Gradio, and related packages. The README documents CPU and CUDA 12.8 installation extras, but this review did not establish that a standard GitHub-hosted runner has adequate RAM/VRAM or that CPU inference is practical.
- Upstream README links a hosted Gradio Space at https://huggingface.co/spaces/sherif1313/3arab-TTS-VoiceDesign-v2. It is a possible manual evaluation surface, not an approved automated/private production dependency. No user dua text was submitted to it.
- Technical decision: a real no-reference CLI path exists, so the next experiment can be isolated to a one-off candidate audio test. Before any workflow edit/run, pin exact model and codec revisions, inspect the full model card/repository files and inference runtime for security/resource behavior, estimate checkpoint sizes and compute requirements, and verify that the available runner is suitable. Do not install or execute arbitrary upstream code in the production workflow.
- No model or codec was downloaded; no inference was run; no audio was generated or listened to; no dua text was submitted to the hosted demo; no Pro workflow was changed or started; no manifest, rights record, render, Telegram message, or TikTok publication was created. The Telegram send authorization and all existing delivery gates remain unchanged.


## 2026-11-07 — Hugging Face checkpoint size and hosted-demo availability

- Rechecked the public Hugging Face file listing for `sherif1313/3arab-TTS-500M-v2-VoiceDesign`: the `model.safetensors` checkpoint is listed at approximately 1.04 GB (repository total about 1.05 GB). The model card declares Apache-2.0.
- The base `sherif1313/3arab-TTS-500M-v2` checkpoint is listed at approximately 1.02 GB. The separate `sherif1313/DACVAE-Arabic-32dim` repository is also Apache-2.0, but its exact checkpoint file sizes and pinned revision still need to be established before planning a reproducible run.
- The official VoiceDesign Space is publicly listed and exposes generation controls, but its current listing reports hardware state `Zero`; this does not establish a currently running GPU endpoint or guarantee free inference capacity. Hugging Face Inference Providers does not currently list this model as deployed. Do not build an automated workflow around an assumed hosted endpoint.
- This reinforces that a self-hosted experiment requires a deliberate compute decision. The current repo's dependency set and 1+ GB acoustic checkpoint make an unverified CPU-only GitHub Actions run a poor default. No inference request was made and no audio was generated.
- Next: inspect exact DACVAE checkpoint files/revision and the Space app/runtime hardware configuration; then decide whether a bounded, isolated one-off test is feasible without paid cloud billing. No user secrets or credentials should be introduced for this research.
- No code/workflow/manifest/secret changes, workflow runs, downloads, audio generation, rendering, Telegram delivery, or TikTok publication occurred.


## 2026-11-07 — Hosted Space execution constraint confirmed

- Inspected the official Space's public commit history. Its inference function is decorated with `@spaces.GPU(duration=120)`, confirming that the hosted demo is designed to execute generation on a GPU and has a 120-second GPU-call duration cap in the inspected revision.
- The Space currently reports `Running on Zero`; this indicates no presently allocated paid hardware in the public listing, not a guarantee that a free GPU slot will be immediately available. Treat it as opportunistic manual evaluation only, not a reliable unattended service.
- The codec model card confirms the DACVAE checkpoint is a separate Apache-2.0 dependency; exact downloadable weight size/revision was not established in this pass.
- Result: do not launch a GitHub Actions CPU job as a speculative workaround, and do not add a dependency on a hosted demo that may be sleeping or lack GPU allocation. A reliable no-upfront-cost inference route remains unproven.
- No Space inference call, text submission, model download, audio generation, repository code change, workflow run, manifest, render, Telegram send, or publication occurred.


## 2026-11-07 — Free GPU options: ZeroGPU vs Colab

- Reviewed current official Hugging Face ZeroGPU documentation: existing ZeroGPU Spaces are free to use; the documented free-account allowance is 5 minutes of GPU time per daily quota window, with a shared RTX Pro 6000 Blackwell allocation (large tier 48 GB VRAM). Queue priority and availability are not guaranteed. The 120-second decorated call in the 3arab-TTS Space is within the documented five-minute free quota in principle, but actual inference duration and queue availability have not been tested.
- The upstream Space page currently reports `Running on Zero`; the official ZeroGPU documentation explains that this is a dynamic allocation model, so that status alone does not prove the demo is unavailable. A generation call may request shared GPU allocation, subject to queue/quota and the Space's own 120-second cap.
- This is currently the strongest no-upfront-cost candidate for a single manual quality test: the author-hosted Space already integrates the exact VoiceDesign model and GPU decorator. However, the current agent toolset cannot submit a form to the Space or listen to its returned audio. No user text has been submitted, no audio was generated, and no Telegram delivery is possible from this check alone.
- Google Colab's official FAQ confirms a free tier with possible GPU access, but explicitly says GPU availability/resources are not guaranteed, usage limits fluctuate and are unpublished; free notebooks can run up to 12 hours depending on availability and usage. It is a potential fallback for a one-off manually initiated notebook, not a dependable unattended production scheduler.
- Decision: do not configure a paid GPU Space, billing, API token, or new secret. Keep the hosted author Space as the preferred zero-cost single-test route and Colab as a secondary manual fallback. Before relying on either for production, measure actual generation time, exact Arabic pronunciation and repeatability.
- Sources reviewed: https://huggingface.co/docs/hub/spaces-zerogpu ; https://research.google.com/colaboratory/faq.html?hl=fr ; https://huggingface.co/spaces/sherif1313/3arab-TTS-VoiceDesign-v2 .
- No repo code/workflow changes, secret changes, model downloads, inference, audio generation/listening, manifest, video render, Telegram send, or TikTok publication occurred.


## 2026-11-07 — Verify 3arab-TTS no-reference inference and audio output path

- Re-inspected the upstream `sherif1313/3arab-TTS` source rather than relying only on the README. `infer.py` exposes `--no-ref` as an explicit mutually exclusive speaker-conditioning mode; `SamplingRequest` receives `no_ref=True` and the runtime creates a zero/reference-free speaker latent. The dedicated `app_voicedesign.py` UI also sets `ref_wav=None` and `no_ref=True` for generation. This confirms that the no-reference path is implemented in source, not just described in marketing text.
- The CLI writes WAV output using the sample rate returned by the codec runtime; the inspected runtime exposes `result.sample_rate` and passes it to `save_wav`. The VoiceDesign model card advertises 48 kHz output. This establishes the intended file format/sample-rate path, not that a real output has been generated or verified.
- Important product-safety note: the UI includes selectable captions/styles with several recitation-like or devotional prompts (for example, styles labelled tajwid/recitation). Pro must not use those presets or present generated speech as Quran recitation. The only permitted experiment remains a plainly disclosed synthetic spoken-dua narration, with a neutral non-imitative voice description and human Arabic pronunciation review.
- The hosted Hugging Face Space is a separate Gradio app from the upstream CLI/UI. Its public page currently reports “Running on Zero”; the model and codec are not listed as deployed Inference Providers. A public Space page does not prove an inference request was submitted or that audio can be retrieved automatically.
- The codec model card confirms Apache-2.0 licensing but the exact codec checkpoint file size/revision remains unresolved in this pass. The acoustic model's Apache-2.0 declaration likewise does not resolve training-corpus provenance; its card says a significant portion of training speech came from publicly available Arabic content. Do not claim complete dataset rights clearance.
- Official sources: https://huggingface.co/sherif1313/3arab-TTS-500M-v2-VoiceDesign ; https://huggingface.co/sherif1313/DACVAE-Arabic-32dim ; https://huggingface.co/spaces/sherif1313/3arab-TTS-VoiceDesign-v2 . Upstream source inspected: https://github.com/sherif1313/3arab-TTS/blob/main/infer.py ; https://github.com/sherif1313/3arab-TTS/blob/main/app_voicedesign.py ; https://github.com/sherif1313/3arab-TTS/blob/main/arabic_tts/inference_runtime.py .
- No model/codec download or inference was run; no dua text was submitted to a third-party service; no audio was generated, listened to, or human-reviewed; no manifest, media rights record, video render, Telegram send, or TikTok publication was created. No Pro workflow or secrets were changed. Existing one-time Telegram test authorization remains conditional on every strict delivery gate passing.


## 2026-11-07 — Verify hosted ZeroGPU Space interface and API integration feasibility

- Rechecked the public hosted VoiceDesign Space page and live Gradio frontend. The Space is currently labelled “Running on Zero”. Its public UI exposes Arabic text, gender/voice-style controls, generation steps, candidate count, seed, optional manual duration, and a Generate action; this is a real hosted interface, not a local deployment. Public page: https://sherif1313-3arab-tts-voicedesign-v2.hf.space/ .
- Hugging Face's official Spaces API documentation states that Gradio Spaces can be called as API endpoints and expose an OpenAPI document at `/gradio_api/openapi.json`. The target Space's OpenAPI URL could not be retrieved through the available GitHub/web readers in this pass, so the exact endpoint name, input ordering, output object schema, and returned audio-file retrieval method remain unverified. Do not write a production caller based on guessed Gradio parameters.
- The public Space currently uses ZeroGPU, and upstream source inspected earlier declares a per-inference GPU decorator with `duration=120`. This does not guarantee queue access or successful completion. Hugging Face documentation lists a free-account daily ZeroGPU quota of 5 minutes (subject to current plan rules and changes); one 120-second call is nominally within that quota, but cold-start, queue, actual runtime, and output handling have not been tested.
- The model card says the acoustic model has about 553M parameters, 48 kHz output, and was trained on roughly 700 hours; it acknowledges a significant portion of speech was collected from publicly available content. Apache-2.0 model licensing does not by itself establish rights to every training recording or guarantee pronunciation accuracy. The codec repo page declares Apache-2.0 and says no Inference Provider deploys it; it is used by the hosted Space rather than offered as a standalone hosted inference provider.
- Sources checked: https://huggingface.co/spaces/sherif1313/3arab-TTS-VoiceDesign-v2 ; https://sherif1313-3arab-tts-voicedesign-v2.hf.space/ ; https://huggingface.co/docs/hub/spaces-api-endpoints ; https://huggingface.co/sherif1313/3arab-TTS-500M-v2 ; https://huggingface.co/sherif1313/DACVAE-Arabic-32dim .
- No user text was submitted to the hosted Space; no third-party inference was triggered; no audio was generated, listened to, or reviewed. No repo workflow, secrets, Telegram delivery, or video render was changed. Next technical gate: retrieve and verify the exact Gradio OpenAPI schema and file-output handling, then design a safe one-off test without exposing private dua content or secrets.


## 2026-11-07 — Identify current Gradio API discovery route for hosted TTS

- Further checked Hugging Face's official Spaces API documentation. It confirms the documented OpenAPI route `/gradio_api/openapi.json`, and the newer official agent integration guide describes a discovery route `/gradio_api/info` plus an optional Space-specific `agents.md` manifest. These are discovery mechanisms only; they do not establish the target Space's actual schema.
- Tried to retrieve the target Space's `/agents.md` and `/gradio_api/info` through the available web reader; both returned inaccessible/internal errors. The target OpenAPI document was also not readable in the prior pass. Thus the exact endpoint and output/file handling remain unverified. Do not guess endpoint names or parameter order.
- Official references: https://huggingface.co/docs/hub/spaces-api-endpoints ; https://huggingface.co/docs/hub/spaces-agents ; target Space: https://sherif1313-3arab-tts-voicedesign-v2.hf.space/ . The live Space UI still exposes a Generate action and audio output, but no generation was submitted.
- No user dua text was submitted; no audio was generated/listened to; no code/workflow/secrets changed; no Telegram send or video render. Next step remains obtaining the exact target schema through a supported direct API/Space metadata route, then testing audio output retrieval before integrating it.


## 2026-11-07 — Inspect upstream VoiceDesign output contract (not yet target-Space API)

- Inspected the upstream repository's current `app_voicedesign.py` directly at https://raw.githubusercontent.com/sherif1313/3arab-TTS/main/app_voicedesign.py . Its generation callback `_run_generation` saves each candidate as a WAV file via `save_wav(..., result.sample_rate)`, then returns up to 32 audio filepath updates plus a detail log and timing log. The Gradio output components are `gr.Audio(type="filepath")`; generation is attached to a Generate button with the full input list. The UI queues with default concurrency limit 1.
- This proves the upstream source has a filepath-based WAV output contract, but it does NOT prove the currently hosted Space is running this exact file/revision or that the Space's public API uses the same endpoint name, input schema, or file-serving route. The hosted page UI differs in visible controls from this upstream source, so do not bind production integration to guessed output indices or `api_name`.
- The public Space UI confirms a single Generate control and audio result slots, but its OpenAPI/info routes remain inaccessible to the available reader. No inference was submitted.
- Practical design implication: if the hosted Space API schema is later confirmed, retrieve the returned Gradio filepath using the supported client response and immediately copy it into a controlled temporary location, then validate actual WAV codec/sample rate/duration and listen-review before video composition. Do not assume the returned path is permanent or directly downloadable.
- No model was run; no user text/audio submitted; no video/Telegram send; no workflow or secrets changed. Existing sender gates remain closed until all approvals and assets exist.


## 2026-11-07 — Confirm official Gradio API invocation and remote audio-file retrieval mechanism

- Rechecked current official Hugging Face Spaces API docs. They explicitly document: endpoint discovery via the Space footer's “Use via API”, `gradio_client.Client(...).view_api()`, async `submit()/job.result()`, REST queue submission at `POST /gradio_api/call/<endpoint>`, and SSE polling at `GET /gradio_api/call/<endpoint>/<event_id>`. They also document that ZeroGPU quota is charged to the caller's account and currently list 5 minutes daily for a Free account (quota may change).
- Rechecked official Gradio Python Client docs/source: the client downloads returned output files to a local temp directory by default; with `download_files=False`, it returns a FileData object containing the remote filepath instead. Thus WAV retrieval is supported by the client when the actual endpoint returns a Gradio filepath output. Official docs/source: https://huggingface.co/docs/hub/en/spaces-api-endpoints ; https://gradio.app/docs/python-client/client ; https://github.com/gradio-app/gradio/blob/main/client/python/gradio_client/client.py .
- The target Space-specific schema remains unavailable from our readers: direct attempts to open its `/gradio_api/openapi.json`, `/gradio_api/info`, and `/agents.md` returned access/internal errors. Therefore endpoint name, actual input order/types, exact output index, and the deployed Space's current source revision are still unverified. Do not implement a caller against guessed values. The public documentation establishes a general mechanism, not target-specific compatibility.
- Safe next implementation step, once exact schema is obtained: use a pinned `gradio_client` version with a bounded timeout/queue wait, explicit API name and exact typed inputs, save returned WAV locally, then validate RIFF/WAV structure, sample rate, channel count, duration and file size before any human listen-review. Treat ZeroGPU quota/queue errors as a failed attempt; do not auto-retry in a way that spends quota unexpectedly.
- No Space inference request was submitted, no HF token was created or used, no model/audio generated, no audio listened to, no video rendered or Telegram message sent. No workflow, secrets, or sender code changed.

## 2026-11-07 — Inspect deployed Pro TTS Space source and identify actual inference payload/output type

- Located the actual hosted Space source through its Hugging Face file tree and inspected app.py at revision 73b8cb9 (the same revision displayed in the source page). This is stronger evidence than the separate upstream repository's app_voicedesign.py and corrects the earlier assumption that hosted output is a filepath.
- Confirmed deployed Space's generation callback is gradio_inference; its Generate button passes 21 inputs in this exact order: text, caption, num_steps, num_candidates, seed_raw, seconds_raw, duration_scale, t_schedule_mode, sway_coeff, cfg_guidance_mode, cfg_scale_text, cfg_scale_caption, cfg_scale_raw, cfg_min_t, cfg_max_t, context_kv_cache, max_text_len_raw, max_caption_len_raw, truncation_factor_raw, rescale_k_raw, rescale_sigma_raw.
- Confirmed callback calls the GPU inference function with no_ref=True, and converts each generated waveform to a Gradio audio tuple (sample_rate, numpy_waveform). It returns up to 32 audio outputs followed by a text log; output components use gr.Audio(type="numpy"), not filepath. Therefore the integration should expect a sample-rate/waveform pair, then encode it into a controlled WAV file itself and validate it. Do NOT use the upstream standalone app's filepath assumptions for this deployed Space.
- UI defaults visible in source include 40 steps, 1 candidate, automatic duration (blank seconds), duration scale 1.0, linear time schedule, sway -1.0, independent CFG, text CFG 3.0, caption CFG 4.0, CFG min/max 0.5/1.0, KV cache true; advanced text/caption lengths, CFG override, truncation and rescale fields default blank. Endpoint name still should be confirmed by runtime Client.view_api() or the Space's Use via API output; do not hardcode an unverified API name. The callback name is a useful candidate, not yet a verified public endpoint name.
- The live Space UI and source page report Running on Zero; callback is decorated with @spaces.GPU(duration=120). The UI source returns numpy audio, so no remote filepath retrieval is required if the API client returns the documented (sample_rate, waveform) representation. The exact serialized response shape still needs a schema/API client inspection before integration.
- Source inspected: https://huggingface.co/spaces/sherif1313/3arab-TTS-VoiceDesign-v2/blob/main/app.py (revision 73b8cb9); source lines 297-320, 408-415, 550-570, 572-655. Official Gradio API docs: https://huggingface.co/docs/hub/spaces-api-endpoints .
- No inference request was submitted, no user dua text used, no audio generated/listened to, no HF token created, no workflow/secrets changed, no Telegram send/video render. Next step: confirm public API endpoint/schema and output serialization with Client.view_api() before writing the adapter.


## 2026-11-07 — Derive the hosted Space's default Gradio endpoint name from deployed source

- Inspected the deployed Space `app.py` at revision `73b8cb9`. The Generate button calls `generate_btn.click(fn=gradio_inference, inputs=[...], outputs=[...])` and does not pass an explicit `api_name` or `api_visibility` argument.
- Checked current Gradio event API documentation/source: when `api_name` is omitted/None, Gradio uses the function name as the API endpoint; the default API visibility is public. Therefore `/gradio_inference` is the source-derived expected endpoint name for this Space revision. This is a strong code-level derivation, not a successful live `view_api()`/OpenAPI verification; the Space runtime API metadata endpoint is still inaccessible to our current reader. Keep the adapter fail-closed: discover/validate the endpoint and schema at startup, or require an explicit reviewed schema fixture; do not silently fall back to guessed positional inputs.
- The deployed source contract remains 21 inputs and outputs `[*out_audios, out_log]`, where each visible audio output is `gr.Audio(type="numpy")`; generation returns a list of `(sample_rate, waveform)` tuples plus a log. The adapter must support this representation and reject unexpected shapes.
- Evidence: deployed source https://huggingface.co/spaces/sherif1313/3arab-TTS-VoiceDesign-v2/blob/main/app.py (revision 73b8cb9; lines 572–655); Gradio event API docs/source https://github.com/gradio-app/gradio/blob/main/gradio/events.py and https://github.com/gradio-app/gradio/blob/main/gradio/component_meta.py.
- No inference was submitted, no ZeroGPU quota used, no audio/video generated or listened to, no Telegram send, no secrets or workflows changed. Next safe step remains a metadata-only runtime schema check from a supported environment; only after that should a pinned client adapter be implemented and covered by mocked serialization tests.


## 2026-11-07 — Recheck hosted Space metadata routes and official API contract

- Rechecked the official Hugging Face Spaces API documentation. It confirms that each Gradio Space exposes `/gradio_api/openapi.json`, and recommends `gradio_client.Client(...).view_api()` to inspect the actual deployed endpoints and parameter schema. Public Spaces may be called without a token; auth can improve rate limits. Source: https://huggingface.co/docs/hub/en/spaces-api-endpoints.
- Rechecked the target Space source listing and pinned deployed app revision `73b8cb9`. The source-derived endpoint hypothesis remains `/gradio_inference`, but the exact runtime schema still has not been retrieved.
- Tried metadata-only reads of the target Space's `/agents.md` and `/gradio_api/info` routes through the available web reader; both returned an internal access error. No inference POST was made and no GPU quota was consumed.
- Decision: do not implement a production caller from inferred function name/positional arguments alone. The adapter must first validate the live API description (or an exact schema emitted by `Client.view_api()`) and then assert expected input/output counts and types before any generation call.
- No code/workflow/secrets changed; no audio/video generated or listened to; no Telegram send. This is a research-only update.


## 2026-11-07 — Check Hugging Face's new Space agent-discovery route

- Found the official Hugging Face “Spaces as Agent Tools” documentation. It describes a plain-text `https://huggingface.co/spaces/<owner>/<space>/agents.md` endpoint intended to provide the exact API schema URL, call/poll templates, file-upload instructions, and authentication hint for a Space. It also identifies `/gradio_api/info` as the schema endpoint. Source: https://huggingface.co/docs/hub/en/spaces-agents.
- Applied that documented discovery route to the target Space `sherif1313/3arab-TTS-VoiceDesign-v2`. The `agents.md` URL still returned an internal access error through the available reader, so no target-specific schema was obtained. The already-observed direct `/gradio_api/info` and OpenAPI route reads remain inaccessible through this reader.
- This narrows the next verification step: retrieve the target's `agents.md` or `/gradio_api/info` from a supported execution environment, then compare its endpoint and typed input/output schema against the source-derived `/gradio_inference` hypothesis and 21-input/numpy-output contract. Do not submit an inference request just to discover the schema.
- No source code, workflow, branch settings, secrets, or bot configuration changed. No model inference, ZeroGPU usage, audio/video generation, or Telegram send occurred.


## 2026-11-07 — Alternative metadata inspection route

- Rechecked the target Space's documented agent descriptor at `https://huggingface.co/spaces/sherif1313/3arab-TTS-VoiceDesign-v2/agents.md` and its live Gradio metadata endpoint at `https://sherif1313-3arab-tts-voicedesign-v2.hf.space/gradio_api/info`; both remain inaccessible through the available web reader (internal access error). No generation endpoint was called.
- Identified the official Gradio team's `hf-gradio` CLI as another metadata-only option: `hf-gradio info <space_id_or_url>` returns endpoint names, typed parameters, defaults/required flags, and output schema. This is a possible route from a supported runner, but it has not been installed or executed in this environment. Source: https://github.com/gradio-app/hf-gradio.
- Implementation gate remains unchanged: do not infer positional arguments from upstream source alone; first obtain the deployed schema, pin the client/tool version, and assert its exact inputs/outputs before any inference. No inference, GPU quota, secrets, workflows, Telegram, or video output were touched.


## 2026-11-07 — Add metadata-only CI probe for the hosted TTS Space

- Added `.github/workflows/inspect-pro-tts-space-api.yml` on `feature/quran-video-pro`. It is restricted to that branch, installs pinned `hf-gradio==0.4.1`, runs only `hf-gradio info sherif1313/3arab-TTS-VoiceDesign-v2`, validates that the returned schema is a non-empty JSON object, prints endpoint/input/output counts, and uploads the schema for review. It contains no prediction/inference command, no HF token, no secrets, no Telegram integration, and no GPU invocation.
- Tool documentation confirms `hf-gradio info` discovers endpoint names, typed parameters, defaults/required flags and return values; `predict` is a separate command and is not called. Version 0.4.1 was checked in the tool's project metadata. Sources: https://github.com/gradio-app/hf-gradio (README and pyproject.toml).
- Verified the workflow file exists on the Pro branch (blob SHA `8ccd2228dfcc217f9205859cf1c94c5477398479`) and branch head is commit `913d1672f0915d51a9bd39e1351724539ee415d3`. Checked recent Actions runs after the commit: no run for this workflow/commit is visible, so execution is NOT confirmed. The available GitHub actions tools expose job/run inspection and reruns, but no workflow-dispatch action; do not claim the schema probe ran. Existing prior runs are unrelated and were not rerun.
- No model inference, ZeroGPU usage, audio/video generation, Telegram send, secrets changes, or production changes occurred. Next step is obtain a real run of this metadata-only workflow (or execute the same pinned `hf-gradio info` command in a supported runner), then inspect the actual schema before implementing the caller.


## 2026-11-07 — Live hosted TTS API schema successfully discovered and validated

- Executed metadata-only workflow run `42419657308` (job `128545139427`) on commit `140487cadcf68fee3ed9caab8f5de17024146af6`; conclusion SUCCESS. Pinned CLI install `hf-gradio==0.4.1` succeeded. Live Space metadata call `hf-gradio info sherif1313/3arab-TTS-VoiceDesign-v2` succeeded.
- Actual discovered endpoints: `/gradio_inference`, `/_on_voice_gender_change`, `/_on_voice_style_change`, `/_on_t_schedule_mode_change`. Main generation endpoint is exactly `/gradio_inference`, with 21 inputs and 33 outputs. Workflow assertions passed: first input is required string `text`; first 32 outputs are file paths; output 33 is a string log. This confirms the source-derived endpoint hypothesis and resolves the API metadata blocker.
- Exact ordered main-endpoint input names from the live schema: `text` (required string), `caption` (optional string), `num_steps`, `num_candidates`, `seed_raw`, `seconds_raw`, `duration_scale`, `t_schedule_mode`, `sway_coeff`, `cfg_guidance_mode`, `cfg_scale_text`, `cfg_scale_caption`, `cfg_scale_raw`, `cfg_min_t`, `cfg_max_t`, `context_kv_cache`, `max_text_len_raw`, `max_caption_len_raw`, `truncation_factor_raw`, `rescale_k_raw`, `rescale_sigma_raw`. Defaults/ranges/enums are available in the run log; do not hard-code unreviewed values beyond the confirmed schema.
- The first metadata run `42419519489` successfully discovered the schema but failed only at artifact upload because repository Actions artifact storage quota was exhausted. Updated the workflow to remove artifact upload, validate the live contract directly, and write the full endpoint JSON schema to the GitHub Actions job summary. The subsequent run `42419657308` completed successfully, avoiding the storage quota issue.
- This was metadata discovery only: no `predict`, `submit`, inference POST, or audio generation occurred; no ZeroGPU quota was consumed; no audio was listened to; no Telegram message was sent; no secrets or external accounts were changed.
- Next step: implement a strictly typed, fail-closed Gradio client adapter using the verified endpoint and ordered parameter schema; use only a neutral non-imitative voice description for synthetic spoken-dua narration (never Quran recitation), with bounded call duration and one attempt. Then add mocked contract/serialization tests before any actual inference. Human Arabic pronunciation/listening review remains mandatory before rendering or sending a preview.


## 2026-11-07 — Add one-shot TTS client wrapper and offline tests

- Added `src/pro_tts_space_client.py`: validates the live Gradio API metadata against the exact 21 ordered input names and 33 output contract; builds named inputs from live defaults; requires non-empty dua text and explicit neutral voice description; forces exactly one candidate; uses one Gradio `Client.submit` call with a bounded `Job.result(timeout=...)`; does not retry after timeout; validates exactly one returned audio path, a final text log, file containment inside the isolated output directory, and a readable WAV with valid channels/sample rate/frame count.
- The wrapper has no auto-run behavior. It only submits inference when a caller explicitly invokes `generate_spoken_dua_once`. No inference has been invoked. This function is for clearly disclosed synthetic spoken dua narration only, never Quran recitation or imitation of a real reciter.
- Added `tests/test_pro_tts_space_client.py` with 12 offline tests covering schema drift, named payload/defaults, required text, one output path, multiple candidates, invalid shape, one-submit success, timeout/no retry, and output path isolation. Updated Pro push safety workflow to run these tests and pinned `hf-gradio==0.4.1` in `requirements.txt` (which supplies the compatible `gradio_client` dependency).
- GitHub Actions run `42419881895` (commit `c98c797cdc696aa7e92552b478b2180cfdf20c4d`) completed SUCCESS. The new TTS test suite reported `Ran 12 tests ... OK`; the full configured Pro offline safety test step also passed, including existing renderer, delivery, rights and ledger suites. A subsequent requirements pin commit is `f1d49d3b93fd02fbc88c4d144941f2a257195ab5`; that commit's workflow run is not yet separately verified here.
- No ZeroGPU/GPU inference, no audio generated or listened to, no video rendered, no manifest/rights approval created, no Telegram send, and no secrets changed. The next gate is selecting a verified non-Quran hadith dua text/source and a rights-reviewed background, then a single explicitly scoped inference attempt and human listening review before video rendering or Telegram delivery.


## 2026-11-07 — Select an authenticated morning/evening dua text candidate

- Researched a non-Quran supplication suitable for the spoken-dua prototype: the dua narrated from Abdullah ibn Umar in Sunan Abi Dawud 5074. Sunnah.com records the hadith and grades it Sahih (Al-Albani): https://sunnah.com/abudawud:5074. The Saudi Alifta hadith portal independently displays the Arabic matn and identifies the same narration/number: https://sunna.alifta.gov.sa/BookToc/ViewMatnPage?bookId=3&mainId=95942.
- The report says the Prophet ﷺ used these supplications in the morning and evening. Candidate text from the matn (using the Uthman wording as shown in the report):
  `اللَّهُمَّ إِنِّي أَسْأَلُكَ الْعَافِيَةَ فِي الدُّنْيَا وَالْآخِرَةِ، اللَّهُمَّ إِنِّي أَسْأَلُكَ الْعَفْوَ وَالْعَافِيَةَ فِي دِينِي وَدُنْيَايَ وَأَهْلِي وَمَالِي، اللَّهُمَّ اسْتُرْ عَوْرَاتِي وَآمِنْ رَوْعَاتِي، اللَّهُمَّ احْفَظْنِي مِنْ بَيْنِ يَدَيَّ وَمِنْ خَلْفِي، وَعَنْ يَمِينِي وَعَنْ شِمَالِي وَمِنْ فَوْقِي، وَأَعُوذُ بِعَظَمَتِكَ أَنْ أُغْتَالَ مِنْ تَحْتِي.`
- Text selection is research-only. The report contains a transmitted wording difference at `عَوْرَتِي` / `عَوْرَاتِي`; the selected plural wording follows the explicitly noted Uthman version. Before any TTS call, compare the exact vocalized text against the chosen hadith edition, obtain a competent Arabic pronunciation review, and keep the on-screen source/reference visible. Do not label synthetic narration as recitation.
- This is a content candidate, not an approved final video script. No inference, GPU quota, audio/video generation, rights approval, manifest, rendering, or Telegram send occurred. WC-001 remains an unapproved background candidate; its suitability for this dua has not been accepted.


## 2026-11-07 — Cross-check the dua matn and narrator's wording variant

- Cross-checked the Arabic matn against Sunnah.com Sunan Abi Dawud 5074 and a separately hosted English/Arabic Sunan Abi Dawud volume. Both show the base wording `اللَّهُمَّ اسْتُرْ عَوْرَتِي` and explicitly attribute the alternative plural `عَوْرَاتِي` to the narrator Uthman; the following `وَآمِنْ رَوْعَاتِي` is also present. Sources: https://sunnah.com/abudawud/43/302 and https://www.islamland.com/uploads/books/sunan-abu-dawud-volume-5-ahadith-4351-5274.pdf.
- Correct production-script handling: do not silently merge narrator variants. If using the Uthman route, state in source notes that the plural `عَوْرَاتِي` is Uthman's transmitted wording; retain `وَآمِنْ رَوْعَاتِي` as printed in that version. The Sunnah.com grading shown is Sahih (Al-Albani). A separate Arabic hadith listing also marks the report Sahih: https://mohaddis.com/View/Abu-Daud/T2/5074.
- This is textual source verification only, not a human tashkeel/pronunciation sign-off. The final vocalized reading still needs qualified Arabic review before TTS. No inference, GPU use, audio/video generation, manifest, rendering, Telegram send, or bot/secrets change.


## 2026-11-07 — Locate a fully vocalized primary hadith matn for review

- Located the Saudi General Presidency for Scholarly Research and Ifta (Alifta) hadith portal entry for Sunan Abi Dawud 5074: https://sunna.alifta.gov.sa/BookToc/ViewMatnPage?bookId=3&mainId=95942. Its displayed Arabic narration includes tashkeel across the matn and identifies the narrator wording: `عَوْرَتِي`, with Uthman's variant `عَوْرَاتِي` followed by `وَآمِنْ رَوْعَاتِي`.
- This provides a better vocalized textual reference than the previously consulted unvocalized/partially vocalized editions. It does NOT by itself constitute expert recitation/pronunciation sign-off; the script must still be checked by a competent Arabic reader before any hosted TTS inference. Preserve the narrator-variant note and do not combine readings without attribution.
- Cross-check: Sunnah.com lists the report as Sahih (Al-Albani): https://sunnah.com/abudawud/43/302. The Alifta portal page confirms the matn and hadith number.
- Research only. No text was submitted to the TTS service, no GPU quota used, no audio/video generated or reviewed, no background approved, no manifest/render created, and no Telegram send. Existing Pro preview delivery gates remain closed.


## 2026-11-07 — Identify a vertical background-video lead for dua visuals

- Found a potentially useful vertical nature clip on Pixabay: `Creek, river, sunrise`, creator FreeFallAnnie, source https://pixabay.com/videos/creek-river-sunrise-morning-nature-184883/. The listing reports MP4, 1080x1920, 29 FPS, published 2023-10-14, and says it is free under the Pixabay Content License.
- Pixabay's official license summary permits free use, adaptation, and use without required attribution, but prohibits standalone redistribution and warns that some uploads may carry third-party rights requiring separate checks: https://pixabay.com/service/license-summary/.
- Candidate status only: visual content has not been downloaded or inspected frame-by-frame; exact duration, file hash, source provenance, and any third-party rights remain unverified. Do not add it to an approved asset manifest or use it in a render until downloaded through an allowed route, inspected, and recorded. This is only a possible river/sunrise theme; it does not replace WC-001 or establish a background approved by the user.
- No inference, GPU use, audio/video render, manifest approval, Telegram send, or production-bot interaction occurred.


## 2026-11-07 — Re-check Pixabay candidate listing and current license boundaries

- Opened the exact Pixabay listing for `Creek, river, sunrise` (FreeFallAnnie): https://pixabay.com/videos/creek-river-sunrise-morning-nature-184883/. The page confirms MP4, 1080×1920, 29 FPS, published 2023-10-14, and a Pixabay Content License label. The accessible page text does not expose the exact clip duration or an inspectable frame preview; these remain unknown.
- Re-read Pixabay's official Content License Summary: free use, no mandatory attribution, and adaptation into new works are allowed, but standalone redistribution is prohibited and additional third-party rights may still apply. Full Terms of Service were updated 2026-10-20; they further clarify that use must not imply false endorsement and that third-party rights/consents remain the user's responsibility. Sources: https://pixabay.com/service/license-summary/ and https://pixabay.com/service/terms/.
- Decision: retain as an unapproved candidate only. The web page alone is not sufficient to verify actual imagery, audio track, duration, source file hash, or absence of third-party rights. No automated scraping/bulk downloading; no download or frame extraction was performed. Before use, obtain the file through the site's normal download flow, inspect it, record exact hash/metadata and retain a copy of the listing/license evidence. Do not use until this evidence exists.
- Latest previously verified Pro offline safety run remains `42419888630` on code commit `f1d49d3b93fd02fbc88c4d144941f2a257195ab5`, conclusion SUCCESS. This run predates the current documentation-only append and does not certify any background or audio/video output.
- No TTS inference, GPU quota, audio/video render, Telegram send, secret changes, or production workflow interaction occurred.


## 2026-11-08 — Pro pre-inference safety audit: Arabic review gate remains incomplete

- Re-fetched the Pro branch ref: current HEAD is `2d0b5e8abde5500def0c29d9ef3da38ed4bc87b0`; no other branch was changed.
- Re-read `src/pro_orchestrator.py`, `src/validate_content_manifest.py`, `src/pro_tts_space_client.py`, `src/render_dua_video.py`, and the review/media-rights policies.
- Confirmed the candidate-preview validator intentionally permits `human_reviewed: false` for a candidate preview, while the TTS adapter's public `generate_spoken_dua_once` function accepts only raw text and a voice caption. Its docstring says "reviewed" but the function does not independently require a review record or bind an approval to the exact text. This is a real fail-closed gap before inference, even though the current hadith item has not been added as a manifest and no inference has been run.
- Decision: do not call the hosted TTS Space or render/send any preview. Before first inference, add an enforceable review-record contract bound to the exact Arabic text (for example, SHA-256 + source/reference + reviewer decision/date), test rejection of missing/mismatched/unapproved records, and require the approved record at the TTS call boundary. A manifest flag alone or this log entry is not a reviewer sign-off.
- The current hadith 5074 candidate still has no independent human Arabic pronunciation/diacritic sign-off; the exact recording/background rights and user-approved background are also not ready. Telegram preview credentials are still not configured.
- No GPU inference, audio/video generation, media download, Telegram request, production workflow, secret change, or production ledger/history change occurred.


## 2026-11-08 — Enforce text-bound human review before hosted TTS

- Updated `src/pro_tts_space_client.py`: `generate_spoken_dua_once` now requires a structured human-review record before constructing the hosted client or making any inference request. The gate checks SHA-256 of the exact UTF-8 Arabic text, explicit `approved` decision, exact-source comparison, diacritics/pronunciation review, reviewer identifier, HTTPS source URL, exact source reference, and a valid ISO-8601 review timestamp.
- Added offline tests for exact-text hash binding, missing/unapproved review records, missing pronunciation review, and non-HTTPS source evidence. Updated mocked generation calls to supply a test-only review record. These fixtures are synthetic test data, not evidence that the actual hadith candidate has been reviewed.
- GitHub Actions run `42431135692` on the intermediate code-only commit failed because the three pre-existing generation fixtures had not yet been updated to pass the new required keyword argument. The fixture updates were then committed; the latest full Pro safety run is `42431164497` on commit `5d78bc338c3a32185ede495d0e354539c745772d`, status was in progress at the time of this log entry. Do not report tests as passing until this exact run completes successfully.
- No live TTS inference, GPU use, audio/video render, media download, Telegram send, production workflow, secret change, or production ledger/history change occurred. The actual hadith text still lacks a real independent human Arabic review and therefore remains blocked.


### Verification update — 2026-11-08

- The latest Pro offline safety workflow completed successfully: run `42431164497`, tested code commit `5d78bc338c3a32185ede495d0e354539c745772d`, all job steps successful, including `Run all Pro offline safety tests`.
- This validates the offline test suite and the new TTS review-record gate against synthetic fixtures only. It does not certify the real hadith review, a generated audio sample, media rights, or a finished video.


### Review-record hardening follow-up — 2026-11-08

- Tightened `validate_human_review` further: review timestamps must now include an explicit timezone, and source URLs containing embedded username/password credentials are rejected.
- Added offline regression tests for naive timestamps and credential-bearing HTTPS URLs.
- Workflow run `42431295486` (code commit `0ff579e14cd1811e03f660502477a41b79e6e74a`) was still running when checked; run `42431300654` (latest code commit `cece8e4f373eb711f01dd5ceaf8178c21ad69e80`) was queued. Do not treat these additional hardening tests as passed until the latest run completes successfully.
- These records remain synthetic test fixtures. They do not represent actual review or approval of Sunan Abi Dawud 5074, and no TTS inference or media generation was performed.


### Verification update — 2026-11-08 (review-record hardening)

- Latest offline safety workflow run `42431300654` completed with conclusion SUCCESS on code commit `cece8e4f373eb711f01dd5ceaf8178c21ad69e80`; the job's branch guard and full offline safety test step both succeeded.
- Inspected the job log: `tests/test_pro_tts_space_client.py` ran 17 tests and passed, including the new timezone-aware timestamp and credential-bearing source URL rejection cases. The renderer suite ran 9 tests and passed; the Pro orchestrator suite ran 16 tests and passed.
- The earlier hardening commit `0ff579e14cd1811e03f660502477a41b79e6e74a` also completed SUCCESS.
- Scope remains unchanged: tests use synthetic review fixtures. No actual Arabic reviewer sign-off, hosted TTS inference, audio playback, video render, background approval, Telegram credentials or send, or TikTok publication exists. The candidate hadith remains blocked pending genuine independent review and media clearance.


### TTS timeout validation hardening — 2026-11-08

- A further code review found that the documented finite-positive timeout check did not explicitly reject IEEE NaN/infinity; NaN can evade ordinary less-than/greater-than comparisons.
- Updated `generate_spoken_dua_once` to reject non-finite timeout values before constructing the hosted client, and added regression coverage for NaN, positive/negative infinity, zero, negative values, and booleans. The test asserts the client factory is never called for invalid values.
- Code commit: `ba02cbbf47a2e27a8a24a82a8cafb62e4b81bb71`; associated workflow run `42431406565` was still in progress at log time. Test commit: `5db9ed586701d3e67dd8851fa547e062bf7ef951`; associated workflow run `42431415179` was queued. Do not claim these latest changes passed until the run for the test commit completes successfully.
- No inference, audio/video generation, media download, Telegram send, or production-path action occurred.
