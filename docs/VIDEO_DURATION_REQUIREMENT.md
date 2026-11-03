# Quran video duration requirement

- Hard maximum: 40.0 seconds for both the final MP4 and its audio.
- No artificial minimum duration; short complete passages are valid.
- Never cut, split, or truncate a Quran ayah to meet the duration target.
- If the next complete ayah would make the video exceed 40 seconds, leave that ayah for a later complete video/candidate; do not send an overlong video.
- If a single ayah itself exceeds 40 seconds, do not create or send an overlong video and do not truncate the ayah. Mark it as deferred for review/handling.
- Keep verse order contiguous; no gaps, repeats, or partial ayahs.
- The implementation must reject a final rendered MP4 longer than 40.0 seconds. A passing audio-only check is not sufficient.
