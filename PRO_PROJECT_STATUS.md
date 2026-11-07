# Islamic Dua & Adhkar Pro — Project Status

- Repository: `samiouess-ux/IslamicTikTokAutomation`
- Active Pro branch: `feature/quran-video-pro`
- Product scope: dua and adhkar videos only.
- Quran production remains on `feature/telegram-review-notifications`; do not modify it.
- Original Telegram bot reuse is desired through a separate Pro-only route, not yet enabled.
- TikTok publishing remains manual; automatic publishing is prohibited.

## Verified Pro implementation
- `src/validate_content_manifest.py`: strict dua/dhikr source, exact Arabic, human-review and hadith-grading checks.
- `src/render_dua_video.py`: dedicated dua/dhikr slideshow renderer; Pro orchestration currently applies a 40-second cap.
- `src/pro_orchestrator.py`: Pro-only dua/dhikr planning, approved-manifest selection, recent-repeat avoidance, dry-run preflight and optional render path.
- `src/send_pro_telegram.py`: isolated Pro-branded sender with dua/dhikr-only, review-only, and reservation-ledger safeguards. Its `--reservation-persisted` mode requires a pre-existing reserved entry matching manifest ID, content type, and workflow run ID.
- `src/pro_delivery_cycle.py`: fail-closed two-phase coordinator. It verifies the ledger path belongs to the Pro checkout, requires an explicit successful push result before sender invocation, and requires outcome persistence afterward. It is not connected to or run by a delivery workflow.
- `src/prepare_pro_telegram_caption.py`: validated review caption preparation.
- Quran-specific `src/orchestrator.py`, `src/render_video_scenes.py`, and production workflow must remain untouched.

## Delivery ledger and Telegram integration — 2026-11-06
- Production cleanup is complete: `src/pro_delivery_ledger.py` and `tests/test_pro_delivery_ledger.py` are absent from `feature/telegram-review-notifications`.
- Recreated both files only on `feature/quran-video-pro`. The ledger supports reserved, delivered, and uncertain states, requires a positive Telegram message ID for delivery confirmation, and requires explicit human confirmation before releasing an uncertain reservation.
- The ledger uses atomic JSON replacement and a process-level file lock. This does not yet persist state across separate GitHub workflow runs or serialize independent runners.
- `src/send_pro_telegram.py` now reserves before contacting Telegram, never auto-retries, marks failed/ambiguous outcomes uncertain, and records delivered only after a valid Telegram message ID.
- `src/prepare_pro_telegram_caption.py` now includes the stable manifest ID needed by the sender.
- Sender tests cover successful confirmation, uncertain outcomes blocking a second attempt, refusal when a pre-persisted reservation is missing, and ambiguous timeout handling in pre-persisted mode.
- Persistence-helper tests cover wrong-branch refusal, unrelated staged changes, ledger-only commits, and remote push failure (which must raise rather than report success).
- Delivery-cycle tests cover first-push failure or no-op blocking sender invocation, uncertain-state persistence, failure to persist an uncertain outcome, persist/send/persist ordering, final-push failure behavior, and rejection of a ledger path outside the persisted checkout.
- **Important:** no Pro workflow currently persists the ledger between runs. Cross-run duplicate protection is therefore not yet complete, and Telegram delivery remains disabled.
 
## Validation status
- Unit tests have NOT been run; no test is reported as passing. Additional sender and persistence failure-boundary tests were committed on 2026-11-06, but remain unexecuted.
- No Pro preflight command, MP4 render, GitHub Actions workflow, Telegram API call, or TikTok publish has occurred.
- No secrets, Cron settings, or production workflow logic were changed.
- Pro has no verified content library yet; do not attempt delivery until reviewed manifests exist and idempotency is safely implemented.

## Cross-run persistence design
- Design committed in `PRO_LEDGER_PERSISTENCE_DESIGN.md` (commit `e3c50a6c66a13d23c753cb9c7f975c1b633accd5`).
- Selected approach: commit the ledger JSON to this Pro branch using normal checkout/commit/push, protected by one fixed Actions concurrency group.
- Required order: persist reservation before Telegram; send once; persist delivered/uncertain outcome. A failed final push leaves the pre-send reservation blocking duplicates.
- A manual-only Pro safety-test workflow exists at `.github/workflows/pro-safety-tests-manual.yml`; it is not a delivery workflow and has not been dispatched. No reviewed `content/pro` manifests exist.

## Next steps
1. Review the new `src/pro_delivery_cycle.py` and tests, then run the offline safety suite only after explicit approval. The coordinator now wires reserve -> persist -> send -> persist in code, but is not connected to any delivery workflow.
2. Build a separate delivery workflow only after the two-phase protocol is integrated and reviewed content exists. The current manual-only workflow runs offline tests only; no delivery workflow or schedule exists.
3. Build a reviewed dua/dhikr content library from trustworthy primary sources.
4. Dispatch the manual-only safety-test workflow only after explicit user approval, then record exact test results.
5. Ask for explicit approval before any workflow dispatch, render, or Telegram send.

## Latest Pro-only commits — 2026-11-06
- Sender failure-boundary tests: `a9dcc3129e80e20605a5d858627a0827459e2f1d`.
- Ledger push-failure test: `927f0b1c0f5f49bba02bba6f228b186f6c245c9f`.
- Documentation update: `f99813748c9f6c3809f84220301ae1db30636e82`.
- Tests remain unexecuted; the manual-only test workflow remains undispatched.
- Two-phase cycle implementation: `e34b1d087b009e010809afd92a96cd2f791b2f72`.
- Cycle tests: `82d66a045cb8afd3a293960df3640c485d741ea3`.
- Manual test workflow update: `fda5a62f89636b004e0bce77980e3cb9f26dc7fb`.
- Persistence test fixture correction: `5bf69ce275b077a04ba92097b5fad2ee80c7d0ec`.
- Strict persistence confirmation hardening: `efc65604523b0c3579fd8b38c3a8a927a8a3a7a8`.
- Additional fail-closed tests: `885db308e84ec7cd97798bb41405ed377e2cb8a1`.
- Ambiguous-outcome persistence failure test: `a34fcfffba92dd7bcb1f237487c9793c2596dfe8`.
- Latest documentation updates: development log `3fa3121f96bcfc3845507aafecf0e727151d32e1`.
- Latest development-log update: `40c8ab02956da15df4730debe5375bde338c724a`.
- Development log update: `ace2159b6969e75f7a17571e1b9d025829a4a99d`.

## Latest read-only review — 2026-11-06
- Static review completed for the two-phase delivery coordinator, ledger-only persistence helper, Telegram sender, their offline tests, the Pro content validator, dedicated dua/dhikr renderer, and Pro orchestrator.
- No immediate static-code defect was identified in the reviewed delivery safety boundary. This is not runtime validation; unit tests remain NOT RUN.
- The validator enforces required metadata and approval flags but cannot independently authenticate Arabic wording, source interpretation, hadith grading, or media reuse rights. Human/source review remains mandatory.
- No reviewed `content/pro` library exists. No delivery workflow exists or is enabled. Telegram delivery remains disabled.
- Development log scope title corrected to Islamic Dua & Adhkar Pro. Latest documentation commit: `3868b4d0c506de978c59c62aa7e6bb7440095e27`.
- No workflow dispatch, rendering, Telegram request, TikTok publishing, production change, or secret/Cron change occurred.

