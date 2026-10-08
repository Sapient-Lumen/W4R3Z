# Teacher/tutor feasibility owner-review stop

A readiness pass is not a human decision. This recorder creates a hash-linked local stop record only
after a real teacher/tutor owner reviews the completed, non-synthetic packet.

## Preconditions

- readiness is `READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE`;
- `SESSION-LOG.csv` uses ISO dates ordered baseline <= coach-use <= transfer;
- no `DRY-RUN-TRACE.json` exists;
- the owner reviewed the local problem, intervention version, aggregate feasibility rows, learner
  participation/access route, protected local review decision, workload, stop triggers, and claim
  ceiling;
- the session event sequence actually happened, and the review date is on or after the latest dated session row.

## Command

```bash
make micro-pilot-owner-review \
  PACKET=scratch/field-handoff/rev0336/teacher-tutor-micro-pilot/teacher-selected-concept \
  REVIEW_DATE=YYYY-MM-DD \
  OWNER_ROLE="local teacher/tutor owner role only" \
  DECISION=<retire|repeat-narrower|continue-bounded|escalate-to-pilot-review> \
  CONFIRM=human-reviewed-local-micro-pilot-aggregate \
  OVERWRITE=1
```

The command writes `OWNER-REVIEW-STOP.json` and `.md` under scratch and hash-locks the reviewed packet
files. It must refuse synthetic rehearsals, incomplete packets, identifying content, and mismatched
decisions.

The four decisions are bounded operational choices. None means “effective.” `escalate-to-pilot-review`
means design a separate pre-specified evaluation before making an efficacy claim.

## Boundary

The stop record is not accepted evidence, custody, a service authorization, a public-claim basis, or
`FT-0181` closure.

## rev0336 result suppression boundary

`OWNER-REVIEW-STOP.*` records the small-cell threshold from readiness and the rule that any later result receipt must mask exact counts/rates below that threshold.

## rev0336 run-definition hash scope

`OWNER-REVIEW-STOP.*` now hash-locks the owner-reviewed run definition as well as the aggregate
packet: `DISCOVERY-FIRST-CONTACT.md`, `COACH-PROMPT.md`, `RUN-CHECKLIST.md`, `MEASURE-CARD.md`,
`CYCLE-RUN-SHEET.md`, `OWNER-PLAN.md`, `SESSION-LOG.csv`, `FINAL-READOUT.csv`,
`OWNER-DECISION-MEMO.md`, `PACK-MANIFEST.json`, and `READINESS-SCORECARD.json`. The later result
recorder must reject the packet if any of those files change after owner review.

## rev0336 event chronology stop

`OWNER-REVIEW-STOP.*` now records `latest_session_date`, the session chronology summary, and the chronology rule. The recorder rejects a review date earlier than the latest `SESSION-LOG.csv` date, preventing a human review stop from predating the aggregate rows it claims to review.

## rev0336 owner-review follow-through seed

Before an owner-review stop can be recorded for a non-retire decision, readiness must show that the owner decision memo contains a de-identified follow-through seed. The owner-review record carries only the seed status and checked label names, not the local seed text.
