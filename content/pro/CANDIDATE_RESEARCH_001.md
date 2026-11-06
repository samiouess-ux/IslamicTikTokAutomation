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
- Tirmidhi page gives Abu 'Isa's grading: `hadith hasan`.
- Sunnah.com listing for Abu Dawud 5068 displays grading `Sahih (Al-Albani)`.
- These are separate grading statements by named authorities. Preserve them separately; do not collapse them into a single unqualified grade.

### Exact Arabic variants — do not merge

**Sunan Abi Dawud 5068** (as displayed on its source page):
- Morning: `اللَّهُمَّ بِكَ أَصْبَحْنَا وَبِكَ أَمْسَيْنَا وَبِكَ نَحْيَا وَبِكَ نَمُوتُ وَإِلَيْكَ النُّشُورُ`
- Evening: `اللَّهُمَّ بِكَ أَمْسَيْنَا وَبِكَ نَحْيَا وَبِكَ نَمُوتُ وَإِلَيْكَ النُّشُورُ`

**Jami` at-Tirmidhi 3391** (as displayed on its source page):
- Morning: `اللَّهُمَّ بِكَ أَصْبَحْنَا وَبِكَ أَمْسَيْنَا وَبِكَ نَحْيَا وَبِكَ نَمُوتُ وَإِلَيْكَ الْمَصِيرُ`
- Evening: `اللَّهُمَّ بِكَ أَمْسَيْنَا وَبِكَ أَصْبَحْنَا وَبِكَ نَحْيَا وَبِكَ نَمُوتُ وَإِلَيْكَ النُّشُورُ`

**Riyad as-Salihin 1453** displays a further wording difference in its Arabic text for the evening ending (`وَإِلَيْكَ الْمَصِيرُ`) and does not reproduce the added `وَبِكَ أَصْبَحْنَا` phrase in the evening line. This is why the production candidate must be tied to one exact collection/reference and must not mix variants.

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