## Safety and change control
- All Pro implementation commits only on `feature/quran-video-pro`.
- Do not touch production Quran logic, production workflow, Cron, secrets, or delivery route.
- Do not run Actions, render, send Telegram, or publish to TikTok without explicit approval.
- Record every implementation commit and validation result in `PRO_DEVELOPMENT_LOG.md`.



## Pro content intake gate — 2026-11-06
- Added `content/pro/README.md` (commit `d0f2215287c106928dd2c9aedd11cba6f8d8c1b5`) documenting the source-by-source human review requirements for future dua/dhikr manifests.
- This adds process documentation only. It does not add or approve any religious content.
- Quran-oriented files elsewhere in `content/` are not Pro dua/dhikr manifests and must not be selected by the Pro engine.
- No reviewed Pro production manifest exists yet. Content intake remains blocked until exact Arabic, named primary source, precise reference, classification, verification, human review, hadith grading where applicable, media rights, and duration are checked.
- Tests remain NOT RUN. The manual-only safety workflow remains undispatched. No delivery workflow, render, Telegram request, or TikTok publish has been started.
- Latest development log update: `1fcd1385fb16bd0ef3a3197b68b8678523778dd0`.


## 2026-11-06 — Offline Pro safety suite executed successfully

This section supersedes earlier historical statements in this file that the current offline suite had not yet run.

- User approved running the offline-only safety suite.
- The manual workflow was registered on the repository default branch so GitHub would expose the workflow_dispatch entry, while the workflow itself checks out and tests only `feature/quran-video-pro`.
- Registration commit on `feature/telegram-review-notifications`: `5b10d89407e2399c219271bb03f6db6f142c6969`. This was the only change on that branch for this setup; no production code, production workflow, Cron, secrets, or sender route was changed.
- Workflow run: `42259731118`; result: `completed / success`.
- Job `Pro-only offline safety tests` completed successfully. The branch guard, exact Pro checkout, Python setup, and combined test step all reported success.
- The combined test step ran all four suites: `test_pro_delivery_ledger.py`, `test_send_pro_telegram.py`, `test_persist_pro_ledger.py`, and `test_pro_delivery_cycle.py`.
- Run URL: https://github.com/samiouess-ux/IslamicTikTokAutomation/actions/runs/42259731118
- This was offline validation only. No MP4 render, Telegram API request, content delivery, or TikTok publishing occurred.
- Content status remains unchanged: `content/pro` contains only its README; no reviewed dua/dhikr manifest exists. Delivery workflow and schedule remain absent; Telegram delivery remains disabled.

## Next safe work
1. Review trusted primary-source candidates and define a source-by-source content review record; do not mark content verified without human/source verification.
2. Add only reviewed, individually approved dua/dhikr manifests to `content/pro`.
3. Keep delivery workflow integration blocked until reviewed content exists and cross-run ledger persistence is implemented and reviewed.


## 2026-11-06 — Content-source research started
- Recorded the user's instruction to continue and keep progress durable on the Pro branch.
- Reviewed source candidates for the future dua/dhikr library.
- Primary-source starting points selected:
  - Qur'anic supplications: Quran.com verse text and reference, using the official Quran Foundation developer/API documentation as the integration reference.
  - Prophetic supplications and adhkar: the exact narration in its named hadith collection, using Sunnah.com as a searchable reader of the listed primary collections.
- Sunnah.com explicitly cautions that it is a research resource rather than a fatwa site; its About page also explains that numbering can differ between Arabic and English editions and that grade metadata coverage is not uniform. Therefore every candidate must store collection, book/chapter where available, displayed reference scheme, exact Arabic, narrator, and grading authority/status as separate fields; no grade may be inferred from a search snippet.
- Secondary dua compilations and third-party APIs are discovery aids only, not approval sources. Each wording must be opened in the underlying Qur'an verse or hadith narration and checked there.
- No individual dua or dhikr has been selected, verified, or approved yet. No manifest was created and no religious text was added.
- No code, workflow, renderer, Telegram, production branch, Cron, secret, or publishing setting was changed during this research step.
- Next: define a machine-readable review record/schema, then review candidate items one by one against the exact primary source and grading evidence before any manifest can be approved.


## 2026-11-06 — Per-item content review template added
- Added `content/pro/REVIEW_TEMPLATE.md` to capture exact source text, stable URL/reference, numbering scheme, narrator, grading authority, context, human review, separate media-rights review, and production readiness.
- The template is explicitly a worksheet, not a production manifest. It cannot be selected by the renderer and does not mark any religious content verified or approved.
- Commit: `372351501a60139963091b43a1d044ca6fe8277e`.
- No actual dua/dhikr wording or manifest was added. No tests, render, Telegram request, or publishing action occurred.


## 2026-11-06 — First Qur'anic dua candidate identified (not approved)
- Candidate reference: Qur'an, Surah Al-Baqarah 2:201.
- Primary source page opened: https://quran.com/2/201 . The page displays the Arabic verse, reference 2:201, and surrounding context.
- Candidate status remains `candidate` only. This source lookup does not itself constitute the project's separate human-review approval, and no production manifest was created.
- Any future use must copy the complete Arabic verse exactly from the primary source, preserve its full verse reference, and receive human text/context review using `content/pro/REVIEW_TEMPLATE.md`.
- No audio/background rights were reviewed; no render or delivery is authorized.


## 2026-11-06 — Initial dua/dhikr source comparison recorded
- Added `content/pro/CANDIDATE_RESEARCH_001.md` (commit `a5a8c7c138371b6a44e19a224aff96963f64192a`).
- Candidate QD-001: Qur'an 2:201 checked against the opened Quran.com verse page, including exact reference and adjacent context. It remains pending human exact-text/context review.
- Candidate PD-001: morning/evening supplication of Abu Hurairah compared across Sunan Abi Dawud 5068, Jami' at-Tirmidhi 3391, and Riyad as-Salihin 1453.
- Important finding: the source collections show distinct Arabic variants, especially the morning/evening wording and endings. The candidate note records them separately and explicitly prohibits merging variants.
- Tirmidhi's page records Abu 'Isa's grading as hasan; Abu Dawud's Sunnah.com listing displays Al-Albani's sahih grading. These are recorded as separate source-specific grading statements, not as one consensus grade.
- Both candidates remain unapproved. No production manifest or religious content library entry was created. Media rights have not been reviewed.
- No tests, render, Telegram request, or TikTok publishing occurred.


## 2026-11-06 — Grading metadata clarification
- Re-opened the primary candidate pages directly. Tirmidhi 3391 contains Abu 'Isa's in-text statement `hadith hasan`, while the page's separate Grade metadata field displays `Sahih (Darussalam)`. These must remain distinct attributions; the initial note was incomplete on this distinction.
- Updated `content/pro/CANDIDATE_RESEARCH_001.md` with the correction and additional exact wording detail for Riyad as-Salihin 1453.
- No candidate is human-approved; no production manifest, render, or Telegram delivery created.


## 2026-11-06 — Additional candidate located
- Added PD-002, Sayyid al-Istighfar, sourced to Sahih al-Bukhari 6306 and attributed on the page to Shaddad bin Aws.
- Source displays Arabic matn, narrator, exact collection reference, and day/night recitation context. It remains a research candidate pending human review, duration feasibility under 40 seconds, and media-rights review.
- No production manifest or render/delivery was created.


