# Orchestrator handoff — IslamicTikTokAutomation

Last reviewed: 2026-10-31
Repository: https://github.com/samiouess-ux/IslamicTikTokAutomation
Default branch: `main`

> **Purpose:** This file is the mandatory handoff note for every ChatGPT/Codex/orchestrator session working on this repository. Read it before doing anything. It prevents lost context, repeated work, contradictory decisions, and accidental changes to approved work.

## 1. Mandatory start-of-session protocol

Before planning or editing:

1. Read this file: `ORCHESTRATOR_HANDOFF.md`.
2. Read `PROJECT_STATUS.md` for the chronological project history, approvals, run IDs, artifact IDs, checksums, and research notes.
3. Read `DESIGN_SPEC.md` for the approved visual and content rules.
4. Inspect the current GitHub `main` tree and the exact files/workflows relevant to the task. Do not assume this handoff is newer than the repository.
5. Check the latest commits and workflow runs relevant to the task. Distinguish a successful old run from the current code state.
6. Tell the user briefly what is already done, what is not done, and the single next action. Do not ask the user to repeat information already recorded here.

**Never restart the project or recreate an existing feature before checking the repository.**

## 2. Product goal — do not change scope

Build a reliable Quran video production engine that prepares vertical videos and sends finished review files to the user's Telegram.

- Prepare Arabic and English versions.
- Content may be a complete surah, a consecutive verse range, or one verse.
- Use authentic Quran recitation, matched exactly to the displayed verses.
- Produce vertical MP4 videos, target 1080×1920 (9:16), 30 FPS.
- Rotate approved backgrounds and visual layouts to avoid repetitive output.
- Prepare Arabic and English captions naming the surah and exact verse range, with suitable hashtags.
- Send the finished video and its caption/review information to Telegram.
- The user downloads the video from Telegram and publishes it manually on TikTok.
- **Do not publish to TikTok automatically.** Do not add auto-publishing.
- The user works from a phone. Prefer GitHub/cloud workflows and do not make local PC commands, Codex desktop, or Android Studio prerequisites.

## 3. Non-negotiable content and safety rules

- Quran text must be exact and source-verified. Never generate or improvise Quran text.
- Translation must be traceable to the chosen source and checked against the relevant verse range.
- Audio must be authentic and have documented reuse permission for the exact recording.
- No music. Quran recitation only.
- Never cut a verse mid-word or mismatch audio and on-screen text.
- Do not show or mention the reciter's name in the video or public caption, per user preference. Keep audio source, rights, and provenance internally.
- Never invent a source, license, approval, test result, artifact, or workflow status.
- Every output remains for user review. A positive reaction to a design is not blanket approval to publish all future videos.
- Keep costs at zero or as low as possible; prefer free/open-source tools and GitHub-hosted cloud execution.

## 4. Verified project checkpoint (2026-10-31)

The following facts are recorded in `PROJECT_STATUS.md`; retain its detailed evidence and history there.

### Completed and user-confirmed
- A first test video for Surah Ash-Sharh 94:5–6 was rendered successfully by GitHub Actions.
- Render artifact: `ash-sharh-first-video-review`, artifact ID `13029197609`, from run `41165699435`.
- Output: `ash-sharh-94-5-6-review.mp4`, 1080×1920, 30 FPS.
- The exact official King Fahd Complex Maher Al-Muaiqly Hafs audio for verses 94:5–6 was extracted and joined. The user listened to that exact clip and confirmed the verse sequence is correct.
- The user approved the Mixkit waterfall background preview.
- The user approved the latest visual design preview from run `41170065024`, commit `fb519f49ff61c7feae83120b332bfaa28b2ae085`: large gold Arabic surah title in an ornate Islamic cartouche, separate ornamental gold verse-number medallions, unchanged white Quran text, and smaller English translation beneath.
- `DESIGN_SPEC.md` contains the visual rules. `content/first_video.json` records the first-video manifest and caption/background information.
- Arabic and English are the target languages; English replaced French.
- A draft manifest exists at `content/second_video_ash_sharh_94_1_8_draft.json`. Treat it as a draft until its text/audio/background and render are checked.

