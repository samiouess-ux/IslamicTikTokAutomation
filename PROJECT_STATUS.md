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

## Research checkpoint (2026-10-31)
- French Hamidullah wording for 94:5 and 94:6 verified against Quran.com and QuranEnc. Keep each verse paired with its own ayah number; display translation smaller than Arabic.
- Candidate background source: Pexels videos. Its official license/help pages state that videos can be used and modified for commercial projects without attribution, subject to restrictions and third-party rights. Save the specific asset page and creator details when selecting a clip.
- Recitation audio: not yet selected. Do not assume that a stream or downloadable recitation is cleared for reuse in monetized TikTok videos. Verify rights/permission for the exact recording before embedding or publishing.
- Suggested first workflow: select one calm nature video from Pexels; select a reciter/recording with documented reuse permission; then assemble and review the 9:16 test video.

## Reciter preference
- User proposed either Islam Sobhi or Yasser Al-Dosari.
- Both have recordings of Surah Ash-Sharh available online; no recording has been selected or downloaded yet.
- Before using a specific recording in TikTok videos, verify permission/licensing for that exact audio recording. Availability to stream/download does not by itself grant reuse rights.
- Next action: identify a rights-cleared recording by one of the two preferred reciters, or obtain explicit permission from the relevant rights holder.

## Audio-rights research update (2026-10-31)
- Quran.com states it does not own the recitation recordings and cannot grant reuse/redistribution permission; rights belong to reciters or managing organizations. A specific Yasser Al-Dosari reuse request was directed to the rights holder; one discussion identifies Salam Network as managing rights for Yasser Al-Dosari recordings. Do not download/use these recordings for publication without explicit permission or a clear license for the exact recording.
- No clear reuse license has yet been verified for Islam Sobhi recordings either. Keep both as preferred choices, but do not assume public availability means permission.
- Pexels confirms its photos/videos are free for personal and commercial use under the Pexels license, subject to restrictions and third-party rights. Use a specific clip only after saving its source page/creator and checking it against the license.
- Next practical step: choose a calm nature background clip from Pexels and separately continue looking for an explicitly reusable recitation or obtain written permission for a preferred recording. Keep music disabled and publishing approval required.
