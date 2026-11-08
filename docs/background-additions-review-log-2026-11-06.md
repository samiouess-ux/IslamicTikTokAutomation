# Islamic background additions review log — 2026-11-06

## Scope and safety
- The four existing approved backgrounds were not edited.
- All eight additions remain review-only. Their `approved`, `user_approved`, and `download_verified` flags remain false.
- No new background was enabled for production.

## Verified official Pexels download redirects
For each of the following Pexels pages, the official **Free download** link was followed and its redirect target was captured. These are genuine Pexels-hosted MP4 URLs, not guessed filenames:

1. `pexels-islamic-dome-geometric-40564360` — `https://videos.pexels.com/video-files/40564360/17335023_2160_3840_60fps.mp4`
2. `pexels-modern-mosque-interior-35417846` — `https://videos.pexels.com/video-files/35417846/15005883_4320_7680_30fps.mp4`
3. `pexels-historic-mosque-stained-glass-30733250` — `https://videos.pexels.com/video-files/30733250/13147570_1080_1920_30fps.mp4`
4. `pexels-mosque-interior-calligraphy-19819594` — `https://videos.pexels.com/video-files/19819594/19819594-hd_1920_1080_50fps.mp4`
5. `pexels-illuminated-mosque-night-34928699` — `https://videos.pexels.com/video-files/34928699/14795106_2160_3840_25fps.mp4`
6. `pexels-moroccan-courtyard-tiles-34527220` — `https://videos.pexels.com/video-files/34527220/14628540_1080_1920_30fps.mp4`
7. `pexels-moroccan-courtyard-decor-32719926` — `https://videos.pexels.com/video-files/32719926/13948792_3840_2160_30fps.mp4`

The seven URLs are now staged in `data/background_additions_review.json` strictly for review-only processing. Capturing a redirect does not itself prove the MP4 bytes download or pass `ffprobe`; CI must establish that.

## Remaining source
- `pixabay-chain-dome-rock-131292` remains without a verified direct media URL.
- The workflow assertion was updated to expect seven downloadable candidates and one unresolved Pixabay candidate. A later workflow change adds Quran-overlay contact-sheet composition for those seven crops, reusing the actual rendered Quran overlay frame without downloading the clips a second time.
- Next checks: actual download, `ffprobe`, 9:16 crop, Quran overlay preview and visual legibility review.
- No approval gate may be opened without explicit user approval.

## Correction to the earlier log
The earlier version overstated what had been verified. At that time, the direct URLs had not been captured and the catalog update had not succeeded. This entry records the later successful official-link redirect checks and catalog staging.

## CI record before staging
Run `42197745790`, commit `b16c5e032c01a168651bd2d724d04ee7fc92f6fa`, concluded `success`. It validated the eight source-only leads but did not download or probe their media.

## Follow-up CI and regression-test correction — 2026-11-06
- Run `42204747258` (commit `174ec4d92fb7343b20eb57c872c2f9b0f57d8c8b`) failed before background downloading. The failure was in the review-catalog unit test: it still expected every `direct_video_url` to be null and required the exact policy phrase `No candidate is active`. The test had not been updated to reflect the seven officially captured Pexels URLs.
- Corrected `tests/test_background_additions_review.py` in commit `86c50a73b994a6403b5bc4bb801ef2054c59db89`: it now checks seven resolved Pexels URLs, the single unresolved Pixabay candidate, and that every candidate remains unverified, unapproved, and not user-approved. It also preserves the assertion that the original four approved backgrounds remain unchanged.
- Updated `data/background_additions_review.json` in commit `80b8fa88b44819cfea5d040ab228dfaa86a18592` to explicitly state `No candidate is active`, retaining the review-only and production-disabled policy.
- Run `42208508139` for the test correction was cancelled when the subsequent catalog commit triggered a newer run. This cancellation is not a test result.
- Latest run at the time of this log update: `42208519520`, commit `80b8fa88b44819cfea5d040ab228dfaa86a18592`, status `in_progress`. Setup and checkout succeeded; package installation was in progress. The corrected regression tests and seven-download/ffprobe/preview steps had not yet completed.
- No new background has been activated. The four existing production backgrounds remain untouched. Do not mark the seven videos as downloaded, probed, cropped, or visually approved until the latest CI artifacts and logs confirm each stage.



