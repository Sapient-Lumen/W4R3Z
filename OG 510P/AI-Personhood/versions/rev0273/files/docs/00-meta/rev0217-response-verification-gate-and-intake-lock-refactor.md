# rev0217 response verification gate and intake-lock refactor

rev0217 closes the next risky seam after response-only custody: a custody record may permit response preparation, but it does not prove that a verified, scoped counterparty reply exists.

## Changed boundary

The live artifact path is now:

`evidence drop -> first-artifact pilot -> LEAP candidate -> candidate challenge/replay -> custody authority gate -> custody record -> response verification gate -> response record -> intake conversion gate -> import gate -> computed floor`

The new response verification gate is deliberately narrow. It can only say whether an external receipt response record may be prepared. It cannot create an intake record, cannot run an import gate, and cannot alter the computed live floor.

## Why this matters

The previous route had a subtle overclaim risk. Once custody became response-only, a later maintainer could still treat a reply-looking artifact as an intake-ready actual response before verifying counterparty identity, independent timestamping, request-trace match, non-host retention, dependency separation, receipt-class match, scoped acceptance, freshness, and manual review.

rev0217 makes that impossible in the runnable path by adding:

- `schemas/external-receipt-response-verification-gate.schema.json`
- `tools/prepare_external_receipt_response_gate.py`
- `tools/audit_external_receipt_response_verification_gate.py`
- `examples/external-receipt-response-verification-gate-rev0217-blocked-no-response.json`
- negative fixtures for unverified replies and missing scoped acceptance

## Refactor effect

`external-receipt-response-record.schema.json` now requires `linked_response_verification_gate_ref` whenever an actual response is marked capable of generating an intake candidate. The older conversion fixture is retained, but it is explicitly marked as a controlled fixture gate rather than a live gate.

The admission graph now includes a `RESPONSE_GATE` node between custody and response. The invariant report scans response-gate objects and blocks any route where a response gate unlocks intake, import, or live-floor credit.

## Reliance limit

rev0217 still has no genuine external artifact and no live receipt. The response gate improves the first-real-artifact path, but all response, intake, import, and floor movement remain stayed until real external material passes every gate in order.

## Audit-path refactor

rev0217 also trims release lint back to the active live-artifact risk boundary. Historical audit scripts remain available in `tools/`, but the packaging-critical `make lint` path now concentrates on response verification, admission graph integrity, invariant/floor checks, front-door freshness, current catalog/registry coverage, and JSON/schema validation. This is deliberate: the release gate should catch current overclaim risk without spending the whole session re-running every older doctrine/backfill audit.
