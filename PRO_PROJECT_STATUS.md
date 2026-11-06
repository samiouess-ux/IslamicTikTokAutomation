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
