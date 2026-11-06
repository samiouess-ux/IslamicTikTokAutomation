# Pro Dua & Adhkar Content Review

This directory is reserved for **Dua & Adhkar Pro** manifests only. Do not place Quran-video manifests here.

## Current status

There are no approved production manifests in this directory yet. A file is not eligible for rendering or delivery merely because it exists or passes the metadata validator.

## Required review for every item

Before adding an item to a production manifest, a human reviewer must verify and record:

1. **Exact Arabic wording** against the named primary source. Preserve the wording exactly; do not paraphrase or silently correct it.
2. **Source identity**: source name, stable HTTPS URL, and a precise reference (for example, collection/book/chapter/hadith number or Quran surah and ayah).
3. **Classification**: one of `quranic_dua`, `prophetic_dua`, `dhikr`, or `general_supplication`.
4. **Verification state**: set `verification_status: "verified"` only after checking the source itself.
5. **Human review**: set `human_reviewed: true` only after the exact Arabic text and its source reference have been checked.
6. **Prophetic duas**: include the exact hadith grading/authenticity reference and verify it from a reliable hadith source. Do not infer a grading.
7. **Media**: separately verify and record rights and approval for any spoken audio or background asset. The text source does not grant media reuse rights.
8. **Duration**: provide reviewed item timing that allows the final video to remain at or below 40 seconds.

## Manifest gates

The shared validator also requires structured `source`, `visual`, `audio`, and `publishing` objects. Every manifest must require user review and keep `auto_publish` disabled. The visual background must have a source URL and direct asset URL, with both approval and user-approval flags. Audio must be explicitly classified and music remains prohibited.

Dua/dhikr items require unique stable IDs, non-empty exact Arabic wording, a named HTTPS source, a precise source reference, verified status, human review, and an explicit classification. Prophetic duas additionally require a non-empty hadith grading field.

These are metadata and workflow gates, not proof that the religious text, interpretation, grading, or media rights are authentic. Human/source review remains mandatory.

## Do not

- Add guessed, AI-invented, paraphrased, or unsourced religious wording.
- Mark a candidate verified or human-reviewed just to make validation pass.
- Treat Quran production manifests from other directories as Pro dua/dhikr content.
- Render, send to Telegram, or publish to TikTok as part of content intake.
- Enable a delivery workflow until the library, offline tests, and workflow safety review are complete.

## Approval record

For each manifest, retain the source URL and exact reference alongside the review status. Any unresolved wording, source, grading, rights, or timing question means the item stays a candidate and must not be selected for production.