## 2026-11-06 — Media-rights policy baseline and review timing
- Added `content/pro/MEDIA_RIGHTS_POLICY.md`. Pexels/Pixabay are discovery sources only; each exact background asset still needs a per-item rights record. Audio recordings require explicit recording-specific permission/license covering edits, video synchronization, social posting, and possible monetization; no recording is pre-approved.
- User decision: the user will personally inspect and validate Arabic text when the Pro preview videos arrive in Telegram and report corrections/approval. Text review is therefore a Telegram preview-stage human gate, not a claim that candidates are already approved. Keep candidate texts clearly marked unapproved until that review.
- No music. No render or Telegram delivery yet; the delivery workflow remains unwired.


## 2026-11-06 — Telegram preview review gate architecture finding
- Code inspection found a workflow mismatch with the user's explicit review preference: user wants to inspect Arabic wording on the private Telegram preview and then report corrections/approval, but `src/validate_content_manifest.py` currently requires `human_reviewed: true` before any dua/dhikr manifest can render. This blocks the intended first preview.
- Safe design required: distinguish `candidate_preview` from `production_approved`. A candidate may render and be sent only to the owner's private review Telegram destination with explicit preview-only metadata; it must never be treated as publish-ready, enter normal rotation as approved content, or trigger TikTok publishing. User approval/corrections must be recorded before promotion to production manifest.
- Existing renderer and orchestrator currently do not implement this two-stage content state. No code changed in this step; do not render or send until the gate is implemented and tested.
- Current Pro sender/ledger remain review-only but that alone does not resolve the content-manifest preflight mismatch.


## 2026-11-06 — Duration regression test corrected
- Fixed a stale renderer test that still expected a 60-second target and 65-second hard cap. The current Pro renderer's actual policy is a strict 40-second target and 40-second hard maximum.
- The regression now asserts both constants are 40 seconds and verifies that a 41-second item is rejected.
- This is a test correction only; no renderer behavior changed. The manual offline safety workflow has not yet been rerun for this commit.
- Preview-only lifecycle implementation remains the next code task; no rendering or Telegram delivery occurred.


## 2026-11-06 — Candidate preview lifecycle implemented (local render only)
- Added an explicit validator opt-in `allow_candidate_preview=True`. Candidate previews must declare `lifecycle_status: candidate_preview` and `preview_only: true`; pending human review is allowed only on this narrow path. Existing production validation remains strict.
- Added `build_preview_plan()` to accept one explicitly named candidate without rotation selection. It rejects rotation-approved candidates, requires source/metadata/media gates, explicit positive timings, stable IDs, and the 40-second hard cap.
- Added renderer flag `--preview-only`. A candidate manifest cannot use the normal renderer path; the preview flag itself cannot be used with a production manifest.
- Added orchestrator options `--preview-manifest` and `--render-preview`. The local output is isolated under `output/pro_preview` with a `PREVIEW-ONLY-` filename. It does not update rotation history, invoke Telegram, or publish to TikTok.
- Added validator, orchestrator, and renderer regression tests for preview/production separation.
- This implements local preview validation/rendering only. It does NOT yet deliver a preview to Telegram; a separately gated private-review sender and workflow still need implementation and tests. No render or Telegram request was performed.
- Tests have not been executed after these code changes; the previous manual offline workflow success predates them.


## 2026-11-06 — Candidate preview lifecycle implemented (local render only)
- Added an explicit validator opt-in for candidate previews. A candidate must declare lifecycle_status=candidate_preview and preview_only=true; pending human review is allowed only on this narrow path. Normal production validation remains strict.
- Added an explicit single-manifest preview preflight. It bypasses rotation selection but rejects rotation-approved candidates and retains source, metadata, media, timing, stable-ID, and 40-second checks.
- Added renderer flag --preview-only. Candidate manifests cannot use the normal renderer path, and production manifests cannot use the preview flag.
- Added orchestrator options --preview-manifest and --render-preview. Local output is isolated under output/pro_preview. It does not update rotation history, invoke Telegram, or publish to TikTok.
- Added regression tests for validator, orchestrator, and renderer preview/production separation.
- This is local preview capability only; private Telegram preview delivery still requires a separate sender/workflow and tests. No render or Telegram request occurred.
- Tests have not been executed after these changes; the previous manual offline workflow success predates them.


## 2026-11-06 — Offline test workflow expanded for preview lifecycle
- Static review found that the manual Pro safety workflow still ran only the original ledger/sender/persistence/delivery-cycle suites; it omitted the newly added validator, orchestrator, and renderer tests.
- Updated `.github/workflows/pro-safety-tests-manual.yml` on `feature/quran-video-pro` to run all seven Pro offline test modules, including the candidate-preview lifecycle regressions.
- Verified the saved workflow content on the exact Pro branch: exact branch guard retained, `contents: read` only, no Telegram secrets, no rendering command, and no publishing/delivery step.
- Commit: `56476b87d25c7da651f51819cad64cb983179bbe`.
- The workflow has NOT been dispatched and tests have NOT run. The available GitHub actions in this session do not expose a workflow-dispatch operation; only a rerun operation for an existing job is available. Do not report tests as passed.
- No render, Telegram API request, TikTok publish, production workflow run, or changes to `main` / `feature/telegram-review-notifications` occurred.
- Next: obtain a supported manual dispatch path and verify all seven suites. Only after tests pass, continue with a separate private Telegram preview sender; keep actual send disabled until the user authorizes a specific preview.


## Latest implementation — 2026-11-06
- Added isolated candidate-preview Telegram sender and offline safety tests. Explicit CLI confirmation and separate Pro preview bot/chat environment variables are required; only `PREVIEW-ONLY-*.mp4` is accepted.
- Preview caption explicitly says it is not approved for posting. Sender has no automatic retry and does not touch the production ledger, rotation history, or TikTok publishing.
- Manual offline workflow now includes eight focused test modules.
- Commits: sender `80e290cf2d77edb172d6794bdb0f2c38cf60d5bd`; tests `4997fe46c0695f1eb2144c0d2f1d5c4f6a04a07a`; workflow `06fda285fd198382c6cd3df4ee018eea66bfb034`.
- Tests NOT RUN; workflow NOT DISPATCHED. No render, Telegram request, secret change, TikTok publish, or production-branch change.
- Next: static review and obtain a supported manual dispatch route for the offline suite. Do not send a real preview until the user authorizes that specific send.


