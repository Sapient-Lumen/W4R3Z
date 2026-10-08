# Time-to-refute (TTR) test plan — Template

**Track:** A (Deployable core)

This is a compact drill plan for verifying that “refutation is possible quickly” (see `docs/240`).
Keep it short; link to packets/digests instead of pasting content.

## Scope
- Jurisdiction / election:
- Public-surface(s) in scope (official site, notice feed, status board, social accounts):
- Mirror paths in scope (`docs/200–205`):
- Who runs the drill (roles + contacts):

## TTR budgets (publish these)
- TTR‑1 target (thin refutation: signed PublicNotice is mirrorable): ___ minutes
- TTR‑2 target (thick refutation: offline-verifiable packet exists): ___ minutes

## Scenarios (pick 3–6)
For each scenario: describe the false claim in one sentence; specify the expected refutation object(s).

| ID | False claim | Expected refutation object(s) | TTR‑1 target | TTR‑2 target |
|---|---|---|---:|---:|
| S‑01 |  | PublicNotice + packet |  |  |
| S‑02 |  |  |  |  |


## Communication path (pre-wire; don’t improvise)
- Authenticity response cell (names + contacts):
- Rostered independent verifiers to notify (verifier_id + report_feed):
- Where the public should look first (status/rumor-control URL + mirror pointers):
- How the verdict propagates to high‑reach channels (digest card / short-form post that points back to the status surface; no screenshots):

## Tools readiness (minimum)
- Offline verifier workflow works on an air‑gapped laptop (`observer-kit/`).
- Comms staff can fetch feed/keyset digests and produce short-form digests without engineering help.
- At least one rostered verifier can publish a PacketVerificationReport during the drill.

## Measurement
- Clock starts when: (first internal recognition / first public observation / other):
- How you measure third‑party verifiability: (MAPT check, independent verifier replay, etc.) (`docs/187`, `docs/188`)

## Outputs (publishable)
- PublicNotice digests/links for each scenario:
- Evidence packet digests/links for each scenario:
- Any PacketVerificationReports / witness cosigns / dissent items:
- After-action notes (what failed, what changed) (`schemas/AfterActionReport.json`)

## Failure conditions (be honest)
- No signed object exists inside TTR‑1.
- Packet exists but can’t be verified offline by a third party inside TTR‑2.
- Refutation required “trust us” language because the authoritative bytes were not discoverable/mirrorable.
