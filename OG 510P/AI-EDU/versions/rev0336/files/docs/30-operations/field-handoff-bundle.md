# Field handoff bundle

State: `SCRATCH_LOCAL_PREPARATION_NOT_EVIDENCE`

```bash
make field-handoff-bundle OVERWRITE=1
```

The bundle prepares two separate rails under `scratch/field-handoff/rev0336/`:

1. the primary teacher/tutor packet at `scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept`;
2. a secondary bounded `FT-0181` owner request and route-block fallback.

## Human discovery before packet completion

Open `DISCOVERY-FIRST-CONTACT.md` first, then `OWNER-PLAN.md`, then `CYCLE-RUN-SHEET.md`. Its purpose is to secure one real teacher/tutor conversation,
name a local instructional friction point, and choose the concept before the owner plan is completed.
Do not start with the owner-evidence rail unless a real accountable owner route exists.

The default packet deliberately does not choose the curriculum problem. A local teacher or tutor must
complete the problem statement, concept, reason to act now, baseline, transfer check, ordinary
fallback, learner participation rule, tool/model/version, numeric privacy threshold, protected local
equity-review route, and post-cycle local attestation route.

The equality one-step kit is available only when locally selected:

```bash
make field-handoff-bundle CONCEPT_CODE=equality-one-step \
  CONCEPT="solving one-step equations by preserving equality" \
  TRANSFER_CHECK="one no-AI explanation of why the same operation preserves equality" \
  CONCEPT_KIT=equality-one-step OVERWRITE=1
```

## Readiness and evaluation class

The readiness scorer should move through `NOT_READY`, then `READY_FOR_LOCAL_CYCLE_NOT_EVIDENCE` after
entry fields are complete and `CYCLE-RUN-SHEET.md` is present, and only later `READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE` after a real
cycle has aggregate rows, a bounded decision, and safe suppression handling for any later result receipt.

The first cycle is feasibility and usability only and must be bounded to one local cycle. It asks whether the human can use the coach, at
least one move is instructionally useful, burden is acceptable, and no obvious answer leakage, access,
fallback, or transfer harm appears. It does not estimate a learning effect, and any local result receipt must mask counts/rates below the configured threshold.

## Boundary

The command sends nothing, runs no pilot, records no human review, accepts no evidence, and creates no
service authority or `FT-0181` closure. Scratch is excluded from release packaging.

## rev0332 provenance reminder (prior)

The micro-pilot rail is not only privacy-gated; it is now run-definition-gated. If `COACH-PROMPT.md`,
`RUN-CHECKLIST.md`, `MEASURE-CARD.md`, `DISCOVERY-FIRST-CONTACT.md`, or `CYCLE-RUN-SHEET.md` needs
editing, regenerate the scratch packet before the owner plan is treated as ready.

## rev0333 event chronology boundary (prior)

For any post-cycle packet, `SESSION-LOG.csv` dates must be ISO and ordered baseline <= coach-use <= transfer. Owner review and result recording must occur after the latest session row. This boundary is a hot-path execution check, not evidence acceptance.

## rev0334 result-decision boundary (prior)

After a local result receipt exists, follow only the bounded decision map: `retire` stops; `repeat-narrower` and `continue-bounded` require a fresh packet and cannot be pooled as evidence; `escalate-to-pilot-review` requires a separate future accepted route and emits no evidence-import command.

## rev0336 handoff addition

After any local result, non-retire follow-through requires a de-identified owner seed and a fresh packet. Operators must not use a generic repeat packet or pool local cycles as evidence.

## rev0336 follow-through note

The first handoff remains discovery-first. If a later local result says `repeat-narrower` or `continue-bounded`, operators should not rerun the default packet generator. They should use `make micro-pilot-followthrough-pack` with the prior local `MICRO-PILOT-RESULT.json` so the next packet is source-linked, non-evidence, and fresh rather than generic repetition.
