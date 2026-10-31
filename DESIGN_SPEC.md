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
