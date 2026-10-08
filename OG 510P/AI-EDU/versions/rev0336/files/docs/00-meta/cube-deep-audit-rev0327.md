# rev0327 deep audit: action-path risk and template/tool drift

## Executive finding

Rev0326 correctly re-centered the mission on field learning, but one critical mechanics problem
remained: the readiness gate could still make the first legitimate teacher/tutor cycle harder to run.
It required post-cycle aggregate rows and a bounded owner decision before the packet could leave
`NOT_READY`. That was backwards for the first field event.

This is the same failure pattern the cube has shown before: internal completion criteria can become
more real than the human event they are supposed to support.

## Highest-risk defect fixed

The scorer now distinguishes:

- entry readiness for one locally approved feasibility cycle;
- post-cycle readiness for human owner review;
- synthetic rehearsal readiness that must be discarded before real work.

The new entry status is `READY_FOR_LOCAL_CYCLE_NOT_EVIDENCE`. It is deliberately weaker than
`READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE`: it means the owner plan has enough local discovery,
intervention identity, participation, fallback, privacy, and protected-review information to run one
bounded cycle if local rules permit. It does not mean a cycle happened.

## Refactor audit

The owner-plan template was stale. The generator wrote a richer owner plan, but the template stayed as
a thin placeholder shell. That is wasteful because future maintainers could edit or trust the wrong
surface. Rev0327 aligns the template with the generated packet and makes the generator check for core
markers before packet creation.

No new schema, registry, or validator family was added. The change modifies an existing hot-path
scorer, router, generator guard, and operational docs.

## Remaining severe risks

1. **No real field partner.** The project still needs a named local owner or a documented route block.
2. **No actual cycle.** Entry readiness is not evidence; a real teacher/tutor interaction still has to
   happen under local approval.
3. **No accepted owner evidence.** `FT-0181` remains queued until the owner-evidence rail receives a
   legitimate send/block/return path.
4. **Compression debt remains.** The archive remains much larger than the active mission requires;
   future work should delete or merge unused control-tail surfaces rather than add new ones.

## Practical next move

Generate the field handoff. Complete the owner plan from a real local need. Rerun readiness. If the
score becomes `READY_FOR_LOCAL_CYCLE_NOT_EVIDENCE`, stop writing and run one bounded local feasibility
cycle if approved. Only after that should the aggregate rows and owner-review stop become available.

## Boundary

This audit is not evidence of learning, access, safety, workload, effectiveness, or compliance. It is a
repair to the action path so the next human event is less likely to be blocked by the cube itself.