### Important existing repository files (verified in current main tree)
- `src/render_video.py`
- `src/render_video_scenes.py`
- `src/main.py`
- `src/validate_quran_reference.py`
- `src/validate_quran_text.py`
- `tests/test_validate_quran_reference.py`
- `tests/test_validate_quran_text.py`
- `content/first_video.json`
- `content/second_video_ash_sharh_94_1_8_draft.json`
- `DESIGN_SPEC.md`
- `PROJECT_STATUS.md`
- `requirements.txt`
- Multiple GitHub Actions workflows already exist under `.github/workflows/`, including render, audio extraction, background fetch, and cloud-runner checks. Inspect and reuse the correct workflow instead of creating duplicates.

## 5. What is NOT complete

Do not describe the project as a finished automatic engine. At this checkpoint:

- The first render proves a prototype can be generated; it does not prove a robust reusable production pipeline.
- Reusable content-manifest-driven production for all three content types (single verse, verse range, full surah) still needs end-to-end validation.
- Background/layout rotation needs to be completed and tested without breaking the approved design identity.
- Automated caption packaging and Telegram delivery are not yet confirmed complete.
- Duplicate prevention/history tracking is not yet confirmed complete.
- Scheduled production, failure notifications, and end-to-end unattended operation are not yet confirmed complete.
- No automatic TikTok publishing is wanted.

If any item above has since been completed, verify the code and successful workflow evidence first, then update this file and `PROJECT_STATUS.md`.

## 6. Next work — proceed incrementally

**First next task:** inspect the current renderer, manifests, tests, and existing render workflows. Determine the smallest safe change that makes the approved design reusable through a content manifest. Do not rewrite the renderer from scratch.

Suggested sequence:

1. Audit the existing renderer and workflow inputs/outputs. Identify what is already reusable.
2. Make one small change at a time to support manifest-driven rendering, preserving the approved design.
3. Test the existing first-video manifest as a regression test before trying another format.
4. Validate the second-video draft and its exact recitation before rendering it.
5. Add and test background/layout rotation using only reviewed/licensed assets.
6. Add reliable output packaging and bilingual caption files.
7. Implement Telegram delivery securely, then test with one approved video.
8. Add duplicate tracking, scheduled runs, and failure alerts only after the single-video pipeline works reliably.
9. Keep TikTok publishing manual.

Do not jump ahead to scheduling or automation while a single manifest-to-video-to-Telegram path is not proven.

## 7. Required update protocol after every work session

At the end of every meaningful task, the orchestrator must:

1. Commit repository changes with a clear, specific commit message.
2. Update `PROJECT_STATUS.md` with:
   - date;
   - exact files changed;
   - what changed and why;
   - tests/workflows actually run and their result;
   - run IDs, artifact IDs, and links/identifiers where available;
   - user approvals and what exactly was approved;
   - remaining blockers and the next concrete step.
3. Update this `ORCHESTRATOR_HANDOFF.md` if the current checkpoint, next task, architecture, or non-negotiable decisions changed.
4. Never mark a task complete based only on code being written. Require a successful test or workflow where applicable.
5. If work is blocked, record the precise blocker and stop rather than silently substituting an unverified source or workflow.
6. In the user-facing response, state what was actually changed, the commit, what was tested, and what remains.

**No silent progress claims. No lost decisions. No repeating completed work.**

## 8. User communication

- Explain in clear, concise Tunisian Arabic or simple French, depending on the user's language.
- Work step by step; avoid giving the user a long list of manual technical actions.
- The user expects the orchestrator to do repository work, not merely give instructions.
- Ask only for a decision that genuinely requires the user's approval (for example, choosing a new reciter or approving a specific video).
- Never ask the user to paste bot tokens, passwords, or other secrets into chat. Use GitHub Secrets or another secure secret store when needed, and explain only the non-secret setup steps.