## 2026-11-06 — Preview sender hardening and current status
- Added an isolated candidate-only Telegram preview sender in `src/send_pro_preview_telegram.py`. It requires explicit `--confirm-preview-send`, separate `PRO_PREVIEW_TG_BOT_TOKEN` and `PRO_PREVIEW_TELEGRAM_CHAT_ID` values, a positive numeric private chat ID, and a preview-prefixed MP4.
- Sender validates the candidate manifest through the explicit preview-only validator; caption begins `PREVIEW — NOT APPROVED FOR POSTING`. It makes one request only, does not retry ambiguous outcomes, and has no import/use of the production delivery ledger or rotation history.
- Hardened preview output identity: candidate manifest IDs must be safe 1–80 character filename components, and the sender requires the exact filename `PREVIEW-ONLY-{content_type}-{manifest_id}.mp4`. This prevents path traversal and prevents a different preview MP4 from being paired with a candidate manifest.
- Added offline regression tests for sender confirmation, destination/file restrictions, exact manifest/file binding, caption warning, single request/no retry, and safe output IDs.
- Expanded manual offline workflow to eight test modules. Static re-fetch verified exact Pro branch guard, read-only contents permission, inclusion of the new sender tests, and absence of secrets or delivery/render/publish steps (the renderer test module is a unit-test invocation only).
- Commits: preview sender `80e290cf2d77edb172d6794bdb0f2c38cf60d5bd`; sender tests `4997fe46c0695f1eb2144c0d2f1d5c4f6a04a07a`; workflow `06fda285fd198382c6cd3df4ee018eea66bfb034`; safe ID guard `9a8577fae641c5fa64369293594bf9dc3d0cc6e5`; exact MP4/manifest binding `a687af0cef089dc2265570061f64c5bc6c11bd3f`; orchestrator test `25ee33f4272aee847187a3550c6b9d19cffb8d5f`; sender binding test `141a630af57a840abe49e99897f6e3c8e6182042`.
- Current verification is static re-fetch only. The offline tests have NOT been executed and the workflow has NOT been dispatched. No render, Telegram API request, token/chat secret addition, TikTok publish, or production-branch change occurred.
- Next: use a supported manual workflow-dispatch path to run the offline suites. Only after tests pass, prepare a specific candidate manifest and rights-cleared assets. Do not send a real preview until the user explicitly authorizes that exact send.


## 2026-11-06 — Latest read-only safety review and status clarification
- Reviewed the eight-suite manual workflow and the current tests for the preview Telegram sender, two-phase delivery cycle, and ledger persistence helper on `feature/quran-video-pro`.
- Preview-sender tests cover explicit confirmation before network access, candidate-only lifecycle, rotation rejection, preview filename and exact manifest binding, positive numeric destination restriction, warning caption, one-request behavior, and no automatic retry.
- Delivery-cycle tests cover failure/no-op of the first persistence step blocking the sender, ambiguous outcomes becoming uncertain, failure to persist uncertainty, persist → send → persist ordering, final persistence failure, and ledger-path isolation.
- Ledger persistence tests cover wrong-branch refusal, pre-existing/unrelated staged changes, ledger-only commit/push, and push failure not being reported as success.
- Static review only: these tests were inspected, NOT executed. The expanded eight-suite workflow remains NOT DISPATCHED. The earlier run `42259731118` passed only the four then-included suites; it does not validate the later preview lifecycle or preview sender tests.
- Documentation clarification: historical “tests not run” statements refer to the later expanded suite at that time. The four-suite success above is a separate earlier result. Current expanded-suite result remains NOT RUN.
- No immediate issue was established by this static review. One small hardening item remains worth considering later: the preview sender treats a positive numeric chat ID as its private-destination guard; tests verify this restriction but do not independently query Telegram's `chat.type`. This is a review suggestion, not a confirmed defect.
- No code, workflow, secrets, Cron, render, Telegram request, TikTok publish, or production/main branch was changed or invoked during this review. Original Quran engine remains out of scope and untouched.
- Next: continue read-only review of content/media gates and workflow integration boundaries. Keep all execution and delivery disabled unless separately authorized.


## 2026-11-06 — Read-only renderer and production-path review
- Re-fetched the current Pro renderer, validator, orchestrator, and media-rights policy from `feature/quran-video-pro`; this was a static review only.
- Confirmed background URL binding gap: validator checks approval flags on `visual.background_candidate`, but renderer prefers `visual.approved_background_url` without requiring it to equal the approved candidate's `direct_video_url`. A different HTTPS URL could therefore be fetched.
- Confirmed production output-ID validation gap: preview planning enforces a safe filename-component pattern, while normal `build_plan()` checks only that the manifest ID is a non-empty string. Production render output interpolates that ID into a path without applying the preview's safe-ID rule. Add the same strict ID validation before production rendering and a regression test.
- Confirmed audio timing limitation: per-item durations control overlay screen changes, while audio is validated only against total video duration; code explicitly states it is not synchronized per item. This is a correctness risk for multi-item videos, not proof that a particular output is wrong. Define and test a per-item audio/timing model before approving multi-item rendering.
- The media-rights policy requires per-asset provenance (asset ID/page, creator, license evidence, download date, intended use, third-party review), but the current manifest validator only checks background approval booleans and source/direct URLs. The validator therefore does not enforce the full policy record. Keep media approval blocked until the schema and validator enforce those fields.
- These are code-path findings, not fixes. No code or workflow was changed. No test suite was run or dispatched, no render or Telegram request occurred, and no TikTok publication occurred.
- Current expanded eight-suite workflow remains NOT RUN. Historical run `42259731118` covers only the earlier four suites.
- Next: close the four validation gaps with focused negative tests, then review candidate manifest/asset records. Obtain separate approval before any code change, test dispatch, render, or Telegram send. Original Quran production engine remains untouched.


## 2026-11-06 — Read-only regression-test coverage review
- Re-fetched `tests/test_render_dua_video.py` (blob `6b0e01359d667682bd1f11ff317607518a07fa41`) and `tests/test_pro_orchestrator.py` from `feature/quran-video-pro`; inspected them alongside the current renderer, validator, and orchestrator.
- Audio: existing tests cover total-file duration mismatch/fail-closed behavior and explicitly assert the renderer's documented limitation. They do not prove per-item audio-to-screen synchronization or a safe multi-item audio mapping.
- Background: no regression test was found that supplies a different `visual.approved_background_url` from `visual.background_candidate.direct_video_url` and expects rejection. The previously identified binding gap remains untested.
- Output identity: the orchestrator tests reject an unsafe ID on the candidate-preview path, but do not exercise an unsafe ID through normal production `build_plan()` / `render_plan()`. The production-path ID validation gap remains untested.
- Media rights: the inspected tests do not require the complete per-asset provenance record described by `content/pro/MEDIA_RIGHTS_POLICY.md`; current validation tests focus on metadata/approval flags. Full rights-evidence enforcement remains unproven.
- These are coverage gaps corresponding to the previously documented implementation gaps; they are not evidence that a specific rendered video was incorrect or that an asset was actually used without permission.
- Validation boundary: source/test inspection only. No tests executed, no workflow dispatched, no code or workflow changed, no render, Telegram request, or TikTok publication. No secrets, Cron, or delivery settings changed. All work stayed on `feature/quran-video-pro`; `main` and `feature/telegram-review-notifications` were not touched. The original Quran production engine remains untouched.
- Next: prepare focused negative/integration test cases for production IDs, approved-background URL binding, per-item audio timing, and required media-rights evidence. Implementation and test execution remain gated by separate explicit approval.

## 2026-11-06 — Delivery preflight boundary review
- Re-inspected the current Pro delivery cycle, Telegram sender, ledger tests, persistence tests, and manual safety workflow.
- Confirmed local validation (secrets/configuration, MP4 existence/size, caption parsing/flags, manifest identity/type) occurs in the sender before the Telegram network-request exception boundary, but after the cycle has reserved and persisted the manifest.
- If such local validation fails, the cycle attempts to persist the unchanged ledger; the reservation generally remains reserved, not uncertain, and blocks reuse despite no Telegram request having started. Actual request/response exceptions are separately transitioned to uncertain by the sender.
- Recommended follow-up: preflight before reservation or a typed, provably pre-network failure path, plus tests for invalid local inputs and preserved uncertain handling for transport ambiguity. No implementation change was made.
- The manual safety workflow remains manual-only, exact-Pro-branch guarded, and contents: read; its eight suites remain NOT RUN. Historical run 42259731118 covers only the earlier four suites.
- Static review only. No test, dispatch, render, Telegram request, TikTok publish, secrets/Cron change, or production-branch modification occurred. Original Quran production engine remains untouched.
- Next: continue read-only review of delivery-cycle call sites and preview/private-destination isolation; implementation and execution require separate explicit approval.

