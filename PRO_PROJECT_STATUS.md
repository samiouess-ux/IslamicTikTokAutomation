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
- `src/send_pro_telegram.py`: isolated Pro-branded sender with dua/dhikr-only, review-only, and reservation-ledger safeguards. Its `--reservation-persisted` mode requires a pre-existing reserved entry matching manifest ID, content type, and workflow run ID; it has not been executed or connected to a workflow.
- `src/prepare_pro_telegram_caption.py`: validated review caption preparation.
- Quran-specific `src/orchestrator.py`, `src/render_video_scenes.py`, and production workflow must remain untouched.

## Delivery ledger and Telegram integration — 2026-11-06
- Production cleanup is complete: `src/pro_delivery_ledger.py` and `tests/test_pro_delivery_ledger.py` are absent from `feature/telegram-review-notifications`.
- Recreated both files only on `feature/quran-video-pro`. The ledger supports reserved, delivered, and uncertain states, requires a positive Telegram message ID for delivery confirmation, and requires explicit human confirmation before releasing an uncertain reservation.
- The ledger uses atomic JSON replacement and a process-level file lock. This does not yet persist state across separate GitHub workflow runs or serialize independent runners.
- `src/send_pro_telegram.py` now reserves before contacting Telegram, never auto-retries, marks failed/ambiguous outcomes uncertain, and records delivered only after a valid Telegram message ID.
- `src/prepare_pro_telegram_caption.py` now includes the stable manifest ID needed by the sender.
- Sender tests were added for successful confirmation and uncertain outcomes blocking a second attempt.
- **Important:** no Pro workflow currently persists the ledger between runs. Cross-run duplicate protection is therefore not yet complete, and Telegram delivery remains disabled.
 
## Validation status
- Unit tests have NOT been run; no test is reported as passing.
- No Pro preflight command, MP4 render, GitHub Actions workflow, Telegram API call, or TikTok publish has occurred.
- No secrets, Cron settings, or production workflow logic were changed.
- Pro has no verified content library yet; do not attempt delivery until reviewed manifests exist and idempotency is safely implemented.

## Cross-run persistence design
- Design committed in `PRO_LEDGER_PERSISTENCE_DESIGN.md` (commit `e3c50a6c66a13d23c753cb9c7f975c1b633accd5`).
- Selected approach: commit the ledger JSON to this Pro branch using normal checkout/commit/push, protected by one fixed Actions concurrency group.
- Required order: persist reservation before Telegram; send once; persist delivered/uncertain outcome. A failed final push leaves the pre-send reservation blocking duplicates.
- No Pro workflow exists yet, and no reviewed `content/pro` manifests exist.

## Next steps
1. Add a narrow ledger-only persistence helper and tests for all failure boundaries. Sender support for a pre-persisted reservation is implemented, but not yet wired to GitHub persistence.
2. Add a dormant `workflow_dispatch`-only Pro workflow with exact branch guard, fixed concurrency, and minimal permissions; no schedule or production secrets.
3. Build a reviewed dua/dhikr content library from trustworthy primary sources.
4. Run the offline test suite in an approved environment and record exact results.
5. Ask for explicit approval before any workflow dispatch, render, or Telegram send.

## Safety and change control
- All Pro implementation commits only on `feature/quran-video-pro`.
- Do not touch production Quran logic, production workflow, Cron, secrets, or delivery route.
- Do not run Actions, render, send Telegram, or publish to TikTok without explicit approval.
- Record every implementation commit and validation result in `PRO_DEVELOPMENT_LOG.md`.

