# Quran Video Pro — Development Log

This log is the durable record for work on `feature/quran-video-pro`.
Production branch `feature/telegram-review-notifications` is out of scope and must not be modified by Pro work.

## 2026-11-05 — Baseline audit (documentation only)

### Scope and baseline
- Repository: `samiouess-ux/IslamicTikTokAutomation`
- Branch: `feature/quran-video-pro`
- Audited baseline commit: `7d8c21ae0b7d57ae7b66a28885ebf3ecb299ecdb`
- Latest known review run: [Actions run #106](https://github.com/samiouess-ux/IslamicTikTokAutomation/actions/runs/41945437319)
- This entry records a source inspection. No application code was changed as part of this audit.
- No GitHub Actions workflow was started or rerun during this audit. No Telegram message was sent during this audit. No production branch, Cron, publishing setting, or secret was changed.

### User-approved product goal
Build a genuinely professional Quran video engine whose opening captures attention respectfully, whose visual storytelling and motion are polished, and whose Quran text, translation, recitation, timing, and rights provenance are protected. Each output remains review-only; automatic TikTok publishing stays disabled.

### Confirmed implementation gaps
1. **Visual templates are not meaningfully distinct yet.**
   - `src/render_video_scenes.py` supports four template names, but all use the same overall composition and fixed title/text/verse-number positions.
   - The main differences are accent colors, border geometry, and verse-number decoration. This explains why the last two comparison videos looked almost the same.
   - `tests/test_quran_visual_templates.py` only verifies that the generated PNGs are pixel-different; it does not measure meaningful layout, hierarchy, motion, readability, or perceived design quality.

2. **The agreed opening cover is not implemented in the active Pro renderer.**
   - `DESIGN_SPEC.md` requires a Quran cover showing “القرآن الكريم”, the surah name, and the exact ayah range, targeting 1.6 seconds with a 0.4-second alpha fade.
   - The inspected render path creates verse overlays and starts the selected audio at the beginning; no separate cover-scene implementation or cover timing/fade was found in `src/render_video_scenes.py`.

3. **The video duration limit conflicts with the design specification.**
   - `DESIGN_SPEC.md` sets a maximum of 40 seconds for the final MP4 and audio.
   - `src/render_video_scenes.py` and the active workflow's ffprobe gate currently allow up to 65 seconds.
   - This must be reconciled before calling the renderer compliant with the approved spec.

4. **Approved background candidates are not active rotation assets.**
   - `data/background_candidates.json` contains four user-approved candidates and explicitly says they await integration.
   - `src/asset_rotation.py` requires `rights_verified=true` and normalized `source_url`/`asset_url` fields; the candidate records currently use a different shape and do not satisfy those checks as written.
   - The active manifest renderer takes one background URL from the manifest; the inspected workflow does not select and rotate among the four candidate records.
   - Therefore the existence of four candidate records is not proof that background rotation is operational.

5. **Full-Quran reference coverage is not yet enabled.**
   - `data/reference/quran_text_uthmani.json` currently contains only six reviewed verse entries: Ash-Sharh 94:5-6 and Al-Ikhlas 112:1-4.
   - The catalog builders can prepare 6,236-verse Arabic and Saheeh translation candidate corpora, but the Arabic candidate is explicitly unreviewed and blocked from rendering; translation rights and verse-level review are also still required.
   - The audio inventory workflow contains checks for 6,236 mapped official archive entries, but this does not by itself approve every exact recording for every passage.
   - Full-Quran rotation must remain fail-closed until all required text, translation, audio, and rights gates are met.

6. **The last comparison was not a fair test of content/audio improvement.**
   - Workflow input `compare_designs=true` deliberately renders two visual overrides from the same manifest, same selected audio, and same downloaded background.
   - Identical audio in that comparison is expected; it was intended to isolate visual changes.
   - The actual failure was that the visual changes were too small to create a professional, clearly distinguishable result.

### Confirmed safeguards to preserve
- Exact Arabic text comparison is Unicode-exact; no normalization, rewriting, or automatic correction.
- Arabic rendering requires RAQM and a known Arabic font.
- The renderer requires approved/user-approved background metadata and documented audio approval/rights.
- No music; no synthetic Quran recitation; no public reciter attribution.
- Quran verses must remain ordered and complete; never cut a verse mid-recitation.
- Captions and each video require user review.
- Automatic publishing must remain disabled.

### Required development sequence
1. Design a genuinely new visual direction and define objective acceptance checks for composition, typography, legibility, and motion.
2. Implement the approved opening cover and its timing/fade without inserting silence or changing the recitation stream.
3. Integrate the four already-reviewed background candidates into a rights-aware, deterministic rotation; fail closed if no eligible asset exists.
4. Resolve the 40-second specification versus 65-second implementation mismatch.
5. Strengthen visual regression tests so they test layout and required design elements, not merely pixel inequality.
6. Expand Quran text/translation/audio coverage only through explicit source, rights, exact-match, and human-review gates.
7. Produce a review video, inspect the actual MP4 and audio/video metadata, and record the user's visual/audio feedback before accepting the result.

### Validation status for this audit
- Source inspection: completed for the files listed above.
- Unit tests: not run during this audit.
- Render: not run during this audit.
- Telegram delivery: not run during this audit.
- Production branch / Cron / TikTok publishing: untouched.

### Change-control rules
- All Pro implementation commits go only to `feature/quran-video-pro`.
- Do not merge Pro into production without explicit user approval.
- Do not trigger Actions or send Telegram review videos without explicit user approval for that run.
- Log every code change, test, workflow run, artifact/delivery result, failure, and approval in this file.


## 2026-11-05 — Development milestone 1: opening cover and duration gate

### Changes committed to Pro
- `src/render_video_scenes.py`
  - Added a separate 1080×1920 Arabic opening-cover overlay.
  - Cover includes “القرآن الكريم”, the manifest's Arabic surah name, and the exact selected verse/range rendered with Arabic-Indic numerals.
  - Cover uses a restrained translucent dark panel and gold framing.
  - Cover fades out from 1.2s to 1.6s.
  - The existing audio remains mapped from input 1 without a new delay, inserted silence, speed change, or audio filter.
  - Renderer maximum duration is now 40 seconds.
- `.github/workflows/render-manifest-video.yml`
  - MP4 technical validation now rejects durations above 40 seconds, matching the design specification.
- `tests/test_quran_visual_templates.py`
  - Added checks for opening-cover creation, 1080×1920 dimensions, required timing constants, and refusal when the Arabic surah name is missing.

### Commits
- Renderer: `eac695aee000a1e22dcbf4501ae437d408501866`
- Workflow duration gate: `04eb08b0f7159c6f839a90f142a6b71e47d800e8`
- Opening-cover tests: `30130543311fa96c14b0e03d928058388175fe85`

### Validation and limitations
- GitHub source re-fetch confirmed the renderer contains the new cover path and 40-second cap, the workflow contains the 40-second MP4 gate, and the tests contain the new cover checks.
- Unit tests have **not** been executed.
- No render or MP4 visual/audio inspection has been performed.
- No GitHub Actions run was triggered.
- No Telegram message was sent.
- The cover's appearance, alpha fade behavior, and exact synchronization must be verified in a real rendered review MP4 before this milestone can be accepted.
- This milestone does not yet implement the four-background rotation or a genuinely redesigned verse-screen layout.

### Current status
- Code committed to `feature/quran-video-pro` only.
- Production branch, Cron, secrets, and publishing configuration remain untouched.
- Milestone status: **implemented, awaiting automated and visual validation**.
