# Event chronology firebreak refactor — rev0333

## Problem

The teacher/tutor packet could be internally coherent while temporally impossible. A human owner-review
stop could be recorded before the dated session rows it claimed to review, and a result receipt could
summarize that packet because previous checks focused on completeness, suppression, and hash drift.

## Change

The hot-path tools now apply one chronology rule:

```text
D1-baseline <= D2-D3-coach-use <= D4-transfer <= owner review <= result receipt
```

The release archive records only aggregate dates and phase bounds, not learner schedules, names, raw
work, protected facts, or local contact routes.

## Implementation

- `tools/score_teacher_tutor_micro_pilot_readiness.py` now validates ISO `SESSION-LOG.csv` dates and
  phase order as a post-cycle check.
- Fresh entry packets still reach `READY_FOR_LOCAL_CYCLE_NOT_EVIDENCE` after owner-plan completion
  because blank post-cycle rows are not treated as attempted results.
- Partially filled post-cycle payloads with missing/invalid/misordered dates become `NOT_READY` for
  repair instead of falling back to entry-ready.
- `tools/record_teacher_tutor_micro_pilot_owner_review.py` refuses review dates earlier than the latest
  session row.
- `tools/record_teacher_tutor_micro_pilot_result.py` refuses result dates earlier than owner review or
  the latest session row.
- Generated owner plans, checklists, and run sheets now name the chronology rule directly.

## Boundary

This is not evidence acceptance. It only prevents the local feasibility record from contradicting the
time order of the human events it claims to summarize.
