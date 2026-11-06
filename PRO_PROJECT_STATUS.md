# Islamic Dua & Adhkar Pro — Project Status

- Repository: `samiouess-ux/IslamicTikTokAutomation`
- Active Pro branch: `feature/quran-video-pro`
- Product scope: dua and adhkar videos only.
- Quran production remains on `feature/telegram-review-notifications`; do not modify it.
- Original Telegram bot reuse is desired, but isolated Pro delivery is not yet implemented or verified.
- TikTok publishing remains manual; automatic publishing is prohibited.

## Verified source baseline
- `src/validate_content_manifest.py` supports `dua` and `dhikr` and now requires stable unique item IDs, exact Arabic, named HTTPS source, exact source reference, verified status, human review, explicit content kind, valid optional repeat count, and hadith grading for prophetic duas.
- `src/orchestrator.py` remains Quran-only and selects `content_type = quran`.
- `src/render_video_scenes.py` remains Quran-specific. A dedicated dua/dhikr renderer is still required.
- `src/asset_rotation.py` may be reusable for approved, rights-verified visual/audio assets, subject to schema mapping and tests.
- No verified dua/dhikr production library, end-to-end render, or Telegram delivery exists yet on this branch.

## Latest implementation commits
- Validator hardening: `545496fd29b590c38abf61f9a82b3750d90060c6`
- Regression tests added: `e4c3ae5365a44277012a226bb99a5ae191583e33`
- Tests have not been executed; do not report them as passing.

## Next implementation sequence
1. Implement dedicated Arabic dua/dhikr renderer and professional templates.
2. Add renderer tests and verify layout bounds/Arabic shaping without producing a video.
3. Extend Pro orchestration and non-repetition history for dua/dhikr only.
4. Build a sourced content library; fail closed on missing/uncertain authenticity data.
5. Design isolated original-bot Telegram review delivery; do not send or change secrets until explicitly approved.
6. Request approval before any render or Telegram test.

## Safety and change control
- All Pro changes only on `feature/quran-video-pro`.
- Do not touch `feature/telegram-review-notifications`, Cron, secrets, or production delivery.
- Do not run Actions, render, send Telegram, or publish to TikTok without explicit approval.
- Log every commit, test result, render, failure, and user approval in `PRO_DEVELOPMENT_LOG.md`.

## Latest checkpoint — 2026-11-06
- Dua/dhikr source validation hardened and regression tests added.
- No tests executed; no workflow or render; no Telegram action.
