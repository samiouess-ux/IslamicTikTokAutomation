# Saad Al-Ghamdi isolated audio validation log

Branch: `experiment/saad-ghamdi-audio-source`

Scope: diagnostic-only experiment. No production audio, active reciter, Cron, publishing, rights flags, or approval gates are changed.

## Confirmed result — Run 19

- Run: https://github.com/samiouess-ux/IslamicTikTokAutomation/actions/runs/41923318165
- Head commit: `d4eae5498e20518a0ef1d8fb900d8ff7d169d34d`
- Conclusion: success.
- Matched-source timestamp bounds check: PASS.
- Acoustic energy screening: 101 ayah intervals across surahs 1, 38, and 114.
- Four conservative listening candidates:
  - Al-Fatihah 1:1 — 0–2.720 s; first-window RMS -34.01 dBFS, last-window RMS -50.49 dBFS, silent windows 7.14%.
  - Al-Fatihah 1:5 — 16.495–21.380 s; first-window RMS -26.67 dBFS, last-window RMS -50.78 dBFS, silent windows 2.04%.
  - Sad 38:1 — 0–8.105 s; first-window RMS -24.43 dBFS, last-window RMS -50.03 dBFS, silent windows 2.44%.
  - Sad 38:88 — 869.465–875.900 s; first-window RMS -17.07 dBFS, last-window RMS -50.27 dBFS, silent windows 3.08%.

These are screening flags, not confirmed timing or recitation defects. Low energy near a clip boundary may be a natural pause or decay. Human listening has not yet been completed. The check validates interval structure and source-audio bounds, not word-level acoustic alignment.

## Workflow cleanup

Commit `ad117d1585f5cc78387f9ba3897f14c6abf75686` removes an unnecessary `requests` installation; the diagnostic uses Python's standard-library `urllib`.

## Current run

- Run 20: https://github.com/samiouess-ux/IslamicTikTokAutomation/actions/runs/41923533600
- Head commit: `ad117d1585f5cc78387f9ba3897f14c6abf75686`
- Last observed state: diagnostic step in progress; final result pending.

## Rights and production guardrails

QUA timing/metadata licensing does not establish rights to the audio recordings. Do not use this recording in production or commercial publishing until the recording rights are independently verified. The production reciter remains Maher Al-Muaiqly; this experiment does not authorize a reciter change.


## Confirmed result — Run 20

- Run: https://github.com/samiouess-ux/IslamicTikTokAutomation/actions/runs/41923533600
- Head commit: `ad117d1585f5cc78387f9ba3897f14c6abf75686`
- Conclusion: success after removing the unused `requests` installation.
- Source package SHA256 verified: `17a0230828fd14b63b52ffc9191cdd43b110eeb73121fe8f7c288a9917cf528e`.
- Riwayah/channel: Hafs an Asim / tarteel.
- Canonical verse keys: 6,236; malformed rows: 0; declared coverage matches.
- Canonical start ordering: PASS across all 114 surahs.
- Audio decode and source-bounds checks: PASS for surahs 1, 38, and 114.
- Acoustic screening: 101 ayah intervals; same four conservative candidates as Run 19.
- Human listening remains outstanding; no word-level acoustic alignment claim is made.


## Confirmed result — Run 21 (all-surah interval consistency audit)

- Run: https://github.com/samiouess-ux/IslamicTikTokAutomation/actions/runs/41924033735
- Diagnostic commit: `c8738402a2ffd9fa94dc99ff6a8a2bf218fd3642`
- Conclusion: success.
- Canonical start ordering: PASS across 114 surahs.
- Canonical interval end-order issues: 0.
- Adjacent canonical ayah interval overlaps: 0.
- Source-audio bounds and decode checks: PASS for sampled surahs 1, 38, and 114.
- Acoustic screening remains 101 intervals with four conservative edge-energy flags.
- This structural audit does not establish word-level acoustic alignment or replace human listening.


## Confirmed result — Run 23 (canonical surah and ayah sequence checks)

- Run: https://github.com/samiouess-ux/IslamicTikTokAutomation/actions/runs/41924205068
- Diagnostic commit: `60cf3babd19ba134867dd25faadfc60f47c328d7`
- Conclusion: success.
- `CANONICAL_SURAH_SEQUENCE_CHECK PASS`: all 114 surah identifiers are present contiguously.
- `CANONICAL_AYAH_NUMBER_CONTINUITY_CHECK PASS`: within each surah, canonical ayah numbers begin at 1 and contain no gaps.
- Interval end-order issues: 0; adjacent interval overlaps: 0.
- Source-audio bounds/decode checks: PASS for sampled surahs 1, 38, and 114.
- Acoustic screening: 101 ayah intervals, four conservative low-edge-energy review flags (1:1, 1:5, 38:1, 38:88).
- These checks establish canonical key/interval structure and source bounds, not acoustic word-level alignment; the four flags still require human listening.
