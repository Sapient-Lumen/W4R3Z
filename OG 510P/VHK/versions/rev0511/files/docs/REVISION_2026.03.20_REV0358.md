# Revision 0358 — per-macro replay board

This revision closes a warm-runtime control-plane gap that was still leaking through the project-wide latest-run helper.

## What changed

- added `vhk macro-replay-board-json <project>`
- generated stacks now expose `bin/macro_replay_board_json.sh`
- added per-macro replay posture ids:
  - `verified_recent`
  - `warning_recent`
  - `failed_recent`
  - `unverified`
- `macro-author-loop-json`, `macro-author-queue-json`, and `macro-runtime-board-json` now consume per-macro replay truth instead of inferring too much from the project's single latest run
- `stack_state_json.sh` / `stack_state.sh` now carry the replay board beside the author queue, runtime board, dispatch catalog, and latest-dispatch receipt lane

## Why it matters

The old shape let one macro's newest run blur another macro's replay posture. That is the wrong contract for a resident service and a private LLM that need to reason about many macros at once.

The replay board keeps replay evidence macro-scoped, which makes authoring triage, runtime posture, and checked dispatch safer and more explicit.
