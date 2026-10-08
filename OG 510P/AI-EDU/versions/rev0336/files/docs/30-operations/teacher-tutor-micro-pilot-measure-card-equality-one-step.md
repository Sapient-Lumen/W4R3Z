# Teacher/tutor micro-pilot measure card: equality one-step

This is an optional worked concept kit. Use it only when a local teacher or tutor selects this construct; packet availability is not evidence of local need. The cycle is feasibility/usability only, and its transfer count is descriptive rather than an efficacy estimate.

It exists to
make the run executable, not to prove that the service works. Use it with
[`teacher-tutor-micro-pilot-run-card.md`](teacher-tutor-micro-pilot-run-card.md) and the scratch
packet created by `make micro-pilot-pack CONCEPT_KIT=equality-one-step`; then use the readiness gate before treating the packet as locally reviewable.

## Construct

Learners preserve equality while solving one-step equations and can explain why the same inverse
operation must be applied to both sides.

The coach may help the teacher/tutor select instructional moves after a learner attempt. The coach
must not solve the item for the learner, score the learner, write a record, infer ability or
protected status, or replace the teacher/tutor explanation.

## Local setup

Use one owner, one learner group selected locally, one ordinary non-AI fallback, and one no-AI
transfer or explanation check. Keep the group description local and de-identified. Do not place names,
raw work, screenshots, recordings, gradebook rows, protected facts, small cells, prompts, or chat
transcripts into the archive.

Recommended packet command:

```bash
make micro-pilot-pack \
  CONCEPT_CODE=equality-one-step \
  CONCEPT="solving one-step equations by preserving equality" \
  SETTING="one teacher-owned practice group selected locally" \
  DATE_RANGE="owner-selected two-session window" \
  TRANSFER_CHECK="one no-AI explanation of why the same operation preserves equality" \
  CONCEPT_KIT=equality-one-step \
  OVERWRITE=1
```

## Baseline before coach use

Use two or three locally selected items like these, or curriculum-matched equivalents. The teacher or
tutor scores locally and records only aggregate counts/minutes.

| Item family | What the owner checks | Archive capture |
|---|---|---|
| `x + 5 = 12` | Can the learner name the inverse operation and preserve equality? | aggregate attempt and success count |
| `3x = 15` | Can the learner explain why division applies to both sides? | aggregate attempt and explanation count |
| `x / 4 = 6` | Can the learner solve and explain the equality-preserving move? | aggregate attempt and success count |

## Coach-use move menu

After a learner attempt, the owner may ask for exactly three teacher-reviewable moves:

1. one probing question about what must stay equal;
2. one misconception check;
3. one smallest-useful hint that does not reveal the next answer step.

The teacher/tutor must choose, edit, or reject the move before use.

## Misconception watchlist

- The equals sign is treated as an answer cue rather than a balance relation.
- Only one side of the equation is changed.
- The inverse operation is selected procedurally but not explained conceptually.
- A hint is copied as an answer.
- The learner can complete a familiar item but cannot explain the operation on a changed item.

## No-AI transfer check

Use a changed number form, variable symbol, or equation shape. Ask for the solution and one sentence
explaining why the inverse operation preserves equality. The owner records only aggregate transfer or
explanation counts.


## Readiness scoring

After the local owner completes the plan, aggregate session rows, final readout, and decision memo, run:

```bash
make micro-pilot-readiness \
  PACKET=scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/equality-one-step \
  WRITE=1
```

The scorecard is scratch-only. It should say `NOT_READY` for a blank generated packet and only move to
`READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE` when local aggregate rows and the bounded owner decision are present.

## Continue / stop threshold

Consider one more bounded feasibility cycle only if transfer is not obviously worse, answer leakage is zero,
access/fallback remains intact, and owner review/correction time is not worse than ordinary support.
Stop or repeat narrower if the coach leaks final steps, worsens access, increases workload, or makes
the evidence about task completion rather than transferable understanding.

## Claim boundary

This measure card and any scratch packet it creates are not evidence. They do not prove learning,
safety, access, workload, compliance, scale readiness, service authority, public-claim support, or
`FT-0181` closure.

## Next-action routing

After packet generation, run `make micro-pilot-next PACKET=scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/equality-one-step WRITE=1` before interpreting readiness output. The router is local preparation support only and does not convert this measure card into evidence.
