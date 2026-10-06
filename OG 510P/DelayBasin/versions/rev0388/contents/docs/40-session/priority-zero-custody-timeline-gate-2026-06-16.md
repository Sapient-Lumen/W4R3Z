# Priority-0 custody timeline / distinct-custodian gate — 2026-06-16

`rev0371` resolves `OQ-0262` via `RS-0270` narrowly: it does **not** collect a clean external response. It closes a more immediate admission gap in the external replay lane.

The risky defect was that a future response could present a separate-looking custody evidence record while still being fake-clean: the record might be time-impossible, self-custodied by the responder, or disconnected from the responder's timestamps. That would make the cube vulnerable to exactly the kind of proof-looking ceremony it has been trying to cut.

The new gate requires all of the following before a response can be treated as clean external evidence:

- a frozen answer-bearing response to `handoffs/priority-zero-timeline-hardened-external-replay-responder-bundle-2026-06-16.zip`;
- a separate custody evidence record;
- a `custodian_id` that differs from the response `responder_id` (custodian_id that differs from responder_id);
- matching custody/response `responder_id` values;
- timezone-bearing chronology where `run_started_at <= run_completed_at <= response_frozen_at <= scorer_opened_at`;
- manual metric coverage and threshold-based confirm/narrow/reverse scoring only after that admission gate passes.

Two negative canaries make the failure mode executable:

- `assays/priority-zero-timeline-hardened-external-replay-time-inverted-custody-canary-2026-06-16.json` is hash-correct but has `scorer_opened_at` before `response_frozen_at`; it must fail closed.
- `assays/priority-zero-timeline-hardened-external-replay-self-custodied-custody-canary-2026-06-16.json` has valid chronology but uses the responder as custodian; it must fail closed.

## Stopgate

No further internal gate-hardening counts as external replay progress. `OQ-0263` must import a response, not another gate-only hardening pass. Internal repairs remain allowed only when labeled as repairs or failure handling; they cannot strengthen the compact gate.

## Scored posture

| Variant | Score | Meaning |
|---|---:|---|
| Pre-timeline custody admission | 6 / 16 | Separate custody existed, but chronology/distinct-custodian forgery remained possible. |
| Timeline/distinct-custodian current gate | 14 / 16 | Admission is harder to fake and current scorer defaults route to the live scorer. |
| Time-inverted custody canary | 16 / 16 | Impossible chronology is rejected before manual scoring. |
| Self-custodied custody canary | 16 / 16 | Responder-as-custodian records are rejected before manual scoring. |
| Clean response plus timeline custody record | 0 / 16 | Correctly absent; no clean external/operator-independent response exists yet. |

Non-claim: not a clean external replay result, not independent certification, not deletion authority, not benchmark authority, not compact-cue confirmation, not a review court, and not a minimality proof.
