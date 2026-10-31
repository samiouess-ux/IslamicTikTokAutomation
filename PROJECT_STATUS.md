# Project status — IslamicTikTokAutomation

Last updated: 2026-10-31

## Project goal
Prepare two vertical Islamic reminder videos per day:
- one Arabic version
- one French version

The user must review and approve every video before publishing. Automatic publishing is disabled.

## Agreed video style
- Format: vertical 9:16, target 1080x1920, 30 FPS.
- Arabic Quran text is the main visual element and must be larger.
- French translation appears underneath in a noticeably smaller font.
- Quran recitation is required; music is not allowed.
- Use a beautiful, calm, high-quality background, preferably subtle natural scenery with gentle motion.
- Recitation must be authentic and match the displayed verses exactly.
- Never invent Quran text, hadith, attribution, source, or translation.

## First test video
Theme: hope and ease after hardship.
- Surah Ash-Sharh (94), verses 5–6.
- Arabic: فَإِنَّ مَعَ الْعُسْرِ يُسْرًا ۝٥ إِنَّ مَعَ الْعُسْرِ يُسْرًا ۝٦
- French translation selected in conversation: Muhammad Hamidullah translation; verify exact wording and source before production.
- Proposed background: peaceful natural scenery (mountains, sunrise, sea, or green valley), gently animated.

## Current technical state
Initial repository structure exists:
- `src/main.py`
- `config/settings.example.json`
- `requirements.txt`
- `.gitignore`
- `README.md`

No video-generation pipeline, recitation audio, external services, or publishing integration has been configured yet.

## Next steps
1. Verify the exact French translation and reliable source for verses 94:5–6.
2. Select a lawful/reusable authentic recitation audio source and confirm the recitation matches the verses.
3. Choose a free background asset/source and verify its reuse terms.
4. Build one Arabic/French 9:16 test video.
5. Review the output with the user before any further automation.

## Non-negotiable constraints
- Prefer free/open-source tools; no upfront paid services.
- Work step by step and test each phase.
- Do not publish automatically.
- Do not make repository changes beyond the agreed project scope.
