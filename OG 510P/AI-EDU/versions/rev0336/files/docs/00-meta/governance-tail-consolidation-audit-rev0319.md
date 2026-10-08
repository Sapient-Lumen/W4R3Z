# rev0319 governance-tail consolidation audit

## Audit target

Rev0319 audits hot-path burden rather than adding another tail inventory. The key question is whether
an operator can act without rereading the branch-history tail.

## Measured state

- Operations markdown: 79 files, about 103,603 words.
- Meta markdown: 264 files, about 142,227 words.
- All markdown: 518 files, about 652,323 words.

The archive can preserve this material as history, but it is wasteful if it becomes the path to the
next action.

## Refactor performed

The re-entry path now drops the current governance-tail audit from first-read startup and adds the
concrete equality-one-step measure card. The current startup path should answer: what is the mission,
what is blocked, what gets sent, and what gets run.

## Current hot path

1. `START_HERE.md`
2. `README.md`
3. `AGENTS.md`
4. `docs/00-meta/charter.md`
5. `docs/00-meta/mission-kernel-rev0319.md`
6. `docs/00-meta/cube-deep-audit-rev0319.md`
7. `docs/00-meta/field-execution-risk-burndown-rev0319.md`
8. `docs/30-operations/ft0181-owner-contact-send-pack.md`
9. `docs/30-operations/teacher-tutor-micro-pilot-run-card.md`
10. `docs/30-operations/teacher-tutor-micro-pilot-measure-card-equality-one-step.md`

## Deletion trigger

After a real owner packet or real micro-pilot readout, review any surface that was not used. Delete,
merge, or cold-park it unless it changed a decision, blocked a concrete harm, or shortened execution.

## Claim boundary

This audit does not delete historical obligations, accept evidence, authorize service use, upgrade
public claims, or close `FT-0181`.
