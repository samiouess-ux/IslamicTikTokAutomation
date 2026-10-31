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
