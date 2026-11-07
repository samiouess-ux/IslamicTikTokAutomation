# Candidate Research — Initial Qur'anic Dua and Morning/Evening Dhikr

**Status: research candidates only. Not approved for production.**

This file records source comparison. It is not a renderer manifest and must not be loaded by the Pro orchestrator.

## Candidate QD-001 — Qur'anic supplication, Al-Baqarah 2:201

- Classification: `quranic_dua`
- Primary source: Quran.com, Al-Baqarah 2:201
- URL: https://quran.com/al-baqarah/201?translations=131
- Exact reference: Qur'an 2:201
- Arabic as displayed by the opened source:
  `وَمِنۡهُم مَّن يَقُولُ رَبَّنَآ ءَاتِنَا فِي ٱلدُّنۡيَا حَسَنَةٗ وَفِي ٱلۡأٓخِرَةِ حَسَنَةٗ وَقِنَا عَذَابَ ٱلنَّارِ`
- Source page displays the Arabic verse and exact reference 2:201, plus its immediate context (2:200–202).
- Research status: `source_checked_candidate`
- Human exact-text review: pending.
- Context review: pending.
- Media/audio rights: not reviewed.
- Production status: blocked; do not create a manifest yet.

## Candidate PD-001 — Morning/evening supplication attributed to Abu Hurairah

- Classification: `prophetic_dua` / morning-evening adhkar (final classification to be decided by reviewer)
- Companion narrator: Abu Hurairah (as identified by the cited collections)
- Primary collection references:
  - Sunan Abi Dawud 5068 — https://sunnah.com/abudawud/43/296
  - Jami` at-Tirmidhi 3391 — https://sunnah.com/tirmidhi/48/22
- Additional compilation reference: Riyad as-Salihin 1453, Book 15, Hadith 46 — https://sunnah.com/riyadussalihin/15
- The Arabic matn on the Tirmidhi 3391 page includes Abu 'Isa's statement: `هَذَا حَدِيثٌ حَسَنٌ` ("this is a hasan hadith"). Separately, the page's displayed Grade metadata says `Sahih (Darussalam)`. Preserve these as two distinct attributions; do not conflate Abu 'Isa's in-text statement with the site's displayed grade.
- Sunnah.com listing for Abu Dawud 5068 displays grading `Sahih (Al-Albani)`.
- These are separate grading statements by named authorities. Preserve them separately; do not collapse them into a single unqualified grade.

### Exact Arabic variants — do not merge

**Sunan Abi Dawud 5068** (as displayed on its source page):
- Morning: `اللَّهُمَّ بِكَ أَصْبَحْنَا وَبِكَ أَمْسَيْنَا وَبِكَ نَحْيَا وَبِكَ نَمُوتُ وَإِلَيْكَ النُّشُورُ`
- Evening: `اللَّهُمَّ بِكَ أَمْسَيْنَا وَبِكَ نَحْيَا وَبِكَ نَمُوتُ وَإِلَيْكَ النُّشُورُ`

**Jami` at-Tirmidhi 3391** (as displayed on its source page):
- Morning: `اللَّهُمَّ بِكَ أَصْبَحْنَا وَبِكَ أَمْسَيْنَا وَبِكَ نَحْيَا وَبِكَ نَمُوتُ وَإِلَيْكَ الْمَصِيرُ`
- Evening: `اللَّهُمَّ بِكَ أَمْسَيْنَا وَبِكَ أَصْبَحْنَا وَبِكَ نَحْيَا وَبِكَ نَمُوتُ وَإِلَيْكَ النُّشُورُ`

**Riyad as-Salihin 1453** displays a further wording difference in its Arabic text for the evening ending (`وَإِلَيْكَ الْمَصِيرُ`) and does not reproduce the added `وَبِكَ أَصْبَحْنَا` phrase in the evening line. Its Arabic text also attributes the report to Abu Dawud and at-Tirmidhi and states that they said it is hasan. This is why the production candidate must be tied to one exact collection/reference and must not mix variants.

- Research status: `source_checked_candidate_with_variant_conflict`
- Human review of chain, exact source wording, and selection of a single reference/version: pending.
- Grading review: pending; record Tirmidhi's `hasan` and Al-Albani's `sahih` for Abu Dawud separately with their own source references.
- Context/timing review: pending.
- Media/audio rights: not reviewed.
- Production status: blocked; do not create a manifest yet.

