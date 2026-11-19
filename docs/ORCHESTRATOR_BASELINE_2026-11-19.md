# Orchestrator Baseline — 2026-11-19

## Purpose and authority
This file is the dated baseline for orchestrating work on the existing Quran video engine. It records observed repository facts and user-confirmed operating constraints. It is not permission to change production behavior.

- Repository: `samiouess-ux/IslamicTikTokAutomation`
- Active branch only: `feature/telegram-review-notifications`
- Baseline source HEAD before this documentation commit: `1d4a7f92a18935d0c1048f7d02dc800ce15f4102`
- `main`: protected by project instruction; do not modify.
- TikTok publishing: manual only, after the user's own review.
- External Cron: user confirms it is working and sends at three daily Tunisia slots (04:10, 12:10, 18:10). Do not change it or add another scheduler.
- Production must continue operating during development. Preserve the existing workflow, original Telegram bot, delivery history, and safety gates.

## Non-negotiable change protocol
1. Read the current branch HEAD and relevant files before every task.
2. Identify the exact existing behavior and prove the proposed gap before proposing implementation.
3. Do not rebuild existing functionality or add duplicate systems.
4. No source/workflow/configuration changes without explicit user approval.
5. Keep each approved change small and isolated on the active branch.
6. Run only the relevant automated tests plus the necessary regression set; do not repeat unchanged tests without a reason.
7. Review the diff and actual test/workflow evidence. A green workflow alone is not proof of real Telegram delivery or visual quality.
8. Never manually dispatch a production send as a test. Test-only paths must remain isolated from Telegram delivery and production history.
9. Do not change Cron, Telegram credentials, bot, delivery architecture, or TikTok publishing policy without separate explicit approval.
10. Record every decision, change, test, result, failure, and next step here or in the linked project records. Never claim a record was saved unless the GitHub write is verified.

## Current verified operational snapshot
Evidence inspected on 2026-11-19:

- Latest observed inventory workflow run: `44512334782`, run #514, completed `success`; event type `workflow_dispatch`.
- Its job logs show the real Telegram send was confirmed with `message_id=124`, MP4 size 6.9 MB, followed by delivery-history finalization and branch push.
- Rendered video in that run: Surah As-Saff (61), ayahs 1–3, 1080x1920, H.264 + MP3, measured duration 30.725 seconds.
- Delivery history reports 288 ayah references protected from reuse after that delivery.
- Latest branch HEAD is the bot-created delivery-finalization commit above. The workflow run started from an earlier SHA and then pushed the final history commit; do not confuse run head SHA with the resulting current branch HEAD.
- The workflow trigger in the repository is `push` (path-filtered) plus `workflow_dispatch`; there is no native `schedule` trigger in this workflow. The three daily launches are handled externally, as user-confirmed. The repository logs alone do not expose cron-job.org's live configuration.
- The last observed run contains successful test groups including renderer (26), Telegram sender (8), delivery history (4), delivery-attempt safety (6), and workflow safety (9). These are test results, not a visual inspection of the MP4.
- No source code or production workflow was changed as part of this baseline inspection.

## TikTok Growth audit — priority 1
Existing implementation inspected:

- `src/quran_social_caption.py` builds Arabic and English captions from the selected surah/range and a small set of detected themes.
- It produces five deterministic hashtags based on the video ID, using Arabic core tags, English core tags, and theme tags.
- The workflow runs `tests/test_quran_social_caption.py` and writes the generated caption JSON into the workflow output before Telegram delivery.

Observed gaps / audit findings:

- No implemented opening hook system was found in the inspected caption builder or active inventory workflow.
- No dedicated CTA generation was found in those inspected paths.
- No TikTok post-performance analytics/feedback loop was found in the inspected repository paths.
- Hashtag rotation is deterministic from the video ID; it is not a persistent global anti-repetition ledger and does not guarantee that a caption/tag set will never recur.
- Static review found a likely Arabic hashtag classification defect: the language filter appears to compare each Arabic character against literal escaped strings rather than the actual Unicode Arabic range. The existing tests assert five unique tags and theme selection, but do not assert that Arabic tags are actually returned in the Arabic field. Treat this as a confirmed code-review finding requiring a focused regression test before any fix is approved.
- Growth changes must remain Quran-appropriate and must not add music, invented religious claims, or automatic TikTok posting.

