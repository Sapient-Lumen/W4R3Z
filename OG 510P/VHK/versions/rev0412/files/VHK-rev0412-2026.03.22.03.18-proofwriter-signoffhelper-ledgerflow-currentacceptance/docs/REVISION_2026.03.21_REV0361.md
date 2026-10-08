# Revision 0361 — per-macro author loop now carries execution posture

This revision tightens the flagship private-LLM lane for the i3/X11 warm runtime.

## Added

- `macro-author-loop-json` now includes `execution.runtime_posture`
- `macro-author-loop-json` now includes `execution.runtime_signoff`
- `macro-author-loop-json` now includes `execution.dispatch_history`
- `macro-author-loop-json` now exposes `llm_handoff.execution_review_inputs`

## Tightened

- runtime signoff normalization is now shared between the per-macro author loop and the project-wide runtime board
- the per-macro LLM handoff no longer requires reopening the runtime board just to answer direct-run vs checked-dispatch vs inspect-history

## Why

Once a private LLM has already chosen one macro, the safest next decision is usually execution posture: edit more, run directly, inspect dispatch blockers, or use the checked warm-runtime path.

That decision should come from the same per-macro surface that already carries source, recorder evidence, and latest-run context.
