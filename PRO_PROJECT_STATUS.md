# Islamic Dua & Adhkar Pro — Project Status

- Repository: `samiouess-ux/IslamicTikTokAutomation`
- Active Pro branch: `feature/quran-video-pro`
- Product scope: dua and adhkar videos only.
- Quran production remains on `feature/telegram-review-notifications`; do not modify it.
- Original Telegram bot reuse is desired. A separate Pro delivery route is not yet implemented or verified.
- TikTok publishing remains manual; automatic publishing is prohibited.

## Verified implementation on Pro
- `src/validate_content_manifest.py`: strict metadata/source/human-review checks for dua and dhikr, including hadith grading for prophetic duas.
- `src/render_dua_video.py` (pre-existing): dedicated dua/dhikr slideshow renderer with per-item explicit durations, Arabic overlay, audio-duration consistency checks, silent or approved spoken/ambient audio, and a 65-second hard cap (60-second target).
- `src/pro_orchestrator.py` (added): separate dua/dhikr-only preflight and optional render routing; uses deterministic recent-repeat avoidance and a Pro-specific history file. It routes to the existing `render_dua_video.py`, validates explicit positive item durations and the renderer hard cap, and supports multiple reviewed items per manifest.
- `src/orchestrator.py` and `src/render_video_scenes.py` remain Quran-specific and unchanged.
- Existing renderer tests: `tests/test_render_dua_video.py`. New Pro orchestration tests: `tests/test_pro_orchestrator.py`.

## Latest Pro-specific implementation commits
- Validator: `545496fd29b590c38abf61f9a82b3750d90060c6`
- Validator tests: `e4c3ae5365a44277012a226bb99a5ae191583e33`
- Pro orchestrator: `28b0dba34a409497ec5b11f44be299525084205c`
- Pro orchestration tests: `75a603b2adedfdbeecf043ab75f48189513cbd7f`
- Renderer consolidation: `17921d5dc5aed0c10474c639ba29229b301c6154`
- Updated orchestration tests: `c62e7cc042381ecdb8f85faab6f93faeb5b34fce`
- Duplicate experimental renderer and its tests were removed; see the development log for exact removal commits.

## Telegram architecture audit
- Existing `telegram-quran-request.yml` is pinned to the production branch and must not be modified or reused for Pro.
- Existing `send_telegram.py` uses `TG_BOT_TOKEN` and `TELEGRAM_CHAT_ID`, but its caption is hard-coded for Quran review.
- Added `src/send_pro_telegram.py`: separate Pro branding, dua/dhikr-only metadata gate, review-only and auto-publish safeguards, 50 MB/1,024-character limits, and Telegram message-ID confirmation. It reuses the existing secret names without reading or changing them. Added `src/pro_delivery_ledger.py` and tests for reserved/delivered/uncertain states, duplicate blocking, message-ID confirmation, and explicit human reconciliation. The ledger is not yet integrated into the orchestrator/workflow; do not enable Telegram delivery until that integration and serialized ledger commits are implemented.

## Latest Pro Telegram sender commits\n- Sender: `9f93f7a143763a2f1d2384c5f8be829ce733b457`\n- Offline sender tests: `b558c01736860d101e37e4aa3a175d4c97b43f61`\n\n## Latest changes (2026-11-06)\n- Pro renderer target and hard maximum reduced to 40 seconds (commit `3a2fdffb1ec1ba5b9e2fcae4f50eba08f1b57dc3`).\n- Added validated Pro Telegram caption preparation (commit `d81dc90d07b50c0c8d95d58f55d634bd333f96c4`) and an offline test (`1404abe2c2097252614f95270d5298bf2ae16b3c`).\n- No tests executed; no workflow, render, Telegram call, or publishing performed.\n\n## Latest changes (2026-11-06)\n- Pro renderer target and hard maximum: 40 seconds (`3a2fdffb1ec1ba5b9e2fcae4f50eba08f1b57dc3`).\n- Pro Telegram caption preparation: `d81dc90d07b50c0c8d95d58f55d634bd333f96c4`; test `1404abe2c2097252614f95270d529d4c4`.\n- Pro delivery ledger: `acfa42ea76285f6a6383325617b1bf2ad2bd1e69`; tests `ceb5c3f35ce52786c7bc49d31fcc3934dc60b31c`.\n- Tests have not been run; no workflow, render, Telegram API call, or publishing action has occurred.\n\n## Validation status
- GitHub writes succeeded on `feature/quran-video-pro`.
- Unit tests have NOT been run; no test is reported as passing.
- No preflight command, MP4 render, GitHub Actions run, Telegram send, or TikTok publish has occurred.
- No verified dua/dhikr production library or Pro Telegram workflow has been added. The sender module exists but has not been executed or connected to a workflow.
- No production branch, Cron, secrets, or production delivery path was changed.

## Next steps
1. Integrate the reservation ledger with Pro preflight and test that all reserved/delivered/uncertain IDs are excluded.\n2. Add a serialized manual-dispatch-only Pro workflow with strict branch guards and separate explicit render/send confirmations.
2. Add tests for sender caption, file limits, and workflow isolation.
3. Add a non-content schema/example and then build a verified library from reviewed primary sources.
4. Request explicit approval before any workflow dispatch, render, or Telegram send.

## Safety and change control
- All Pro changes only on `feature/quran-video-pro`.
- Do not touch `feature/telegram-review-notifications`, Cron, secrets, or production delivery.
- Do not run Actions, render, send Telegram, or publish to TikTok without explicit approval.
- Record every implementation commit and validation result in `PRO_DEVELOPMENT_LOG.md`.
