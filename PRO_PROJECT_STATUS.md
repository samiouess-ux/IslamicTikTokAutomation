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
- Delivery-cycle tests cover first-push failure or no-op blocking sender invocation, uncertain-state persistence, persist/send/persist ordering, final-push failure behavior, and rejection of a ledger path outside the persisted checkout.
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
- Latest development-log update: `40c8ab02956da15df4730debe5375bde338c724a`.
- Development log update: `ace2159b6969e75f7a17571e1b9d025829a4a99d`.

## Safety and change control
- All Pro implementation commits only on `feature/quran-video-pro`.
- Do not touch production Quran logic, production workflow, Cron, secrets, or delivery route.
- Do not run Actions, render, send Telegram, or publish to TikTok without explicit approval.
- Record every implementation commit and validation result in `PRO_DEVELOPMENT_LOG.md`.

