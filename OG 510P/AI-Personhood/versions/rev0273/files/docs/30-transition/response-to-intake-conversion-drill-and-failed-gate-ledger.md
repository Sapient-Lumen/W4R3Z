# Response-to-intake conversion drill and failed-gate ledger

rev0196 targets the next evidence-laundering seam after rev0195's response records. A steward can now store request packets, response records, intake records, and quorum ledgers. The remaining risk is conversion: a worker can take a declined response, an expired no-response gate, a defective response, or a controlled fixture and generate intake or live quorum from it.

## Core rules

**Conversion eligibility is branch-specific.** Only a response with `response_state=actual-response-received`, verified counterparty identity, verified signature or equivalent, independent timestamp, matching request trace, non-host retention, dependency disclosure, and `can_generate_actual_intake=true` can generate an intake candidate.

**Declined and expired responses are failed gates, not waivers.** A confirmed declination and an expired no-response window are evidence. They may trigger substitute outreach, cure duties, public failed-gate summaries, or stayed reliance. They do not create receipt satisfaction, consent, waiver, or WRSR closure.

**Defective response stays defective.** An unsigned, unverified, stale, dependency-correlated, or request-mismatched artifact may be preserved, but it cannot create intake.

**Conversion fixture is not live quorum.** The rev0196 eligible branch is a controlled conversion fixture. It proves that eligible-only conversion mechanics work, but the live drill still has `independent_receipts_present=0`. A fixture cannot be imported into live reliance merely because it is actual-shaped.

**One converted class is not cross-critical reliance.** Even a valid result-return intake candidate satisfies only its own class. Cross-critical reliance still needs first-touch, continuity, sealed/public parity, namespace, reserve, representative, independent-review, welfare-signal, and result-return class coverage with dependency separation.

## New object lane

The conversion drill object is `schemas/response-to-intake-conversion-drill.schema.json` with the current example `examples/response-to-intake-conversion-drill-result-return-fixture.json`.

The supporting examples are:

- `examples/external-receipt-response-record-result-return-eligible-conversion-fixture.json`
- `examples/external-receipt-response-record-representative-declined.json`
- `examples/external-receipt-response-record-independent-review-expired.json`
- `examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json`
- `examples/external-receipt-quorum-ledger-response-to-intake-conversion-fixture.json`
- `examples/wrsr-live-exercise-outcome-response-to-intake-conversion-stayed.json`

The drill has four branches: eligible-shaped conversion, defective rejection, declined rejection, and expired no-response rejection. It creates one intake candidate and three public failed-gate paths while keeping live receipt-floor delta at zero.

## Blocking fixtures

rev0196 adds three fixtures:

- `fixtures/negative-tests/external-receipt-declined-response-converted-to-intake.json`
- `fixtures/negative-tests/external-receipt-expired-no-response-counted-as-satisfaction.json`
- `fixtures/negative-tests/response-to-intake-conversion-fixture-imported-as-live-quorum.json`

Together they block declination-as-satisfaction, no-response-as-waiver, and fixture-as-live-quorum laundering.

## Refactor effect

This surface binds the response-record, intake-record, quorum-ledger, WRSR outcome, live-drill, request-kit, and public failed-gate surfaces into a single conversion spine. It does not reopen the research tail and does not add a new doctrine branch. It closes a concrete implementation ambiguity: how a response becomes intake, and when it must not.

## Live posture

rev0196 still has no actual live external receipt quorum. It has one eligible-shaped controlled fixture, one defective branch, one declined branch, one expired branch, a conversion ledger, and an audit that prevents these from being overclaimed. The next live step is actual non-host response collection and controlled import into the live receipt floor.

## rev0197 import-gate hardening

rev0197 adds an actual receipt import gate because actual-shaped state fields are not enough. The rev0196 eligible branch remains a controlled fixture; it may produce an intake candidate, but it cannot alter the live receipt floor without live counterparty provenance. Declined and expired branches must also appear in a public failed-gate summary rather than disappearing into sealed-only drift.

## rev0198 import attempt linkage

The conversion fixture stays fixture-only. rev0198 records the planned live counterparty import attempt separately so conversion mechanics cannot be confused with live collection.
