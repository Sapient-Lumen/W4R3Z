# rev0328 deep audit: human activation before administration

## Executive finding

After rev0327, the field path could finally distinguish entry readiness from post-cycle evidence. The
next severe risk was order-of-operations: the generated handoff and startup path still exposed the
owner-evidence/admin rail before the teacher/tutor discovery move. That pattern could recreate the
cube's old vice—doing more internal evidence choreography while the first educator conversation never
happens.

## Highest-risk seam corrected

The handoff generator now emits the primary pedagogical rail first and includes a scratch-only
`DISCOVERY-FIRST-CONTACT.md` file in each teacher/tutor packet. The card compresses the first human
ask to a 15-minute conversation and seven required local answers: problem/concept, baseline and
transfer check, participation/access, fallback, tool/version/configuration, privacy/protected review,
and stop triggers.

The secondary `FT-0181` owner-evidence rail remains available, but it is explicitly not the first thing
to open unless a real accountable owner route exists.

## Refactor audit

This revision changes an existing generator and active re-entry surfaces instead of adding validators,
schemas, ledgers, or recorder families. The refactor is deliberately operational:

- add one generated contact card to the scratch packet;
- reorder the field handoff so discovery precedes administration;
- update startup docs and operational run cards to point at the discovery card first;
- keep no-evidence, no-efficacy, no-closure boundaries intact.

## Remaining severe risks

1. **No real educator route.** The package makes the ask easier but does not contact anyone.
2. **No real local concept.** `teacher-selected-concept` is still a placeholder until a human replaces it.
3. **No actual cycle.** Readiness remains local preparation, not evidence.
4. **No owner evidence.** `FT-0181` is live and still needs a true owner route or block.
5. **Control-plane debt.** The archive remains much larger than the active path requires; future work
   should delete or merge unused control-tail material when safe.

## Practical next move

Generate the field handoff, open `DISCOVERY-FIRST-CONTACT.md`, and secure one educator conversation.
If the conversation yields a viable local problem, complete `OWNER-PLAN.md` and rerun readiness. If it
cannot yield a route, record nothing as evidence and stop expanding the cube.

## Boundary

This audit is not learning, access, safety, workload, fairness, compliance, or effectiveness evidence.
It is a hot-path refactor intended to make the next human event more likely.