## Latest CI failure diagnosis and correction — 2026-11-06
- Run `42208519520` completed with failure in `test_prepare_accepts_eight_source_only_candidates_without_claiming_download`.
- The test intended to cover eight source-only candidates, but copied the live review catalog after seven Pexels direct URLs had been staged. It therefore attempted real downloads and hit the intentional 100 MiB per-file safety limit. The download limit is correct and was not weakened.
- Fixed the test fixture in commit `da5aa26c4a5c049d9178470b4ff3a161a08257d0` by removing `direct_video_url` only from its temporary in-test copy. The real review catalog and all seven official URLs remain unchanged.
- Run `42208519520` confirmed: archive inventory tests passed; existing four-background tests passed; eight-addition policy tests passed; actual-overlay composition test passed. The source-only fixture failed as described above. Download/probe and Quran overlay workflow steps were skipped because the test step failed.
- Next: verify the new CI run from commit `da5aa26`; only then report whether seven clips actually downloaded, passed `ffprobe`, produced 9:16 crops, and generated the Quran-overlay contact sheet. No production activation is authorized or performed.


## Corrected actual download failure — 2026-11-06
- Run 373 (`42208966090`, commit `da5aa26c4a5c049d9178470b4ff3a161a08257d0`) completed with failure during the real seven-clip download stage, not during the unit-test fixture. The four existing-background tests, eight-addition policy tests, and preview-composition unit tests all passed.
- The actual exception was `Background candidate exceeds the 100 MiB review-download limit.` The source catalog includes high-resolution Pexels MP4s (including 4K/60fps); the 100 MiB per-file ceiling was too restrictive for legitimate source media.
- Updated `src/prepare_background_review_previews.py` in commit `964900cfe3d55e0fd108cf6dfbece0245eda444c`: the bounded per-file ceiling is now 1 GiB, the error reports the candidate ID, and partial files are deleted on download failure. The bound remains finite; no download-size protection was removed.
- The source-only unit-test fixture is correctly isolated and all four relevant unit-test groups passed in run 373. The next CI run must establish whether each real MP4 downloads within the new cap, passes ffprobe, creates a 9:16 crop, and supports the Quran-overlay contact sheet.
- No new background has been enabled. The original four approved backgrounds remain unchanged; all eight additions remain review-only and require explicit user approval before activation.


## Workflow correction and checkpoint — 2026-11-08
- Commit `ad4b383deddbc3964c8e5ab0819da5425f4a50ea` updates `.github/workflows/review-background-candidates.yml` to test and process `data/background_additions_review.json` (the eight Islamic/Arabic additions), rather than the unrelated six-item nature batch.
- The workflow runs the catalog and preview safety tests, then downloads the seven staged Pexels clips under the existing finite 1 GiB per-file limit, probes them with `ffprobe`, extracts vertical 9:16 crops, and uploads a review-only artifact. The Pixabay item remains unresolved because it has no verified direct media URL.
- Important correction: this workflow invocation does **not** pass an actual Quran overlay frame to the preview script. It therefore produces background-only crop previews, not Quran-overlay legibility composites. The older note above describing a later workflow change that adds Quran-overlay composition is not true for this commit and must not be treated as completed.
- The workflow remains manual (`workflow_dispatch`). It has not been run from this commit, so no download, probe, crop, or artifact success is claimed.
- Production remains untouched: all eight additions are still unapproved and disabled; the four existing approved backgrounds are unchanged.


## Regression-test hardening — 2026-11-08
- Commit `24b078295dce6f7168cec5b27ee7bc771ac83f69` strengthens `tests/test_background_additions_review.py`: each of the seven resolved media URLs must use the official Pexels video host, and the original four approved background IDs must match the exact protected set.
- This is test-only hardening. It does not change either background catalog, download media, approve candidates, or activate production assets.
- The review workflow is still manual and no run from the latest workflow commit has been confirmed. The seven MP4s remain unverified until a real workflow run completes download, ffprobe, and preview generation.


## Failed preview cleanup hardening — 2026-11-08
- Commit `63811b7fdcf34eea1a8c4a0c226a64d1338d7a63` changes the review preparation path so any failure during download, ffprobe, or vertical-crop extraction removes both the downloaded MP4 and any partial crop for that candidate before raising a candidate-specific error.
- Commit `4eb7539ac67938b334b57533e5921f19de394adf` adds a regression test for cleanup after an ffprobe failure. The test context was corrected in commit `74b222b0ac2297a8a9fe1d1eba1ae01115a423a3` to use nested mocks cleanly.
- This is review-pipeline safety only. No catalog flags, approved backgrounds, or production behavior were changed.
- GitHub Actions showed an unrelated Quran audio inventory run queued for commit `4eb7539`; it is not the manual Islamic-background review workflow and does not validate these changes. The background review workflow remains unrun.
