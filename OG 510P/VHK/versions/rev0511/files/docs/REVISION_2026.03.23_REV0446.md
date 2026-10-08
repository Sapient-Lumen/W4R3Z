# Revision 0446 — 2026-03-23

## Theme

Make the direct per-macro author loop speak the same bounded LLM/operator contract as the selected-macro work ticket.

## What changed

- `macro_author_loop_json.sh <macro>` now emits a top-level `llm_workbench`.
- The per-macro execution lane now mirrors `execution.runtime_handoff` and `execution.latest_dispatch_handoff`.
- The workbench favors recorder-first authoring states before falling through to generic direct-run handoff, so new macros stay in the record -> cleanup -> replay lane instead of prematurely biasing toward ad hoc execution.
- The fused helper metadata now projects the direct author loop's workbench mode, recommended command, runtime handoff, and receipt-handoff summary fields.
- Tests now cover both first-pass recording guidance and current warm-receipt inspection on the direct per-macro lane.
- The stale older expectation that a merely historical receipt should still yield `dispatch_now` on the direct author loop has been removed; the control plane now honestly routes that case through stale-receipt inspection first.

## Why it matters

This closes an important surface mismatch in the resident-runtime product story. A private LLM can now open either:

- the selected macro from the fused stack, or
- a named macro directly

and still get the same bounded answers to four practical questions:

1. what should I inspect first?
2. what file should I edit?
3. how do I review/verify the change?
4. when should I checked-dispatch, direct-run, or stop?

That keeps the i3/X11-first control plane faster and less error-prone for the always-on resident service model.
