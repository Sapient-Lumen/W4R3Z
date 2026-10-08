# REV0355 — thin-dispatch catalog for the warm runtime

This revision makes thin-dispatch an explicit project-wide control-plane surface for the flagship i3/X11 resident-runtime lane.

## What changed

- added `vhk macro-dispatch-catalog-json <project>`
- generated `bin/macro_dispatch_catalog_json.sh` in the flagship warm-runtime stack
- taught `stack_state_json.sh` / `stack_state.sh` to carry dispatch-catalog runtime, summary, and primary-macro truth
- extended `control-plane.json` so a private LLM can discover the dispatch catalog as a runtime-snapshot / dispatch surface
- tightened docs so the project-wide control-plane story is now: author queue, runtime board, acceptance ledger, dispatch catalog, then per-macro author loop

## Why this cut matters

Before this revision, VHK could answer two adjacent questions separately:

- which macro deserves attention next
- which macros look warm-runtime-ready

But it still made the resident service or a private LLM reconstruct the practical thin-dispatch contract by hand. The new dispatch catalog closes that gap by saying, at project scope:

- which bus event currently owns thin dispatch
- what minimal payload is worth emitting for each macro
- which generated wrapper owns that contract
- which explicit blocker still prevents cheap dispatch today

That keeps the resident-runtime path fast and observable without pretending every macro is equally ready for cheap bus emission.

## Validation

Focused tests cover:

- project-wide dispatch-catalog payload shape and bus-event override handling
- dispatch blockers for interactive, stale, candidate, and ready macros
- generated stack exposure of the dispatch-catalog helper and control-plane metadata
- fused stack-state propagation of dispatch-catalog runtime/summary/helper metadata