## 2026-11-06 — Telegram bot reuse checkpoint
- Existing bot reuse is feasible in design: original workflow uses repository secrets `TG_BOT_TOKEN` and `TELEGRAM_CHAT_ID`; Pro preview sender expects `PRO_PREVIEW_TG_BOT_TOKEN` and `PRO_PREVIEW_TELEGRAM_CHAT_ID`.
- Proposed future Pro-only workflow maps the existing secret names into the Pro sender's environment variables. No second bot and no original-workflow/secrets change are required by this design.
- This is **not implemented or tested**. Secret values were not inspected. No workflow was created/dispatched, no render or Telegram send occurred.
- Next: continue read-only integration review. Any Pro workflow creation, dispatch, render, and preview send require their own explicit approval. Original Quran engine and production branch remain untouched.


## 2026-11-06 — Pro Telegram integration safety gates (read-only)
- Future Pro integration must be a manual-only workflow on the exact Pro branch, with branch guard before exposing the existing Telegram secrets.
- Existing secret mapping remains a proposal; values are not visible or verified. Pro sender requires explicit `--confirm-preview-send`, candidate-only manifest, exact preview MP4/manifest filename match, and does not auto-retry.
- Separate approval gates: preparing/rendering a candidate does not authorize Telegram delivery. No failure-notification Telegram path is allowed to bypass the send gate.
- Constrain all manifest/output paths to Pro preview locations; avoid arbitrary shell/path inputs. Numeric chat-ID validation alone does not independently prove Telegram chat type.
- Review only. No workflow/code/test/dispatch/render/send/secret changes. Original Quran production engine remains untouched.


## 2026-11-06 — Latest read-only preview and workflow-isolation review
- Confirmed statically that the preview sender test fixture omits the top-level `source` object required by `validate_content_manifest.py`. Four tests are likely to stop at validation before reaching their intended caption, exact-name, successful-send, and transport-timeout assertions. This is static inference only; tests were NOT run. Correct the fixture, not the validator.
- Confirmed the eight-suite manual safety workflow includes the preview sender suite, exact Pro branch guard, Pro checkout, `contents: read`, and no render/send step. It remains undispatched.
- Identified two legacy Quran render workflows in the Pro branch that lack an exact branch guard: `.github/workflows/render-first-video.yml` has manual dispatch plus a push-path trigger without branch filtering; `.github/workflows/render-manifest-video.yml` has manual dispatch and checks out the triggering ref by default. Both can enter Quran rendering paths if invoked from Pro and should be branch-isolated before any Pro Actions activity. Neither was run.
- The original `telegram-quran-request.yml` remains scoped to `feature/telegram-review-notifications`; it was not changed.
- Recommended sequence: isolate legacy Quran workflows on Pro; fix preview fixture; add Pro-only preview-send idempotency with uncertain outcomes blocked; then add a separate manual Pro preview workflow using existing Telegram secrets via environment mapping. No implementation has been performed.
- No code/workflow/secrets/Cron/bot configuration changed. No tests, dispatch, render, Telegram send, or TikTok publish occurred. Original Quran engine and production Telegram route remain untouched.
- Current test status: expanded eight-suite workflow NOT RUN / NOT DISPATCHED. All findings are static and require approved follow-up before implementation.


## 2026-11-06 — Workflow inventory and original-engine protection
- Static review on `feature/quran-video-pro` identified legacy Quran workflows that must not be manually dispatched from Pro. Highest risk: `build-quran-audio-inventory.yml` (manual trigger without exact branch guard, `contents: write`, production-state commit/rebase/push to `feature/telegram-review-notifications`, and Telegram send using original secrets; even `test_only=true` does not skip Telegram send). Also high risk: `render-manifest-video.yml` (unguarded manual render path with original Telegram delivery path).
- Other legacy Quran render/preparation/test workflows without exact Pro guards are classified for isolation before any Pro Actions activity. `render-second-ash-sharh-review.yml` currently has its Telegram send step disabled, but still can render Quran content.
- Binding safety rule: do not modify, disable, dispatch, or reconfigure `feature/telegram-review-notifications`, its active Telegram workflow, bot secrets, or schedule. Its daily videos are intended to continue on their existing unchanged path. Only future Pro-branch-local isolation work may be considered, with explicit approval; it must not change the production branch or delivery configuration.
- The Pro reuse of the existing Telegram bot is still only a design proposal, not an active integration. No secret values were read/changed and no Telegram send occurred.
- This checkpoint was documentation/static inspection only: no code/workflow edits, tests, Actions dispatch, render, Telegram request, TikTok publication, Cron changes, or production-branch changes. Eight-suite Pro safety workflow remains NOT RUN.
- Next: finish workflow inventory and prepare a reviewable Pro-only isolation plan; execution remains separately gated.


## 2026-11-06 — Workflow inventory checkpoint
- Branch reviewed: `feature/quran-video-pro` only.
- Additional static classifications: media extraction/preparation workflows are read-only and artifact-producing, without Telegram or Git push steps; archive inspection/connectivity workflows are read-only network checks; `cloud-runner-check.yml` is an environment check; `official-audio-preflight-tests.yml` checks out a separate repair branch; `review-background-candidates.yml` checks out the original production branch and must not be run from Pro.
- Manual dispatch without exact Pro guard remains a reason not to run legacy workflows from Pro, even where no write/send side effect was found.
- Previously recorded high-risk workflows remain blocked: especially `build-quran-audio-inventory.yml` (production branch push + original Telegram send) and legacy Quran render workflows.
- Pro/original Telegram integration remains design-only. Existing production bot/workflow/secrets/Cron have not been changed. No tests, dispatch, render, Telegram send, or TikTok publish occurred.
- Current next step: consolidate the workflow allow/deny matrix, then seek explicit approval before any Pro-only workflow edits. The production Quran engine remains untouched.


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


## 2026-11-06 — Preview sender idempotency review
- Static re-fetch confirms explicit confirmation and no automatic retry, but no durable preview-send idempotency record exists. Re-running the same preview command could send the same candidate again; no duplicate send is known to have occurred.
- Required before delivery: a Pro-only durable reservation/receipt ledger keyed to candidate and immutable artifact identity; persist reservation before network access; delivered only with valid Telegram message ID; ambiguous outcomes stay blocked for human resolution. Keep it separate from production rotation and original Quran state.
- Review only: no code/workflow/test/dispatch/render/Telegram/secret/Cron changes. Eight-suite workflow remains NOT RUN. Original production engine and delivery route untouched.

- Design detail: keep preview idempotency in a separate Pro preview ledger rather than assuming the existing delivery ledger is sufficient. Bind each send to candidate ID plus manifest and MP4 SHA-256 hashes, persist across workflow runs, and serialize with one fixed Actions concurrency group. Existing local file locking alone is not cross-run protection.


