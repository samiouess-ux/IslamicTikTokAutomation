# Quran video duration requirement

- Preferred target: approximately 45 seconds; this is a target, not a stopping limit.
- Hard maximum: 60.0 seconds for every final MP4 and its audio, whether it contains one ayah or several.
- Continue selecting the next complete contiguous ayah after passing 45 seconds whenever the combined whole-ayah sequence remains at or below 60 seconds. Do not stop early merely because the 45-second target was crossed.
- Never cut, split, truncate, skip, reorder, or speed up a Quran ayah to meet a duration target.
- When adding the next complete contiguous ayah would make the part exceed 60 seconds, end the current video at the preceding complete ayah boundary and continue from that next ayah in a later video/candidate.
- If an individual ayah exceeds 60 seconds, defer that complete ayah intact; do not create or send an overlong video.
- Keep verse order contiguous; no gaps, repeats, or partial ayahs.
- The implementation must reject a final rendered MP4 or audio stream longer than 60.0 seconds. A passing audio-only check is not sufficient.
- Short complete passages remain valid; there is no artificial minimum duration.
