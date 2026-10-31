# Project status — IslamicTikTokAutomation

Last updated: 2026-10-31

## Project goal
Prepare two vertical Islamic reminder videos per day:
- one Arabic version
- one English version

The user must review and approve every video before publishing. Automatic publishing is disabled.

## Agreed video style
- Format: vertical 9:16, target 1080x1920, 30 FPS.
- Arabic Quran text is the main visual element and must be larger.
- English translation appears underneath in a noticeably smaller font.
- Quran recitation is required; music is not allowed.
- Use a beautiful, calm, high-quality background, preferably subtle natural scenery with gentle motion.
- Recitation must be authentic and match the displayed verses exactly.
- Never invent Quran text, hadith, attribution, source, or translation.

## First test video
Theme: hope and ease after hardship.
- Surah Ash-Sharh (94), verses 5–6.
- Arabic: فَإِنَّ مَعَ الْعُسْرِ يُسْرًا ۝٥ إِنَّ مَعَ الْعُسْرِ يُسْرًا ۝٦
- Language choice updated by user: English replaces French (not an additional third language).
- English translation: Sahih International, wording verified for both verses against Quran.com / Quranic Arabic Corpus; retain the exact verse-specific wording.
- Proposed background: peaceful natural scenery, gently animated; Pexels candidate is documented in content/first_video.json.

## Current technical state
Initial repository structure and project documentation exist:
- src/main.py
- config/settings.example.json
- requirements.txt
- .gitignore
- PROJECT_STATUS.md
- DESIGN_SPEC.md
- content/first_video.json

The language configuration and first-video manifest are now set to Arabic + English. No video-generation pipeline, recitation audio, external services, or publishing integration has been configured yet.

## Next steps
1. Verify the exact English translation wording and source for verses 94:5–6.
2. Reciter approved: Maher Al-Muaiqly (Hafs), selected by the user. The King Fahd Complex official rights page grants free public-use permission for the listed recordings inside and outside Saudi Arabia. The exact Surah Ash-Sharh audio file still needs to be obtained and checked before production.
3. Review and approve the Pexels background candidate.
4. Build one Arabic/English 9:16 test video.
5. Review the output with the user before any further automation.

## Non-negotiable constraints
- Prefer free/open-source tools; no upfront paid services.
- Work step by step and test each phase.
- Do not publish automatically.
- Do not use music.
- Do not use recitation audio without documented reuse permission for the exact recording.
- Do not make repository changes beyond the agreed project scope.

## Research checkpoint (2026-10-31)
- Earlier French translation research is retained only as historical context; French is no longer an output language.
- Candidate background source: Pexels videos. Its official license/help pages state that videos can be used and modified for commercial projects, subject to restrictions and third-party rights. Save the specific asset page and creator details when selecting a clip.
- Recitation audio: reciter selected by user — Maher Al-Muaiqly (Hafs). The official King Fahd Complex page grants free public-use permission for the listed recordings in apps, websites, broadcast channels, and private/institutional works inside and outside Saudi Arabia. The official reciter page lists full-surah and verse-by-verse downloads. The exact Surah Ash-Sharh file has not yet been downloaded, listened to, or technically checked; do not embed it until that check is complete.
- User's initial preferred reciters: Islam Sobhi or Yasser Al-Dosari. No reuse permission has been verified for their recordings. Quran.com states it cannot grant reuse rights; rights belong to the reciter or rights manager. A public reuse-permission candidate was found from the King Fahd Complex: Maher Al-Muaiqly (Hafs), with Surah Ash-Sharh listed on his official recitation page. User approval is still needed before switching reciter.
- The Pexels ocean-and-mountains clip by Engin Akyurt remains a candidate only; it has not been downloaded or approved.
