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


## Renderer geometry audit (code inspection only)
- The existing opening-cover function reads the immutable PNG asset directly and fits it to 1080x1920; the source asset itself is not edited.
- The surah title is centered at (540, 918), uses Arabic RAQM shaping, and is fitted to the available title width.
- The ayah range is centered at (540, 1148), uses Arabic RAQM shaping, and is fitted to the available range width.
- The current renderer passes the same approved moving-background frame as an argument, but `make_intro_frame` does not use that argument; the original cover asset remains the actual background.
- The current intro visibility is explicitly limited to 0.6 seconds, while the recitation audio is mapped from time zero. These settings are recorded for protection only and must not be changed as part of cover artwork work.
- This audit establishes text placement and technical constraints, not the visual appearance of the original PNG. No replacement artwork has been generated or approved, and the original asset has not been changed.

- Follow-up review found and fixed a rotation fairness bug: the selector previously chose the first eligible cover other than the last one, which could leave later designs unused. It now advances cyclically through the full approved catalog and wraps to the original after the final variant.
- Updated the rotation test to assert that all catalog entries are visited in order before wrapping, with no consecutive repeat. Tests are authored but still require execution in the repository runtime/CI.

- Added a bounded per-video assignment history (latest 500 video keys), so a delayed retry of an earlier video reuses its original cover even after later videos have advanced the rotation. If that assigned asset is no longer eligible, the selector fails closed rather than silently changing the cover for the same video.
- Added a delayed-retry regression test. The isolated GitHub Actions workflow ran the expanded test command successfully on commit 9c4ff6a843de8f13075369cd9da5e0fe3fa2592d; the workflow job was still completing its post-run cleanup when last checked.
