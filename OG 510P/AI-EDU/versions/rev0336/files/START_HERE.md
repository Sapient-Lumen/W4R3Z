# Start here

`rev0336` is in source-result hashlink mode. The riskiest missing event is still a real teacher/tutor cycle, but the next technical failure mode was allowing a `repeat-narrower` or `continue-bounded` decision to produce a generic fresh packet with no link to the prior non-evidence result.

## First action

```bash
make field-handoff-bundle OVERWRITE=1
```

Open `scratch/field-handoff/rev0336/FIELD-HANDOFF.md`, then open:

1. `scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept/DISCOVERY-FIRST-CONTACT.md`
2. `scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept/OWNER-PLAN.md`
3. `scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept/CYCLE-RUN-SHEET.md`
4. `scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept/OWNER-DECISION-MEMO.md`

Use the discovery card to select the local problem, the owner plan to complete entry fields, and the run sheet to conduct at most one locally approved feasibility/usability cycle.

## Entry-ready path

```bash
make micro-pilot-readiness PACKET=scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept WRITE=1
make micro-pilot-next PACKET=scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept WRITE=1
```

`READY_FOR_LOCAL_CYCLE_NOT_EVIDENCE` means the completed local plan can support exactly one approved cycle. It is not proof that a cycle happened, not post-cycle owner-review readiness, not `SRC2+`, and not `FT-0181` closure.

## After a non-retire result

A `repeat-narrower` or `continue-bounded` result must now create a source-linked fresh packet:

```bash
make micro-pilot-followthrough-pack \
  SOURCE_RESULT=scratch/.../MICRO-PILOT-RESULT.json \
  CONFIRM=source-result-read-for-local-followthrough-not-evidence \
  CONCEPT_CODE=<owner-selected-safe-slug> \
  CONCEPT="<de-identified next concept or narrowing constraint>" \
  SETTING="<fresh bounded local setting>" \
  DATE_RANGE="<fresh bounded window>" \
  TRANSFER_CHECK="<new no-AI transfer/explanation check>" \
  OVERWRITE=1
```

The new packet writes `FOLLOWTHROUGH-SOURCE-RESULT.json` and readiness checks that the source result still exists, still hashes to the recorded digest, and is a non-evidence repeat/continue result. The source link does not copy owner seed text, learner counts, protected facts, local observations, or prior result details.

## Secondary owner-evidence rail

Keep the owner-evidence rail visible but secondary:

```bash
make owner-field-work OVERWRITE=1
make owner-field-report OVERWRITE=1
make owner-field-next CSV=/path/to/real-owner-return.csv OUT=scratch/field/ft0181/ft0181-field-next-action/returned-owner-reply
```

Use it only for a real bounded send, route block, or returned owner packet.

## Read next

1. [`docs/00-meta/mission-kernel-rev0336.md`](docs/00-meta/mission-kernel-rev0336.md)
2. [`docs/00-meta/cube-deep-audit-rev0336.md`](docs/00-meta/cube-deep-audit-rev0336.md)
3. [`docs/00-meta/field-execution-risk-burndown-rev0336.md`](docs/00-meta/field-execution-risk-burndown-rev0336.md)
4. [`docs/00-meta/source-result-hashlink-freshpacket-refactor-rev0336.md`](docs/00-meta/source-result-hashlink-freshpacket-refactor-rev0336.md)
5. [`docs/30-operations/teacher-tutor-micro-pilot-readiness-gate.md`](docs/30-operations/teacher-tutor-micro-pilot-readiness-gate.md)
6. [`docs/30-operations/teacher-tutor-micro-pilot-next-action-router.md`](docs/30-operations/teacher-tutor-micro-pilot-next-action-router.md)

## Boundary

No real pilot, real owner contact, route block, accepted `SRC2+` evidence, owner-reviewed local result, or `FT-0181` closure exists. Scratch packets are not evidence. Keep security payloads, credentials, names, raw learner material, exact small cells, protected facts, transcripts, screenshots, gradebook rows, final-readout small-cell free text, and patched run-defining prompts out of every release artifact.
