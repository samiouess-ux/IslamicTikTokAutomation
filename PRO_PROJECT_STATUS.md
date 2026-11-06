# Islamic Dua & Adhkar Pro — Project Status

- Repository: `samiouess-ux/IslamicTikTokAutomation`
- Active Pro branch: `feature/quran-video-pro`
- Product scope: dua and adhkar videos only.
- Quran production remains on `feature/telegram-review-notifications`; do not modify it.
- Original Telegram bot reuse is desired, but isolated Pro delivery is not yet implemented or verified.
- TikTok publishing remains manual; automatic publishing is prohibited.

## Verified implementation on Pro
- `src/validate_content_manifest.py` requires stable unique item IDs, exact Arabic, named HTTPS source, exact source reference, verified status, human review, explicit content kind, valid optional repeat count, and hadith grading for prophetic duas.
- `src/render_dua_dhikr.py` is a dedicated review-only renderer for exactly one dua/dhikr item per manifest. It builds a 1080×1920 Arabic overlay, supports optional English meaning/repeat count, approved audio or silent duration, approved background, and a 40-second cap.
- `tests/test_render_dua_dhikr.py` adds layout and invalid-text tests.
- `src/orchestrator.py` remains Quran-only and is intentionally unchanged.
- `src/render_video_scenes.py` remains Quran-specific and is intentionally unchanged.

## Latest implementation commits
- Validator: `545496fd29b590c38abf61f9a82b3750d90060c6`
- Validator tests: `e4c3ae5365a44277012a226bb99a5ae191583e33`
- Dua/dhikr renderer: `6eded850610126acdc10becac8e66d62cdcb8948`
- Renderer tests: `463512211a001475b23cc5472c190f0de152ccc0`
- Development log and this status file are updated in this checkpoint.

## Validation status
- GitHub writes were successful on `feature/quran-video-pro`.
- Unit tests have NOT been run; no test is reported as passing.
- No MP4 render, GitHub Actions run, Telegram send, or TikTok publish has occurred.
- The FFmpeg filter graph, silent audio path, installed-font/RAQM availability, and visual output remain unverified.
- No sourced dua/dhikr content library has been added.

## Next steps
1. Add an isolated Pro-only orchestrator with dry-run preflight and recent-repeat avoidance.
2. Add tests for selection/history and renderer routing.
3. Build a verified content library only from reviewed primary sources; do not invent religious text or authenticity claims.
4. Inspect original-bot delivery architecture read-only, then design an isolated Pro route. Do not send messages or change secrets without explicit approval.
5. Request explicit approval before any workflow, render, or Telegram test.

## Safety and change control
- All Pro changes only on `feature/quran-video-pro`.
- Do not touch `feature/telegram-review-notifications`, Cron, secrets, or production delivery.
- Do not run Actions, render, send Telegram, or publish to TikTok without explicit approval.
- Record every implementation commit and validation result in `PRO_DEVELOPMENT_LOG.md`.