## Review findings / next actions

1. Human reviewer must choose whether to assess Abu Dawud 5068 or Tirmidhi 3391 as the intended source record; do not synthesize a hybrid wording.
2. Recheck Arabic letter-by-letter against the selected collection page and retain its displayed variant exactly.
3. Record grading authority and source-specific grading without implying all scholars give one unanimous grade.
4. Complete the review template, including media rights and duration, before a separate production manifest is considered.
5. No render, Telegram delivery, or TikTok publishing is authorized by this research note.


## Verification addendum — 2026-11-06

A second direct page inspection clarified the grading display on Jami' at-Tirmidhi 3391:
- The Arabic matn itself includes Abu 'Isa's statement `قَالَ أَبُو عِيسَى هَذَا حَدِيثٌ حَسَنٌ`.
- The separate Sunnah.com Grade metadata field displays `Sahih (Darussalam)`.
- These are different attributions/fields and must both be recorded exactly; the earlier shorthand that only mentioned Abu 'Isa's hasan statement was incomplete.
- Direct page checks also confirmed the exact Arabic matn and source reference for Abu Dawud 5068, the Tirmidhi 3391 wording, and the variant in Riyad as-Salihin 1453. See the linked source pages in the candidate entry.

This correction does not approve the hadith. Human selection of one exact source/version and independent review remain pending.


## Candidate PD-002 — Sayyid al-Istighfar (Chief supplication for forgiveness)

- Classification: `prophetic_dua` / istighfar.
- Companion narrator: Shaddad bin Aws (as identified by the source).
- Primary collection: Sahih al-Bukhari 6306, Book 80, Hadith 3.
- Source URL: https://sunnah.com/bukhari:6306
- Source page displays the Arabic matn, narrator, collection/reference, and the report's day/night recitation context.
- Arabic text as displayed by the source:
  `سَيِّدُ الاِسْتِغْفَارِ أَنْ تَقُولَ اللَّهُمَّ أَنْتَ رَبِّي، لاَ إِلَهَ إِلاَّ أَنْتَ، خَلَقْتَنِي وَأَنَا عَبْدُكَ، وَأَنَا عَلَى عَهْدِكَ وَوَعْدِكَ مَا اسْتَطَعْتُ، أَعُوذُ بِكَ مِنْ شَرِّ مَا صَنَعْتُ، أَبُوءُ لَكَ بِنِعْمَتِكَ عَلَىَّ وَأَبُوءُ لَكَ بِذَنْبِي، فَاغْفِرْ لِي، فَإِنَّهُ لاَ يَغْفِرُ الذُّنُوبَ إِلاَّ أَنْتَ`
- The source continues with the stated virtue for one who recites it during the day or night with certainty and dies before the corresponding period ends. Do not omit or paraphrase this context as though it were part of the supplication itself.
- Research status: `source_checked_candidate`.
- Human exact-text/context review: pending.
- Duration suitability under the 40-second cap: not tested; Arabic plus English may require careful timing or a separate format decision. Do not truncate the dua to force a fit.
- Media/audio rights: not reviewed.
- Production status: blocked; do not create a manifest yet.


### QD-001 source corroboration addendum — 2026-11-07

A further source check compared the Quran.com verse page with the Quranic Arabic Corpus verse 2:201 page. Both identify the item as Al-Baqarah 2:201 and display the Saheeh/Sahih International English rendering: “But among them is he who says, ‘Our Lord, give us in this world [that which is] good and in the Hereafter [that which is] good and protect us from the punishment of the Fire.’” The Quranic Arabic Corpus page also provides parallel translations and word-by-word morphology. This corroborates the reference and the intended English translation; it does not replace the still-pending human letter-by-letter Arabic review, context review, or the separate media-rights process.

Sources checked:
- Quran.com: https://quran.com/al-baqarah/201?translations=131
- Quranic Arabic Corpus: https://corpus.quran.com/translation.jsp?chapter=2&verse=201
- Legacy Quran.com source rendering: https://legacy.quran.com/2/201

