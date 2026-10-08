# Teacher/tutor feasibility next-action router

The router turns packet state into one bounded scratch-local action. It prevents a blank packet, an
entry-ready packet, or a synthetic rehearsal from being mistaken for completed field progress.

## Entry

```bash
make field-handoff-bundle OVERWRITE=1
make micro-pilot-next \
  PACKET=scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept \
  WRITE=1
```

Running `make micro-pilot-next WRITE=1` without `PACKET` uses the same revision-scoped default path.

## Decisions

| Router decision | Trigger | Operator action |
|---|---|---|
| `PREPARE_PACKET` | no packet exists | generate the discovery-first `teacher-selected-concept` packet |
| `COMPLETE_ENTRY_PACKET_OR_OPTIONAL_DRY_RUN_COPY` | readiness is `NOT_READY` | complete entry fields; synthetic rehearsal only belongs on a disposable scratch packet |
| `RUN_ONE_LOCAL_CYCLE_THEN_RERUN_READINESS` | readiness is `READY_FOR_LOCAL_CYCLE_NOT_EVIDENCE` | run one locally approved feasibility cycle outside the archive, then fill aggregate rows and rerun readiness |
| `DISCARD_SYNTHETIC_AND_REGENERATE` | synthetic packet passes | delete/regenerate before real owner work |
| `LOCAL_OWNER_REVIEW_STOP` | a real non-dry post-cycle packet is complete | record review only after a human local owner actually reviews it |
| `RECORD_LOCAL_RESULT_RECEIPT_STOP` | review stop exists | record a descriptive local result receipt, not evidence |
| `FOLLOW_LOCAL_RESULT_DECISION_NOT_EVIDENCE` | result receipt exists | follow the receipt decision map: retire stops; repeat/continue require a fresh packet; escalation requires a separate future accepted route |

## Optional equality worked kit

Use equality one step only when the local owner selects it:

```bash
make micro-pilot-pack \
  CONCEPT_CODE=equality-one-step \
  CONCEPT="solving one-step equations by preserving equality" \
  SETTING="one teacher-owned practice group selected locally" \
  DATE_RANGE="owner-selected bounded window" \
  TRANSFER_CHECK="one no-AI explanation of why the same operation preserves equality" \
  CONCEPT_KIT=equality-one-step \
  OVERWRITE=1
```

## Boundary

The router does not run a cycle, estimate efficacy, contact an owner, accept evidence, authorize use,
support public claims, or close `FT-0181`.

## rev0336 result-decision boundary (prior)

For any post-cycle packet, `SESSION-LOG.csv` dates must be ISO and ordered baseline <= coach-use <= transfer. Owner review and result recording must occur after the latest session row. After a result receipt exists, the router reads `decision_followthrough`: `retire` stops, `repeat-narrower` and `continue-bounded` start only through a fresh packet, and `escalate-to-pilot-review` emits no evidence-import command. This boundary is a hot-path execution check, not evidence acceptance.

## rev0336 fresh-packet command boundary

For post-result `repeat-narrower` or `continue-bounded`, the router emits a placeholder command that must be filled from the owner decision memo's follow-through seed. It no longer emits the broad default `teacher-selected-concept` command for result follow-through, because that could create generic repetition without owner substance.

## rev0336 source-result hashlink boundary

For post-result `repeat-narrower` or `continue-bounded`, the router now emits `make micro-pilot-followthrough-pack` with `SOURCE_RESULT=<prior MICRO-PILOT-RESULT.json>` and `CONFIRM=source-result-read-for-local-followthrough-not-evidence`. The command must still be filled with the owner-selected next concept/constraint, setting, window, and transfer check.

The source result is read only to validate that a fresh local packet is allowed. The new packet carries a hash link to the prior non-evidence result; it does not copy seed text, learner counts, local observations, or protected facts, and it cannot pool cycles or support claims.
