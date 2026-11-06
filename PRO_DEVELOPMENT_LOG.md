# Quran Video Pro — Development Log

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
