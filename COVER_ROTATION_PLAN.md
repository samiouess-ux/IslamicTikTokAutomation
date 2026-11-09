# Cover rotation preview — isolated proposal

Status: preview branch only. This file does not change the renderer or scheduled workflow.

## User-approved behavior
- Keep the existing approved cover template unchanged and available as a permanent option.
- Add new cover variants that preserve the established identity and the original cover's layout hierarchy.
- Select covers automatically for each generated video.
- Never select the same cover for two consecutive videos when at least two approved covers are available.
- Rotate through the approved pool; persist the last-used cover ID so a workflow rerun does not accidentally repeat it.
- If only one approved cover is available, use it rather than failing.
- If a new variant is missing, unapproved, or fails validation, fall back to the existing approved cover.

## Non-goals / protected behavior
- Do not change when or how the opening cover is inserted into the video.
- Do not change audio start time, audio bytes, cover duration, fade, video dimensions, Telegram delivery, cron scheduling, or publishing behavior.
- Do not remove or overwrite the original cover asset.
- Do not enable a new design in production before the user reviews and approves it.

## Visual variety direction
The new covers should feel meaningfully different at a glance, while clearly belonging to the same page identity:
- Keep the same core title hierarchy, Arabic typography, respectful Quranic tone, and recognizable brand palette.
- Explore distinct treatments such as deep emerald with gold ornament, warm ivory with restrained geometric detail, and a darker night-sky treatment with subtle light.
- Vary framing, ornament placement, and background atmosphere rather than changing only tiny colors.
- Keep the Quran title and surah name readable; avoid busy imagery behind text.
- Do not create final variants until the original template has been visually inspected. The original remains an unchanged option.

## Preview acceptance checks
1. Show the original cover alongside each proposed variant.
2. Verify Arabic shaping and reviewed diacritics for every surah name.
3. Verify the exact ayah range remains legible and correctly rendered.
4. Verify consecutive selections differ: A → B → C → A, never A → A when alternatives exist.
5. Keep all changes isolated until explicit approval.