Status remains `source_checked_candidate`; no manifest, approval flag, render, or delivery is authorized by this addendum.


## Background candidate MK-001 — Sunrise landscape (visual sample reviewed)

- Exact Mixkit item page: https://mixkit.co/free-stock-video/beautiful-sunrise-landscape-1944/
- Asset page explicitly displayed the Mixkit Stock Video Free License and commercial/personal-use wording at intake time; applicable terms: https://mixkit.co/license/modal/videoFree/ and https://mixkit.co/terms/.
- Automated single-item intake completed on 2026-11-07 at 20:17:10 UTC. Exact download: 16,515,983 bytes; MIME `video/mp4`; H.264; 1280×720; 24000/1001 fps; 54.804750 seconds; SHA-256 `9bbf623aa42493925e612659cf90a6e5a15762e22f0ba1f92c179265173fe27d`.
- Nine sampled frames were visually inspected from the exact downloaded file. They show a calm sunrise over distant mountain silhouettes and a broad open landscape; no people, logos, or obvious artwork are visible in the sampled frames. The scene appears visually plausible for QD-001's broad request for good in this world and the Hereafter. The sun and mountain line remain within the central crop area, but the source is horizontal 16:9 and will require a 9:16 crop; the foreground is comparatively dark. Full-frame review is still required before any final use.
- Durable sample contact sheet: `content/pro/review_previews/MK-001-contact-sheet.jpg` (nine frames, timestamp labels). This is a visual review aid, not the licensed video file or a rights record.
- Status: `visual_sample_reviewed_candidate_only`. No actual MP4 is retained in the repository; it was downloaded in the ephemeral CI runner only. No creator/rights-owner identity has been established in the per-asset record; full-file third-party review, worldwide use/monetization scope, and human rights decision remain pending. Do not create an approved rights record or use this candidate in a render yet.


## Background candidate MK-002 — Morning forest (intake pending)

- Exact Mixkit item page: https://mixkit.co/free-stock-video/forest-during-the-morning-3012/
- The page currently describes morning sunlight through a forest and explicitly labels the download for commercial or personal use under the Mixkit Stock Video Free License. Page-listed metadata: 24 seconds, 60 fps, 6.76 MB; available listed resolutions are 1080×720 and 1920×1080.
- Proposed semantic fit: a separate renewal/quiet-morning visual direction for a future Sayyid al-Istighfar candidate, rather than reusing MK-001's open sunrise/mountain landscape. This is only a proposed mapping; the exact visual and framing must be inspected after download.
- Intake workflow `.github/workflows/pro-background-intake-mk002.yml` was added, exact-branch restricted, and triggered. At the time of this note, the initial run and corrected run were still in progress/queued; no downloaded file, hash, contact sheet, or visual review is claimed yet.
- Status: `source_page_checked_candidate_only`. No media file, rights JSON, manifest, approval flag, render, or delivery has been created.


### MK-002 visual sample review — 2026-11-07

- Exact Mixkit item page: https://mixkit.co/free-stock-video/forest-during-the-morning-3012/; page displayed the Mixkit Stock Video Free License and commercial/personal-use wording.
- Single-item CI intake run `42410443005` succeeded. Exact download: 7,083,251 bytes; MIME `video/mp4`; H.264; 1280×720; 60 fps; duration 23.550000 seconds; SHA-256 `6a39a371443cbed05f27a6a213e8905318186ac5086424d8e6a37f1d6ad1d462`.
- Nine sampled frames were visually inspected. They show a sunlit woodland with strong shafts of morning light between trees; no people, logos, or obvious artwork are visible in those sampled frames. This provides a clearly distinct visual direction from MK-001 and may fit a quiet renewal/istighfar theme. The source is horizontal 16:9; a central 9:16 crop focuses on trunks and sun rays and may be visually busy, so the text overlay needs a calm/darkened legibility treatment. Full-file inspection remains outstanding.
- Durable sample contact sheet: `content/pro/review_previews/MK-002-contact-sheet.jpg`.
- Status: `visual_sample_reviewed_candidate_only`. The MP4 existed only in the ephemeral CI runner and is not stored in the repository. No creator/rights-owner record, full-file third-party review, worldwide rights decision, approved rights JSON, or user approval exists. Do not use in a render yet.
