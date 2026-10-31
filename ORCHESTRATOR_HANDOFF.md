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
