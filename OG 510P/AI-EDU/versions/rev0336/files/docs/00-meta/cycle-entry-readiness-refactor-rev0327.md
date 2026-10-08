# rev0327 cycle-entry readiness refactor

## Finding

The previous readiness gate answered the wrong operational question. It asked whether a packet had a
completed session log, final readout, clear stop-trigger counts, and a bounded owner decision. That is
useful after a cycle, but it is not the same as readiness to start one.

This made the riskiest path fragile: a maintainer could either see a legitimate pre-cycle packet as
`NOT_READY` forever, or try to complete post-cycle fields before any teacher/tutor interaction had
actually happened.

## Change

`tools/score_teacher_tutor_micro_pilot_readiness.py` now classifies checks by stage:

- `entry`: packet files, prepared/not-evidence boundary, feasibility/no-efficacy boundary, absence of
  raw/protected markers, and completed owner plan fields;
- `post_cycle`: baseline/coach/transfer aggregate rows, eight final readout rows, zero stop-trigger
  counts, and one bounded owner decision.

A packet with all entry checks passing and post-cycle rows still blank returns
`READY_FOR_LOCAL_CYCLE_NOT_EVIDENCE`. The next-action router now routes that state to one local cycle
and a later readiness rerun, not to owner-review recording.

## Template refactor

`templates/teacher-tutor-micro-pilot-owner-plan.md` had become a stale short skeleton while the packet
generator emitted the real field requirements. The template now mirrors the intervention identity,
participation/access, protected local review, and method-boundary fields. The pack generator refuses
to proceed if the template loses those core markers again.

## What changed for the operator

The operator no longer has to choose between blocking a complete pre-cycle plan and pretending the
post-cycle readout exists. The new sequence is:

1. complete the owner plan from a real local need;
2. score readiness;
3. if the score is `READY_FOR_LOCAL_CYCLE_NOT_EVIDENCE`, run at most one approved local feasibility
   cycle outside the archive;
4. fill aggregate post-cycle rows only after the event;
5. rerun readiness before any owner-review stop record.

## Boundary

This is an action-path refactor, not a field event. It creates no evidence, no owner review, no result,
no service authority, and no public claim support.