## 2026-11-06 — Preview idempotency test/concurrency requirements
- A future preview-send workflow needs its own fixed concurrency group (`cancel-in-progress: false`); the current concurrency group only serializes the manual test workflow.
- Ledger unique key must be candidate ID, with manifest/video SHA-256 stored and compared as immutable attributes. Same candidate ID with changed hashes must fail closed; do not key only by candidate+hash.
- Test matrix required: duplicate candidate; changed manifest/video hashes; success terminal state; timeout/connection loss/invalid response uncertain state; preflight failures before reservation; pre-send persistence failure means no request; post-send persistence failure leaves remote reservation blocking; concurrent attempts allow only one reservation.
- Static review only. No code/workflow/test/dispatch/render/Telegram/secret/Cron changes. Original production engine untouched; expanded eight-suite workflow NOT RUN.


## 2026-11-06 — Telegram integration review checkpoint
- Original Quran request workflow remains pinned to `feature/telegram-review-notifications`; unchanged.
- Pro preview sender expects `PRO_PREVIEW_TG_BOT_TOKEN` and `PRO_PREVIEW_TELEGRAM_CHAT_ID`; original workflow uses `TG_BOT_TOKEN` and `TELEGRAM_CHAT_ID`. Mapping the existing secrets into a future Pro-only workflow is a design proposal only; values were not read and availability was not verified.
- No Pro delivery workflow is enabled. Private destination type is not independently verified by the sender; its positive numeric chat-ID check is only a guard, not proof of Telegram `chat.type`.
- No code, workflow, tests, dispatch, render, Telegram request, TikTok publish, secrets, Cron, original bot configuration, or production branch changed in this review. Expanded eight-suite Pro safety workflow remains NOT RUN.
- Next: complete the fail-closed integration design and destination verification requirements before any implementation. Original Quran engine remains untouched.


## 2026-11-06 — Preview ledger persistence checkpoint
- Existing ledger persistence writes only the existing delivery ledger and pushes only to the exact Pro branch; it requires `contents: write`. Existing file locking is local to one runner and does not prevent two separate GitHub runners from racing.
- A future preview workflow therefore needs a separate preview ledger, one fixed concurrency group (`cancel-in-progress: false`), exact Pro-ref guard before secrets/write permission, and a hard stop on persistence push failure before Telegram.
- Preview identity must bind a unique candidate ID to immutable manifest/video SHA-256 hashes. Persist `reserved` before send; mark `delivered` only with a valid Telegram message ID; keep ambiguous outcomes blocked as `uncertain` until human reconciliation. Complete local preflight before reserving.
- Review/design only: no code, workflow, test, dispatch, render, Telegram request, TikTok publish, secret, Cron, bot setting, or production-branch change. Original Quran engine untouched; eight-suite safety workflow NOT RUN.


## 2026-11-06 — Preview ledger contract
- A separate `data/pro_preview_send_ledger.json` is required; do not reuse `data/pro_delivery_ledger.json` or production rotation history.
- Version 1 entries are keyed by immutable candidate ID and store content type, manifest SHA-256, MP4 SHA-256, workflow run ID, state, timestamps, and Telegram message ID only after confirmed delivery.
- Existing candidate ID always blocks a second send. Changed hashes under the same ID are an identity conflict; create a new reviewed candidate ID instead.
- Preflight all local inputs before reservation. Persist and verify `reserved` on the exact Pro branch before Telegram; send once; mark `delivered` only with a valid positive message ID. Ambiguous network/response outcomes become `uncertain`; failed final persistence leaves the earlier reservation blocking. No automatic retry or expiry.
- Allowed transitions: reserved to delivered/uncertain; uncertain to delivered only with recovered receipt. Human confirmation and evidence are required before releasing an uncertain/not-delivered candidate.
- Serialize the manual Pro workflow with fixed concurrency and no cancellation; fetch latest ledger before changes; stop on push conflict (never force-push). Grant write permission and expose existing bot secrets only after exact Pro-ref guard.
- Design/documentation only: no code, workflow, tests, dispatch, render, Telegram, TikTok, secret, Cron, bot setting, or production branch changes. Original Quran engine untouched; eight-suite workflow NOT RUN.


## 2026-11-06 — Pro preview workflow boundary
- No preview-delivery workflow is active or present in the reviewed workflow inventory.
- Future workflow must be manual `workflow_dispatch` only, exact job-level ref guard for `feature/quran-video-pro`, and explicit checkout of that branch. No schedule/push/PR/workflow_run triggers or pull_request_target.
- Keep Telegram secrets out of global env; expose existing `TG_BOT_TOKEN` and `TELEGRAM_CHAT_ID` only to the final one-shot send step after validation and verified persisted reservation. Do not print or store secret values.
- Use least privilege: read-only by default; `contents: write` only in the guarded ledger-persistence job. No unrelated write scopes.
- Accept only fixed Pro candidate/output paths; reject traversal/symlinks and require exact PREVIEW-ONLY filename-to-manifest identity. Serialize all sends in one fixed concurrency group with `cancel-in-progress: false`; fetch latest ledger and stop on push conflict.
- Validate/preflight, reserve and push ledger, verify remote reservation, send once, persist delivered/uncertain. No retry. Offline tests must remain separate and receive no secrets/write permission. No TikTok publishing step or credentials.
- Design only: no workflow/code/test/dispatch/render/Telegram/TikTok/secret/Cron/bot-setting/production changes. Original Quran engine untouched; eight-suite safety workflow NOT RUN.


## 2026-11-06 — Preview ledger implementation/test checklist (not implemented)
- Planned order: standalone versioned preview ledger → strict schema/identity/state validation → atomic persistence + local lock → exact-Pro persistence wrapper → offline tests → manual-only guarded workflow → preflight/reserve/verify/send-once/finalize orchestration.
- Ledger identity: unique candidate ID bound to manifest and MP4 SHA-256; an existing ID always blocks another send, and changed hashes under the same ID are a conflict. Do not reuse production delivery ledger or rotation history.
- Validation must reject malformed/unknown schema, unsupported states/types, invalid SHA-256, mismatched IDs, unsafe paths/symlinks, wrong PREVIEW-ONLY filename, invalid/oversized/missing MP4, invalid caption/config, and invalid Telegram message IDs (including bool).
- State machine: reserved→delivered/uncertain; uncertain→delivered only with recovered receipt. No automatic retry, expiry, deletion, or release. If final persistence fails, the remote reservation remains a duplicate-send block.
- Persistence must check exact Pro branch, commit only the preview-ledger file, reject unrelated staged changes, verify remote reservation, and stop on push conflict; never force-push.
- Offline tests must mock filesystem, Git and Telegram. Cover schema/identity, atomicity, locking/concurrent attempts, state transitions, all preflight failures, persistence-before-send ordering, exactly-one-send/no-retry, uncertain outcomes, final-persist failure, and workflow static security guards.
- Workflow checks: workflow_dispatch only; exact Pro ref guard; pinned Pro checkout; one fixed concurrency group with cancel-in-progress false; least permissions; secrets only in final send step; no secret logging; no TikTok; no production sender/workflow.
- Tests must assert no live network, Telegram, GitHub writes, render, secrets, or TikTok calls. Existing eight-suite Pro safety workflow remains NOT RUN.
- Status: checklist/matrix documented only. No implementation, test run, dispatch, render, Telegram, TikTok, secret/Cron/bot change, or production/original engine change. Next: map checklist to exact source/test files, then seek explicit approval before implementation.

