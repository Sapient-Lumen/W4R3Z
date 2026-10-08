
# Contract witness: Safety-Critical Readiness Cards

Status: **illustrative witness, not live proving-ground evidence**

## Identity
- candidate: **Safety-Critical + Institutional Readiness Commons**
- governing packet: `packets/top-band-v0/safety-critical-readiness.deepen.current.md`
- governing kernel: `kernels/top-band-v0/safety-critical-readiness-cards.v0.md`
- governing slice: `slices/top-band-v0/safety-critical-readiness-cards.slice0.md`
- governing contract: `contracts/top-band-v0/safety-critical-readiness-cards.contract0.md`
- witness role: `contract-witness/v0`

## Invocation shape
Illustrative command family:
- `readiness lint --cards cards/*.json --out readiness-lint-report.example.json`
- `readiness pack --cards cards/*.json --subject controller-ecu --out readiness-pack.example.json`
- `readiness diff --left readiness-pack-v1.json --right readiness-pack-v2.json --out readiness-diff.example.json`

## Example files
- `safety-critical-readiness-cards.readiness-card.example.json`
- `safety-critical-readiness-cards.readiness-pack.example.json`
- `safety-critical-readiness-cards.readiness-lint-report.example.json`
- `safety-critical-readiness-cards.readiness-diff.example.json`
- `safety-critical-readiness-cards.stale-card-receipt.example.json`

## Truth preserved
This witness is allowed to show:
- owner/freshness/evidence-bearing card structure,
- one bounded readiness pack for a concrete subject,
- and one diff that changes risk posture without pretending to certify the subject.

## Negative or partial-state posture
This witness keeps one explicit non-proof clause and one explicit stale-card receipt:
- the card and pack can improve institutional review, but they do **not** prove certification or universal readiness.

## Refused wider interpretations
Do **not** read this witness as:
- a qualification badge,
- proof that async-runtime requirements are fully settled,
- or evidence that one subject pack generalizes across criticality ladders.

## Refresh trigger
Refresh this witness when:
- readiness-card required fields change materially,
- safety-critical guidance shifts materially,
- or pack/diff posture grows beyond current contract0.
