# Cover rotation implementation notes

This is an isolated implementation note. No production renderer, scheduler, or delivery workflow is changed here.

## Existing patterns found in the current code
- `src/asset_rotation.py` currently accepts only `background` and `audio`; it requires explicitly approved and rights-verified catalog entries and excludes IDs passed in `recent_ids`.
- `src/background_rotation.py` similarly selects only user-approved, download-verified backgrounds and accepts recent IDs.
- `src/render_quran_review_previews.py` has a separate opening-cover renderer, `make_intro_frame`, which loads the existing `file_000000005e3481f4996a7ee6217f56c6.png` template and writes the surah title and ayah range onto its blank plaques.
- The surah title currently uses `f"سورة {surah_name}"`; the source of `surah_name` must be audited before adding reviewed diacritics.

## Safe implementation proposal
1. Add a dedicated cover catalog; do not mix covers with backgrounds or audio.
2. Keep the existing template as an immutable, permanently eligible cover entry.
3. Add new cover variants only after the original image has been visually inspected and the user approves each design.
4. Every catalog entry must have a stable unique ID, asset path, approval flag, and validation status. Unapproved or missing assets are never selected.
5. Select from eligible covers while excluding the last-used cover ID. Persist the last-used ID atomically in the same durable state mechanism already used by the daily workflow; inspect that mechanism before implementation.
6. If multiple approved covers exist, never choose the immediately previous cover. If only one approved cover exists, use that one. If the previous ID is missing or invalid, select a valid approved cover.
7. Keep the selection deterministic for a single video build/retry so retries do not silently change the chosen cover.
8. Do not change cover insertion timing, intro duration/fade, audio start, video dimensions, Telegram delivery, cron, or publishing.

## Required tests before production use
- Existing cover remains in catalog and its bytes are not modified.
- A -> B and B -> A transitions are allowed; A -> A is rejected when B is eligible.
- Rotation survives process restarts and workflow reruns using durable last-used state.
- A failed/missing new cover falls back only to the original approved cover.
- All cover variants pass 1080x1920 checks and Arabic RAQM shaping.
- Surah title diacritics are checked against a reviewed 114-surah mapping, not generated heuristically.
- Audio stream, cover timing, and output dimensions are unchanged in a regression render.

## Progress recorded on the preview branch
- Added src/cover_rotation.py: a dedicated selector for approved cover assets, with atomic persistent state and an idempotent video key so a render retry reuses its chosen cover.
- Added tests/test_cover_rotation.py: tests for consecutive-repeat prevention, retry idempotency, persisted state, original-only fallback, ignoring unapproved variants, and fail-closed behavior if the original is missing.
- These files are not imported by or wired into the production renderer, scheduler, Telegram workflow, or publishing path.
- The tests have been authored but have not yet been executed in the repository's CI/runtime.

## Remaining before any integration
1. Visually inspect the existing original cover asset; binary image retrieval through the connected GitHub file reader is unavailable.
2. Prepare and review new variants based on that original; do not invent or approve them automatically.
3. Add the catalog and reviewed Arabic surah-name mapping.
4. Run the new tests and a regression render, then ask for approval before wiring the selector into production.

Production code and the production branch remain untouched.
