# Video design specification

## Supported content formats
- Complete surah.
- A consecutive range of verses.
- A single verse.
- The duration follows the approved recitation; never cut a verse mid-word.

## Canvas and visual identity
- 1080 × 1920 px (9:16), 30 FPS.
- Calm, respectful, uncluttered composition.
- Rotate among a curated set of approved backgrounds and layouts; do not default to the same background for every video.
- Nature, sky, sea, and architecture can be used when appropriate and rights-cleared.
- Use subtle motion and text transitions only; no flashing, bouncing, or distracting effects.
- Keep Arabic Quran text primary, large, centered, and legible.
- Place the English meaning underneath in a noticeably smaller font.
- Keep verse numbers and Arabic/English verse pairing accurate.

## On-screen information
- Show the surah name and exact verse range (or indicate that the complete surah is being recited).
- Do not display the reciter's name.

## Captions for each video
Prepare a caption for review alongside the video:
- Arabic caption and English caption.
- Identify the surah and exact verse range, or say it is the complete surah.
- Add a short, relevant description and restrained hashtags.
- Do not mention the reciter's name.
- Keep audio source and license/provenance information in internal project metadata, not public captions.

## Audio
- Authentic Quran recitation is required; music is prohibited.
- The exact recording must have documented reuse permission.
- The recitation must match the displayed Arabic text exactly.
- Never invent Quran text, translations, hadith, sources, or attributions.
- Do not use synthetic recitation as a replacement.

## Review and publishing
- Every generated video and caption must be presented for user review.
- No automatic publishing. Publishing remains disabled unless the user explicitly approves a specific video and caption.


## Approved visual reference — first test design (2026-10-31)

The user approved the latest rendered preview (GitHub Actions run 12; commit fb519f49ff61c7feae83120b332bfaa28b2ae085) as the reference style for the first video.

- Surah title: larger, bold Noto Naskh Arabic Bold, gold, centered inside an ornate pointed Islamic cartouche with double borders and small rosette details.
- Verse numbers: larger, bold Noto Naskh Arabic Bold, placed in separate gold multi-lobed ornamental medallions.
- Quran text: keep the exact original Arabic source strings unchanged; render in white Noto Naskh Arabic with proper RAQM shaping. Decorations and verse-number badges must remain separate and must not overlap or modify the Quran text.
- English translation: keep beneath the Arabic verses in a smaller, readable white font.
- Keep the calm natural background, vertical 9:16 layout, and translucent dark reading panel.
- Preserve the title/verse visual hierarchy and readability when varying backgrounds and subtle decorative details in future videos.
- No public reciter attribution; captions and publishing still require user review and explicit approval.


## Background rotation requirement — reaffirmed by user (2026-10-31)
- Do not use one fixed background for all videos.
- Maintain a curated pool of multiple backgrounds that have both explicit user approval and verified reuse rights.
- Rotate backgrounds across consecutive generated videos; exclude the most recently used background when at least one other eligible asset exists.
- Prefer visual variety across calm natural scenery, sky, sea, and suitable architecture, without making the video distracting or reducing text contrast.
- Background rotation must never bypass approval or rights checks. If no safe alternative is available, stop or use a documented fallback; do not silently select an unapproved asset.


## Quran variety safeguard (2026-10-31)
Rotate between reviewed surahs and verse selections (single ayahs or consecutive ranges). A candidate is eligible only when exact Uthmani text is present in the reviewed reference snapshot, the translation is sourced and verified for those exact verses, and an authentic permitted recitation matches the exact passage and order and has been user-reviewed. Preserve the approved 9:16 gold cartouche, separate gold verse medallions, white Arabic, smaller English translation, calm approved backgrounds, and all audio rules: no music, no synthetic recitation, no public reciter name. Skip any candidate that fails a check; never trade correctness for variety.


## Full-Quran rotation and short-video duration (2026-10-31)
- The Quran engine must not be hard-coded to Ash-Sharh or any other single surah. Its target inventory is all 114 surahs and all ayahs, with deterministic rotation across surahs and contiguous ayah passages.
- Build each clip from the longest contiguous prefix of complete ayahs whose measured final audio duration is at most 40 seconds. There is no artificial minimum duration. The hard maximum applies to the final rendered MP4 as well as its audio.
- Never speed up recitation, cut a verse mid-recitation, reorder verses, or combine non-contiguous ayahs to meet the limit. If the next complete verse would exceed the limit, close the clip before it and leave that verse and all later ayahs unselected for a future batch.
- Reuse the approved Ash-Sharh render as the visual template/example, not as a fixed content source. Select surah title, verse number, exact Arabic, translation, and matching verse audio dynamically from validated Quran-wide sources.
- Full-Quran coverage requires a versioned trusted Uthmani text corpus, a sourced translation corpus, and the official reuse-permitted verse-audio archive. Verify source identifiers, exact verse mapping, archive entry mapping, and rights before enabling a passage. Missing or mismatched data must fail closed, not silently narrow coverage to the two sample surahs.
- Keep the approved 9:16/1080x1920/30fps design, gold ornate surah cartouche, independent gold verse medallions, white Arabic, smaller English translation, varied approved backgrounds, authentic matching recitation, no music/synthetic audio, no public reciter attribution, and manual review.


## Opening cover frame (2026-11-01)
- Every Quran review video begins with a short, elegant 9:16 opening cover showing "القرآن الكريم", the Arabic surah name, and the exact selected ayah range in Arabic numerals.
- Use the established gold cartouche and calm dark panel; preserve the existing ayah layout after the cover fades.
- Target cover display: 1.6 seconds with a gentle 0.4-second alpha fade. The selected prepared recitation stream starts at video time 0; the cover must not insert silence or delay playback, and the renderer must not alter that stream.
- The first frame is the TikTok cover candidate. TikTok publishing remains manual; the user chooses the cover in the TikTok app.


## Parallel cinematic review mode (2026-11-17)

- The existing renderer now supports an opt-in `--visual-mode cinematic`; `classic` remains the default and its rendering path is unchanged.
- Cinematic mode uses the existing approved moving-video and photo background libraries, with a slow centered zoom and restrained crossfades (maximum 0.45 seconds) between ayah scenes.
- Each complete ayah remains its own timed overlay. Arabic text and its paired Saheeh International English meaning are not rewritten or merged across scenes.
- The opening cover remains visible only for the first 0.6 seconds. The original MP3 ayah files are concatenated by stream copy; recitation is not synthesized, sped up, or replaced.
- Cinematic runs are review-only. They must never reserve or send Telegram deliveries, record delivery history, or enable auto-publishing. The existing production branch and scheduled classic mode remain unchanged until the user reviews and accepts the cinematic output.
