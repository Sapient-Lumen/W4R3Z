# Re-entry navigation map

Current revision: `rev0336`

## First read

1. `docs/00-meta/mission-kernel-rev0336.md`
2. `docs/00-meta/cube-deep-audit-rev0336.md`
3. `docs/00-meta/field-execution-risk-burndown-rev0336.md`
4. `docs/00-meta/source-result-hashlink-freshpacket-refactor-rev0336.md`
5. `START_HERE.md`
6. `AGENTS.md`

## Current hot path

Generate the field handoff and open the teacher/tutor lane first:

```bash
make field-handoff-bundle OVERWRITE=1
```

Open `scratch/field-handoff/rev0336/FIELD-HANDOFF.md`, then `scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept/DISCOVERY-FIRST-CONTACT.md`, `OWNER-PLAN.md`, `CYCLE-RUN-SHEET.md`, and `OWNER-DECISION-MEMO.md`.

## Why this route

The first valuable external event is still one real teacher/tutor discovery conversation and one locally approved feasibility/usability cycle. rev0336 adds a source-result hash-linked fresh-packet so a later `repeat-narrower`, `continue-bounded`, or `escalate-to-pilot-review` decision cannot become generic repetition or implicit evidence.

## Secondary rail

Use the `FT-0181` owner-evidence rail only when there is a real send, real route block, or returned owner packet:

```bash
make owner-field-work OVERWRITE=1
make owner-field-report OVERWRITE=1
make owner-field-next CSV=/path/to/real-owner-return.csv OUT=scratch/field/ft0181/ft0181-field-next-action/returned-owner-reply
```

## Do not start here

Do not start with branch history, public-claim lexicons, release examples, or completed followthrough records. They remain constraints and audit surfaces, not the mission.
