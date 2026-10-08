# rev0327 mission kernel

## Heart of the mission

AI-EDU exists to strengthen human learning and human educational judgment. The useful unit is a
teacher/tutor move after a learner attempt: a better question, misconception check, or smallest-useful
hint that helps the learner explain or transfer without AI.

Governance stays in service of that interaction. It should prevent answer leakage, hidden authority,
privacy failures, unsupported claims, and learner harm. It should not turn artifact completion into a
substitute for a real educator cycle.

## Current correction

Rev0327 fixes the highest-risk field-path defect left after rev0326: the readiness gate treated
post-cycle aggregate rows and an owner decision as prerequisites for being “ready.” That could block
the first real cycle or pressure an operator to fabricate post-cycle completion.

The readiness path now separates three moments:

1. `NOT_READY`: entry fields are incomplete, unsafe, missing, or still placeholder-based.
2. `READY_FOR_LOCAL_CYCLE_NOT_EVIDENCE`: discovery, intervention identity, participation, fallback,
   privacy, and protected-review fields are complete enough for one locally approved teacher/tutor
   feasibility cycle.
3. `READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE`: after the cycle, aggregate rows, stop-trigger counts,
   and one bounded decision are coherent enough for a human local owner review stop record.

Synthetic dry-runs remain `SYNTHETIC_READY_SMOKE_NOT_EVIDENCE` and must be discarded before real work.

## What remains risky

No revision can manufacture the missing relationship. A real teacher/tutor owner still has to select
the concept, approve participation and fallback rules, run a bounded local cycle if allowed, and record
only aggregate local observations. `FT-0181` also remains open until a genuine owner-evidence route is
used or blocked.

## Revision gate

The next revision should ship only for one of these reasons: a real field event, a reproducible defect,
a material deletion/compression, or evidence that changes a decision. New registries, schemas,
validators, and recorder families remain disfavored unless they repair an observed failure.

## Boundary

Rev0327 improves the action path and refactors a stale template/tool seam. It does not contact an
owner, run a teacher/tutor cycle, accept `SRC2+` evidence, prove learning, or close `FT-0181`.
