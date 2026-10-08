# Live artifact import fieldkit and invariant replay

## Purpose

rev0204 proved that the computed live-floor engine can count strict eligible imports inside quarantine while keeping the archive floor at zero. That is necessary but not sufficient. The next live artifact can still fail before the computation step if an operator creates a response, intake, or import gate from an incomplete artifact package.

rev0205 adds a fieldkit for the first live counterparty artifact and an invariant replay report. The fieldkit defines the raw evidence slots that must exist before any artifact leaves quarantine. The invariant replay report recomputes the archive floor and records why every current import-like object still has zero live weight.

## Current rule

**Raw artifact package precedes response creation.**

No response record, receipt-intake record, import gate, class-local replay, WRSR closure, result-return closure, or live-floor delta may be created from a counterparty artifact until the raw artifact package has been admitted. Admission requires raw payload custody, hash match, independent timestamp, class-specific authority proof, request trace, non-host retention, sealed/public parity, dependency-group review, and failed-gate publication path.

**Fieldkit readiness is not artifact admission.**

The fieldkit can make a live import attempt easier, but it has `fieldkit_state=ready-no-live-artifact`. It carries no receipt weight, starts no no-response clock, and cannot create an intake record.

**Invariant replay beats narrative.**

The invariant report is generated from the computed-floor engine and cross-checks archive examples. If a hand-edited quorum ledger, public summary, or narrative says a live receipt exists while the invariant replay and computed snapshot disagree, reliance stays blocked until the source artifacts are repaired and recomputed.

## Required raw evidence slots

A live artifact package must include, or explicitly fail-gate, all of these slots:

1. Raw payload or sealed raw payload locator.
2. Hash and hash algorithm for the exact raw payload.
3. Independent timestamp or transport trace not controlled by the host.
4. Sender/counterparty identity evidence.
5. Class-specific authority proof for the receipt class being claimed.
6. Request trace tying the response to the live receipt request.
7. Non-host retention proof or custody undertaking.
8. Sealed/public parity split, including a public shell that does not leak sealed details.
9. Dependency-group map for counterparty, witness, steward, and host dependencies.
10. Failed-gate public summary route for rejection, challenge, no-response, declination, or rollback.

## Replay sequence

The only permitted positive path is:

`fieldkit -> custody -> envelope -> response -> intake -> import gate -> challenge/rollback check -> class-local replay -> computed floor -> quorum recomputation -> public failed-gate or live-class summary`.

Every skipped step is a no-go condition. A class-local positive result can at most satisfy its receipt class. Cross-critical reliance remains stayed until all required live classes are recomputed as present.

## Failure modes blocked in rev0205

- A fieldkit or checklist is treated as admitted live evidence.
- A response record is created before raw artifact custody is admitted.
- A hash match is treated as authority proof.
- A result-return authority proof is reused for another receipt class.
- A hand-edited import or quorum record overrides computed-floor and invariant replay output.
- Failed-gate branches disappear because an artifact never made it past quarantine.

## Operational consequence

The archive still has zero live external receipts. rev0205 makes the next real artifact safer to process by forcing raw package completeness and invariant replay before any live-floor claim can be made.
