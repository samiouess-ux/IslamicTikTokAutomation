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
- The workflow assertion was updated to expect seven downloadable candidates and one unresolved Pixabay candidate.
- Next checks: actual download, `ffprobe`, 9:16 crop, Quran overlay preview and visual legibility review.
- No approval gate may be opened without explicit user approval.

## Correction to the earlier log
The earlier version overstated what had been verified. At that time, the direct URLs had not been captured and the catalog update had not succeeded. This entry records the later successful official-link redirect checks and catalog staging.

## CI record before staging
Run `42197745790`, commit `b16c5e032c01a168651bd2d724d04ee7fc92f6fa`, concluded `success`. It validated the eight source-only leads but did not download or probe their media.