## 2026-11-06 — Current-file mapping for future preview implementation
- Reusable test patterns: `tests/test_send_pro_preview_telegram.py` (temporary files + mocked `urlopen`), `tests/test_pro_delivery_ledger.py` (state and bool/int validation), `tests/test_persist_pro_ledger.py` (mocked Git subprocess and exact staged-path checks), and `tests/test_pro_delivery_cycle.py` (injected persistence/sender and ordering assertions).
- Existing modules are not to be reused unchanged for preview state: `src/pro_delivery_ledger.py`, `src/persist_pro_ledger.py`, and `src/pro_delivery_cycle.py` are wired to the production delivery ledger/path. Keep preview state isolated.
- Proposed new modules: `src/pro_preview_send_ledger.py`, `src/persist_pro_preview_ledger.py`, and `src/pro_preview_delivery_cycle.py`; proposed focused tests: corresponding `tests/test_pro_preview_send_ledger.py`, `tests/test_persist_pro_preview_ledger.py`, `tests/test_pro_preview_delivery_cycle.py`, plus a workflow static-security test if it can avoid adding unverified dependencies.
- Current preview sender tests do not cover durable idempotency, hash identity, or cross-run concurrency. Existing production ledger/persistence/cycle tests provide patterns but do not prove preview-specific behavior.
- The existing safety workflow has its own test-only concurrency group; it must remain separate from a future single fixed concurrency group for preview sends. Do not add send permissions/secrets to the safety workflow.
- This is a static file/test mapping only. No implementation or tests were run; eight-suite workflow remains NOT RUN. No render/Telegram/TikTok/secret/Cron/original-bot/production-engine changes occurred.


## 2026-11-06 — Isolated preview ledger code added (tests not run)
- Added `src/pro_preview_send_ledger.py` for a separate versioned preview ledger with strict validation, candidate-ID uniqueness, SHA-256 binding, atomic writes, local locking, and explicit transitions. Uncertain recovery requires an explicit recovered-receipt flag.
- Added `src/persist_pro_preview_ledger.py` for exact-Pro-only persistence: fetch/check branch freshness, reject pre-staged or unrelated paths, stage only the preview ledger, normal push, then verify remote HEAD. No force push.
- Added `src/pro_preview_delivery_cycle.py` for fixed-root preflight, candidate lifecycle/filename/size/config validation, manifest/video hashes, reservation persistence before send, reservation verification, artifact re-hash, one injected send attempt, and delivered/uncertain state handling.
- Added focused offline tests: `tests/test_pro_preview_send_ledger.py`, `tests/test_persist_pro_preview_ledger.py`, and `tests/test_pro_preview_delivery_cycle.py`. These are authored but NOT RUN.
- No preview delivery workflow or automatic caller was created. No Telegram request or render was performed. Workflow auth/concurrency and independent private-chat destination verification remain future gates.
- Static implementation only. No change to production ledger/rotation, original Telegram bot/workflow, main or `feature/telegram-review-notifications`, Cron, secrets, TikTok, or original Quran engine. Eight-suite safety workflow remains NOT RUN.
- Next: static review the new code/tests; request separate approval before executing offline tests. Workflow creation and Telegram send need separate approval.


### Static hardening after initial implementation
- Uncertain→delivered now requires explicit recovered-receipt confirmation; plain message ID alone is not sufficient.
- Persistence fetches the exact remote tracking ref before freshness comparison. Preview input/output and ledger paths reject symlink escapes.
- Cycle tests were added for post-reservation artifact mutation and final persistence failure. Tests remain NOT RUN.


### Final static review corrections
- Remote refspec refresh is explicit before and after persistence; persistence test newline fixtures corrected.
- Latest verified code/test blobs: ledger `4165e0b9`, persistence `97cea2e3`, cycle `a96c1b62`; tests `2762f1b3`, `ebc9e66e`, `8cf87814`.
- Activation blockers remain: no workflow/caller; private Telegram chat type not independently verified; a narrow artifact mutation race remains between final hash and sender file read; full per-asset rights evidence is not enforced by the shared validator.
- Tests remain NOT RUN. No Telegram/render/TikTok/secret/Cron/original-engine or production branch operation.


## 2026-11-06 — Preview upload hash binding hardened
- Corrected the mocked Git command sequence in preview persistence tests (not executed).
- Preview sender now reads MP4 and manifest bytes once, checks both against reserved SHA-256 digests, and sends those same bytes. The preview cycle passes the hashes; mismatch is rejected before any Telegram request.
- Added offline test assertions for manifest/video hash mismatch and zero network calls.
- Still blocked from activation: no workflow/caller; Telegram chat type not independently confirmed private; full per-asset media-rights evidence gate not enforced. Tests NOT RUN.


### Next rights gate requirements
- Require a per-asset rights record bound to the exact file SHA-256 and manifest asset reference.
- Visual record: exact asset page/ID, creator, platform, download date, exact license and saved evidence, intended uses, edits, third-party people/logos/artwork/property/privacy review, reviewer and checked date.
- Audio record: exact recording URL, performer and recording owner, platform/download date, explicit permission evidence and scopes for download/edit, video sync, public social posting, monetization if applicable, territory/duration, attribution, reviewer and checked date.
- Missing/unclear evidence fails closed; generic provider license page or boolean approval alone is insufficient. Silent media does not require an audio-file record.
- This is a policy-to-validator design checkpoint only; no individual asset has been approved.


## 2026-11-06 — Preview delivery activation gate review
- Re-fetched and statically reviewed the preview ledger, persistence helper, cycle, Telegram sender, shared content validator, and focused offline tests on `feature/quran-video-pro`.
- Confirmed: unique candidate-ID reservation with manifest/video SHA-256 identity; explicit reserved/delivered/uncertain states; safe IDs and strict message-ID typing; exact-Pro ledger-only persistence; fixed input-root/symlink checks; exact preview filename and size checks; reservation persisted before send; pre-send hash recheck; sender uploads the same in-memory bytes it hashes; no automatic retry.
- Confirmed activation blockers: (1) numeric chat ID does not prove Telegram `chat.type == private`; an independent destination verification gate is absent; (2) shared manifest validator does not enforce complete per-asset license/permission evidence bound to exact asset hashes; (3) no isolated preview delivery workflow/caller exists, so cross-run concurrency and workflow secret/permission boundaries are not yet implemented.
- Required next work: define strict visual/audio rights evidence schema and validator; add an independent private-chat verification step; add focused offline tests for both; only then design/review a manual-only exact-Pro delivery workflow with one fixed concurrency group and least-privilege secrets/permissions.
- Focused tests remain NOT RUN. Existing eight-suite safety workflow remains NOT RUN. No workflow was created/dispatched, no render or Telegram/TikTok action occurred, and no manifest was approved.
- This pass changed documentation only. No code, tests, workflow, secrets, Cron, original bot/workflow, production ledger/rotation, `main`, `feature/telegram-review-notifications`, or original Quran engine was changed.
- Development log review checkpoint: commit `8387ff349485d76667412f5517239c6d7aaf625e`.


