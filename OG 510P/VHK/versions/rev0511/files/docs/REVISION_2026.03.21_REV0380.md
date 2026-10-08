# REV0380 — stack state lifts selected macro review-queue slice

## What changed

- `stack_state_json.sh` now lifts the author-queue-selected macro's active review-queue slice into `primary_macro_review_queue`.
- The fused payload preserves whether the selected macro is present in the queue, which queue buckets it belongs to, the ordered review item, and the review command to run next.
- `sources.helpers.macro_review_queue_json` now mirrors selected-macro queue facts for fast triage.
- `stack_state.sh` now prints the selected macro's review-queue presence, categories, and review command.

## Why this matters

The resident control plane already carried the selected macro's gate, latest run, contract, author loop, recorder truth, entrypoints, board slices, acceptance, and latest dispatch receipt. But the caller still had to rescan project-wide review-queue buckets to answer whether the selected macro was actively queued for recorder or segment cleanup. This revision keeps that answer in the same one-read stack snapshot.

## Tests

- Added focused generated-stack coverage for `primary_macro_review_queue`.
- Re-ran the key stack-state snapshot tests around the selected macro's acceptance, latest dispatch, board slices, and entrypoints.
