# Revision 0362 - embed checked-dispatch verdict into the per-macro author loop

This revision tightens the flagship private-LLM lane for the i3/X11 warm runtime again.

## What changed

- `macro-author-loop-json` now includes `execution.dispatch_gate`
- the embedded dispatch-gate view carries:
  - `decision`
  - `dispatch_readiness`
  - `dispatch_contract`
  - `force_override`
- checked-dispatch projection logic is now shared so:
  - `macro-dispatch-catalog-json`
  - `macro-dispatch-gate-json`
  - `macro-author-loop-json`
  all derive from the same readiness/decision contract
- runtime-board and author-queue builders now reuse precomputed dispatch-history context when they call the per-macro author loop

## Why this matters

Once a private LLM has already selected a macro, the next question is not “which helper should I open now?” but “what should I do now?”

That answer now lives directly in the per-macro handoff:

- dispatch now through the checked warm-runtime lane
- direct-run because the macro is interactive
- inspect latest replay proof before dispatch
- stabilize recorder / cleanup debt before dispatch
- override deliberately, with an explicit paper trail

That keeps the flagship i3/X11 lane centered on one session-bound warm runtime, one thin dispatch path, and one per-macro authoring surface instead of forcing extra helper hops.
