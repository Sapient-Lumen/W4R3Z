# Teacher/tutor feasibility readiness gate

The readiness scorer distinguishes a generated packet, a cycle-entry-ready packet, a post-cycle
owner-review-ready packet, and a synthetic rehearsal. It is not an evidence grader.

## Default command

```bash
make micro-pilot-readiness \
  PACKET=scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept \
  WRITE=1
```

## Check stages

| Stage | Checks |
|---|---|
| `entry` | required files including `CYCLE-RUN-SHEET.md`, `PREPARED_NOT_RUN` / `NOT_EVIDENCE`, feasibility/no-efficacy method boundary, no forbidden raw/protected markers, completed owner plan |
| `post_cycle` | baseline/coach/transfer aggregate rows, ISO dated and ordered session rows, eight final readout rows, clear stop-trigger counts, one bounded owner decision |

## Status meanings

| Status | Meaning | Permitted next step |
|---|---|---|
| `NOT_READY` | entry fields are incomplete, unsafe, or missing | complete the owner plan or repair packet structure before learner-facing work |
| `READY_FOR_LOCAL_CYCLE_NOT_EVIDENCE` | entry checks pass while post-cycle rows are still blank or incomplete | use `CYCLE-RUN-SHEET.md` to run exactly one locally approved feasibility cycle, then fill aggregate rows and rerun readiness |
| `SYNTHETIC_READY_SMOKE_NOT_EVIDENCE` | the dry-run harness exercised the positive path | discard or regenerate before real work |
| `READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE` | a non-dry post-cycle packet is coherent enough for human local review | record the owner-review stop only after review actually occurs |

A passing gate does not establish efficacy, data quality, legitimate participation, deployment
readiness, or accepted evidence. It only says the packet is internally complete enough for the next
human stop. The old post-cycle attestation placeholder must not be required for entry readiness; only the local attestation route is set before the cycle. If aggregate post-cycle rows are partially filled but dates or rows are incoherent, the packet returns to `NOT_READY` for repair rather than pretending it is entry-ready again.

## Boundary

No status authorizes evidence import, service-record authority, public claims, or `FT-0181` closure.

## rev0336 suppression check

Entry readiness now includes `small-cell-threshold-usable`. `OWNER-PLAN.md` must contain a numeric local threshold of at least three so a future result receipt can mask exact counts/rates below that threshold.

## rev0336 run-definition hash check

Entry readiness now includes `run-definition-hash-stable`. The generated `DISCOVERY-FIRST-CONTACT.md`,
`COACH-PROMPT.md`, `RUN-CHECKLIST.md`, `MEASURE-CARD.md`, and `CYCLE-RUN-SHEET.md` must still match
`PACK-MANIFEST.json`, and `COACH-PROMPT.md` must match the prompt-card SHA-256 in `OWNER-PLAN.md`.
If a teacher/tutor needs different prompt or run instructions, regenerate the packet rather than
patching those files.

## rev0336 event chronology check

Post-cycle readiness now includes `session-log-dates-valid-and-ordered`. `SESSION-LOG.csv` rows must use ISO `YYYY-MM-DD` dates ordered `D1-baseline <= D2-D3-coach-use <= D4-transfer`. The owner-review recorder refuses a review date before the latest session row, and the result recorder refuses a result date before owner review or the latest session row.

## rev0336 follow-through seed check

Post-cycle readiness now includes `decision-followthrough-spec-recorded`. A non-retire decision (`repeat-narrower`, `continue-bounded`, or `escalate-to-pilot-review`) must include a de-identified owner-written follow-through seed in `OWNER-DECISION-MEMO.md` before owner review can pass. The scorer records only that the seed exists; it does not copy local seed text into the scorecard.

## rev0336 follow-through source link check

Ordinary first-cycle packets have no prior-result source link. A fresh packet produced after a `repeat-narrower` or `continue-bounded` result must include `FOLLOWTHROUGH-SOURCE-RESULT.json`. Readiness checks that the source result exists locally, still matches the recorded SHA-256, has a repeat/continue decision, and preserves non-evidence/no-copy boundaries. If the source result is missing or changed, the packet is `NOT_READY` and must be regenerated from the valid local result and owner-supplied next arguments.
