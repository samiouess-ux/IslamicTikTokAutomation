# Approved-design Quran synchronization preview

## Status
- Isolated test branch: `test/quran-approved-design-sync-preview`
- Base: `test/quran-repeat-sync-preview`
- Production branch: `feature/telegram-review-notifications` (read-only reference)
- No production integration or production render has been performed.

## Objective
Render the already-validated repeat-aware timing for Surah Al-Kahf 18:14 using the exact approved Quran visual renderer/reference, without changing the production renderer.

## Required invariants
- Repeated phrase (word numbers 11–15) remains on screen across both recitations.
- The next phrase appears only after the repeated phrase finishes.
- Arabic and Saheeh International English remain paired by phrase.
- Use the approved reference ornaments, typography, gold ayah medallion and uncluttered layout from the production renderer.
- No translucent text panel or new decorative treatment.
- Keep a review-only artifact; no Telegram delivery, Cron trigger, or TikTok publishing.
- Do not modify `main` or `feature/telegram-review-notifications`.

## Existing verified timing input
- Previous isolated run: `46007075577`
- Commit: `99b0ceaaf6d4be0537196affee6dfd62d05cae12`
- Repeated phrase detected twice; expected 24-event sequence verified.
- Previous preview was timing-only on a neutral background and still requires human listening review.

## Next validation
1. Reuse the production renderer's approved design functions and reference asset in this isolated branch.
2. Render the same 18:14 repeat-aware phrase timings.
3. Check video dimensions, duration, event/group boundaries and report that production files were not changed.
4. Review the resulting MP4 visually and aurally before proposing any integration.

## Important
A successful automated render does not itself prove recitation/text synchronization. Listening and visual review remain mandatory.
