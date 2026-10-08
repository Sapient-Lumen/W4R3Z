# rev0328 pedagogy-forward execution refactor

## Refactor target

The hot path should make the next human event easier than the next internal artifact. Rev0328 changes
field execution from “generate bundle, inspect multiple rails” to “generate bundle, open the discovery
card, ask one educator.”

## Operator sequence

1. Run `make field-handoff-bundle OVERWRITE=1`.
2. Open `scratch/field-handoff/rev0328/FIELD-HANDOFF.md`.
3. Open `scratch/field-handoff/rev0328/teacher-tutor-micro-pilot/teacher-selected-concept/DISCOVERY-FIRST-CONTACT.md`.
4. Use the card for one 15-minute local teacher/tutor conversation.
5. If a viable route exists, complete `OWNER-PLAN.md` from that conversation and rerun readiness.
6. If readiness returns `READY_FOR_LOCAL_CYCLE_NOT_EVIDENCE`, run at most one locally approved
   feasibility cycle outside the archive.
7. Fill aggregate rows only after the cycle; stop at owner review before any result receipt.

## What changed

- The generated packet now includes `DISCOVERY-FIRST-CONTACT.md`.
- The field handoff opens the teacher/tutor discovery rail before the `FT-0181` owner rail.
- Startup docs no longer treat the owner-evidence rail as co-first work.
- The owner-evidence rail remains available only for real send, block, or returned material.

## What did not change

No new validator, schema, registry, or claim rule was added. Entry readiness remains not-evidence.
Synthetic dry-runs remain disposable. The `FT-0181` evidence boundary remains live.

## Boundary

This refactor sends nothing, runs no cycle, accepts no evidence, records no owner review, proves no
outcome, and closes nothing.