## Existing engine safeguards and known inconsistencies

### Audio duration
- Current source `src/prepare_quran_review_batch_audio.py` sets `MAX_SECONDS = 45.0`; renderer and delivery tests also explicitly accept/reject against 45 seconds.
- Existing project handoff notes record a user-approved 40-second hard maximum, while the user's stated desired practical range is 30–40 seconds.
- This is a source/documentation mismatch. Do not change it silently. Before implementation, reconcile the requirement and ensure whole-ayah selection; never split an ayah or speed up recitation.

### Background rotation
- `data/background_candidates.json` contains 15 candidates; 11 are marked approved, user-approved, download-verified, and 9:16 in the inspected catalog.
- `src/background_rotation.py` filters for explicit approval, verified download, portrait ratio, and HTTPS URLs; it rotates deterministically and avoids IDs supplied as recent when alternatives exist.
- This is not proof of unlimited variety or a globally persistent anti-repeat guarantee. A finite catalog will eventually repeat.
- The renderer darkens the blurred full-screen background fill behind the cover foreground. This code inspection does not prove whether the original foreground cover itself is darkened in the final MP4. Visual inspection is still required before claiming the cover-darkness issue is solved.

### Quran text, translation, recitation, and delivery
- The current workflow builds a 6,236-verse Saheeh International English translation candidate corpus and a 6,236-verse Uthmani Arabic candidate corpus with a mandatory human-review/rendering gate for the Arabic candidate catalog.
- The workflow uses whole-ayah contiguous selection and checks the final video duration against its current 45-second code limit.
- Telegram delivery is review-only; sender requires valid credentials and a positive Telegram message ID. The workflow reserves the selected ayahs before sending, then records only confirmed selected ayahs and clears the pending reservation after confirmation.
- TikTok publishing remains manual.
- The latest confirmed delivery is evidenced by run logs; this does not replace visual/audio review of the actual MP4.

## Test strategy — avoid waste
- Use existing GitHub Actions test groups already defined in `.github/workflows/build-quran-audio-inventory.yml`.
- For a small code change, run its focused test first, then only the relevant regression group(s).
- Run the full workflow validation only when a change affects cross-stage integration, shared data contracts, rendering, or delivery orchestration.
- Never send a real Telegram video merely to test a code change. Use isolated test-only mode and verify its conditions skip production reservation, send, and history updates.
- Do not repeat a successful test unless the relevant code/input/environment changed or a failure requires diagnosis.
- User should not be asked to perform routine tests manually; report the automated evidence and ask only for genuinely human-only review (e.g. visual/audio quality or TikTok performance data).

## Next work order
1. Finish the read-only audit of existing TikTok Growth behavior and tests; confirm the Arabic hashtag finding with a minimal focused test.
2. Present evidence, exact affected files, risk, and the smallest safe proposed change. Wait for user approval.
3. Implement only the approved TikTok Growth improvement; preserve the existing daily Cron launches and Telegram delivery path.
4. After Growth, address other proven issues one at a time, starting with the 40-vs-45-second policy mismatch only after confirming the exact user requirement.

## Evidence links
- Active branch: https://github.com/samiouess-ux/IslamicTikTokAutomation/tree/feature/telegram-review-notifications
- Last observed workflow run: https://github.com/samiouess-ux/IslamicTikTokAutomation/actions/runs/44512334782
- Baseline branch HEAD: https://github.com/samiouess-ux/IslamicTikTokAutomation/commit/1d4a7f92a18935d0c1048f7d02dc800ce15f4102

---
This document records the state observed on 2026-11-19. Refresh the branch HEAD and evidence before relying on it in a later session.