## 2026-11-06 — Strict preview activation contracts documented
- `content/pro/MEDIA_RIGHTS_POLICY.md` now specifies a versioned per-asset rights JSON record under `content/pro/rights/`, bound to the exact asset SHA-256 and manifest asset ID.
- Required evidence includes exact asset/recording page, creator/performer, rights owner, platform, download date, exact license/permission evidence, explicit intended-use permissions, territory/time scope, attribution, third-party rights review, human reviewer/date, and approved decision. Audio additionally requires performer/recording-owner distinction and explicit sync/public-posting/commercial scope as applicable. Silent output does not need an audio record.
- Future Pro validator must reject missing/duplicate/orphaned records, path/symlink escapes, hash mismatch, missing/ambiguous/expired permissions, and boolean-only approvals.
- Telegram gate: call Bot API `getChat` immediately before preview upload using the same bot token/chat ID; require API success, exact returned ID match, and `result.type == "private"`. Reject non-private, mismatched, malformed, or error responses before `sendVideo`; never log secrets or unnecessary personal metadata. Official reference: https://core.telegram.org/bots/api#getchat .
- Policy update commit: `4a705b4185cba8f76f08a9c36f1bf2345bb93d03`. Development log update commit: `ceab6a08eca9bd04bfd7c65402aef177f6d51506`.
- Documentation only. Rights validator, getChat code, tests, workflow, rights records, and content manifests are not implemented. Tests remain NOT RUN; no dispatch, render, Telegram, or TikTok action occurred.
- No changes to secrets, Cron, original bot/workflow, production ledger/rotation, `main`, `feature/telegram-review-notifications`, or original Quran engine.
- Next: request explicit approval before implementing these two gates and their offline mocked tests. Keep delivery disabled.


## 2026-11-07 — Media rights and private Telegram destination gates implemented
- Added `src/validate_pro_media_rights.py`: per-asset versioned rights JSON, exact asset references, fixed local media/evidence roots, symlink/traversal rejection, SHA-256 verification, asset-specific HTTPS source page, explicit permission scopes, worldwide territory, active validity, third-party review notes, human reviewer/approval, and separate performer/recording-owner requirements for audio.
- Preview policy requires permission for eventual public social posting and commercial/monetized use in addition to private review. Required attribution remains blocked until renderer/caption attribution support exists. Silent media has no audio asset.
- `src/render_dua_video.py` now uses the exact rights-cleared local background/audio files and no longer downloads the background URL during render.
- `src/pro_preview_delivery_cycle.py` checks rights and verifies Telegram private-chat identity before reservation; sender repeats getChat immediately before upload.
- `src/send_pro_preview_telegram.py` confines direct sender paths to Pro manifest/output roots, rechecks rights, and requires Telegram getChat success + exact chat ID + `type=private`. Non-private, mismatch, malformed, API, or network failures block upload; token-bearing exceptions are redacted. Definite pre-upload failures keep the reservation blocking duplicates without marking the upload uncertain.
- New/updated tests: `tests/test_validate_pro_media_rights.py`, `tests/test_send_pro_preview_telegram.py`, `tests/test_pro_preview_delivery_cycle.py`, `tests/test_render_dua_video.py`. Tests authored but NOT RUN.
- Key source blobs: rights validator `d4515d2417c6d61ae2a81b3524b962083afd2996`; sender `f1f86053dff98097ce7c3e356e1e38966b9841ef`; cycle `c883d1ace52745eb8b7d092a293bdf2f5e149c95`; renderer `16e59b7ba6c760a1d98a9f5d688f5c1cb9d7e3be`.
- Policy update commit: `492f045cbea0793200aae35cb67f0e46220d7fbe`; development log update commit: `58f17b27be8dab36e32931f7a69f2083bf5da10c`.
- No actual media/rights record was approved or created. No preview workflow/caller was created or dispatched; no render, Telegram request, TikTok publish, secret/Cron/bot-setting change occurred.
- No changes to original Telegram bot/workflow, production ledger/rotation, `main`, `feature/telegram-review-notifications`, or original Quran engine. Eight-suite safety workflow and focused offline tests remain NOT RUN.
- Next: static workflow isolation/concurrency/secret-scope review, then final source/test review and a separately authorized offline test run. Telegram send requires separate explicit approval.


### Workflow review checkpoint
- Current Pro branch has 21 workflows and no Pro preview delivery workflow/caller.
- Existing `pro-safety-tests-manual.yml` remains manual-only, exact-Pro guarded, pinned to the Pro branch, `contents: read`, no secrets, no render/send, fixed test-only concurrency with cancellation disabled.
- It includes the updated preview sender and renderer test modules, but not the new `test_validate_pro_media_rights.py` or `test_pro_preview_delivery_cycle.py`. Those two new suites are not wired into the current workflow.
- No workflow changes were made. Adding those two test commands to the existing read-only safety workflow needs separate approval; creating a preview delivery workflow needs separate approval.
- Latest verified sender-test blob SHA is `2a1606744f83d1721d1fbd5c1c24f9cacbae7a1f`.
- Focused tests and eight-suite workflow remain NOT RUN. No dispatch, render, Telegram/TikTok, secrets/Cron/bot-setting change. Original Telegram and Quran production routes remain untouched.


## 2026-11-07 — Safety workflow dependency fix
- Latest safety run `42314108213` failed at `test_pro_orchestrator.py` import because `Pillow` (`PIL`) was not installed. The preceding eight test modules completed successfully; do not label the full workflow green.
- Added a dedicated `Install offline test dependency` step installing `Pillow` in `.github/workflows/pro-safety-tests-manual.yml` on `feature/quran-video-pro` only.
- Fix commit: `e5d13045afc8a2425f287aed78ae070fc38dc0b4`.
- Workflow remains manual-only and contains no render/Telegram send action. Rerun still needed; no dispatch or production/original Quran engine changes have been made.

## 2026-11-07 — Safety workflow run #3 diagnosis
- New manual Pro safety run: [42318772835](https://github.com/samiouess-ux/IslamicTikTokAutomation/actions/runs/42318772835), commit `f8e0d76a151e7241901f21b9c257de1d0a7a97fb`, branch `feature/quran-video-pro`. Overall conclusion: FAILURE.
- The Pillow installation step completed successfully, so the previous `ModuleNotFoundError: PIL` blocker is resolved.
- Eight suites passed before the orchestrator suite: 75 tests total (6 + 10 + 13 + 10 + 8 + 5 + 7 + 16).
- `test_pro_orchestrator.py`: 6 tests passed, 1 test errored. Failing test: `test_candidate_preview_is_separate_from_rotation_and_production`.
- Diagnosis from traceback and source: the candidate manifest correctly has `rotation_approved=false`; `build_plan` therefore raises `FileNotFoundError` ("No eligible non-recent dua manifest; refusing to repeat or invent content."). The test currently expects `SystemExit`, so its expected exception type does not match the fail-closed rotation behavior. This is a test assertion mismatch, not evidence that candidate preview was admitted into production rotation.
- `test_render_dua_video.py` was not reached because the shell exits on the orchestrator suite failure. Full workflow is NOT green.
- Next safe code fix to review: update only the test expectation to the actual `FileNotFoundError` (with the no-eligible message), then rerun the manual offline safety workflow after explicit approval. Do not weaken the production rotation guard.
- No render, Telegram request/send, TikTok publish, secrets/Cron/bot-setting change, or original Quran engine operation occurred. No changes to `main` or `feature/telegram-review-notifications`.
