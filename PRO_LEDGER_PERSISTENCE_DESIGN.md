# Pro Delivery Ledger — Cross-Run Persistence Design

Status: **design approved for implementation planning; not implemented or enabled**  
Target branch: `feature/quran-video-pro` only.

## Why local JSON is insufficient
`src/pro_delivery_ledger.py` safely updates a JSON file on one runner, but GitHub-hosted runners are ephemeral. A fresh workflow run does not inherit the previous runner's filesystem. Therefore a local `data/pro_delivery_ledger.json` alone cannot prevent a manifest from being sent again on a later run.

## Chosen persistence model
Persist the ledger as a normal, non-secret file committed to the Pro branch, at `data/pro_delivery_ledger.json`. Use the workflow's checked-out branch and the repository's standard Git commit/push path. Do not use Git database/tree/ref APIs or bypass GitHub branch controls.

The Pro workflow must:
- Be `workflow_dispatch` only; no `schedule`, `push`, `pull_request`, or external trigger.
- Reject unless both `github.ref` and the checked-out branch are exactly `feature/quran-video-pro`.
- Use a fixed `concurrency.group` for all Pro ledger operations and `cancel-in-progress: false`.
- Grant only the permissions needed for checkout and a normal commit/push (`contents: write`); do not expose production secrets or use production workflow files.
- Fail closed if ledger restore, validation, commit, or push fails.

## Required two-phase delivery protocol
The current sender reserves and sends in one process. That is not sufficient for cross-run safety because the reservation must reach the branch **before** the Telegram request.

1. Checkout the exact Pro branch and load/validate the committed ledger. A missing ledger is initialized only on the first controlled run.
2. Validate the selected manifest and rendered MP4. No Telegram request is allowed during preflight.
3. Reserve the stable manifest ID locally. Commit and push that reservation to the Pro branch. If the push fails, stop before Telegram.
4. Only after the reservation commit is confirmed on the branch, call Telegram once. The sender must verify that the existing reservation belongs to the current workflow run and is still in `reserved` state; it must not create a second reservation.
5. On a valid Telegram `message_id`, transition to `delivered` and commit/push the updated ledger.
6. On timeout, transport failure, malformed response, or any ambiguous result, transition to `uncertain` and commit/push. Never retry automatically.
7. If the post-send ledger push fails, the already-persisted `reserved` entry remains a duplicate-send block. Stop and require human reconciliation; never resend automatically.
8. Release a `reserved` or `uncertain` entry only through an explicit human reconciliation after checking the Telegram destination and confirming it was not delivered.

## Why artifact-only persistence is not selected
Workflow artifacts are immutable per upload and expire according to repository retention. A robust "latest ledger" design would need reliable cross-run artifact discovery, ordering, and race handling. A fixed branch-committed ledger plus serialized runs is simpler to audit and does not silently expire.

## Remaining implementation work
- Add an explicit sender mode that accepts only a pre-existing reservation matching the current run ID; preserve the existing unit-testable local mode if useful.
- Add a small workflow-safe persistence helper that validates the expected branch and commits only the ledger file; reject empty or unrelated changes.
- Add a dormant manual-only workflow with the branch guard, concurrency, minimal permissions, and the reserve/persist/send/persist sequence.
- Add tests for: no send when reservation persistence fails; no send for wrong run/state; successful confirmed delivery; uncertain outcome; post-send persistence failure; and duplicate blocking across a fresh process after reloading the committed ledger.
- Verify workflow YAML and run offline tests before any workflow dispatch.

## Current safety state
- No Pro workflow exists yet.
- No verified Pro dua/dhikr manifests or approved content library exist yet.
- Sender is not connected to a workflow.
- No Telegram secrets were read or changed; no workflow was dispatched; no render or Telegram send occurred.
- The production Quran branch, its workflow, Cron, secrets, and bot route are out of scope and must remain untouched.
