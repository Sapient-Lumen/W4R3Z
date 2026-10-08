
# Contract witness: Package Intake Review Kit

Status: **illustrative witness, not live proving-ground evidence**

## Identity
- candidate: **Package Intake + Release Boundary Review**
- governing packet: `packets/top-band-v0/package-intake.advance.current.md`
- governing kernel: `kernels/top-band-v0/package-intake-review-kit.v0.md`
- governing slice: `slices/top-band-v0/package-intake-review-kit.slice0.md`
- governing contract: `contracts/top-band-v0/package-intake-review-kit.contract0.md`
- witness role: `contract-witness/v0`

## Invocation shape
Illustrative command family:
- `intake review --route-profile github-trusted-publishing --project ./example/app --out intake-receipt.example.json`
- `intake waive --receipt intake-receipt.example.json --reason ./waiver.md --owner release-eng --expires 2026-06-01 --out waiver-receipt.example.json`
- `intake drill --route-profile alternate-registry-basic --scenario extraction-permission-bug --out incident-drill-report.example.json`

## Example files
- `package-intake-review-kit.route-profile.example.json`
- `package-intake-review-kit.intake-receipt.example.json`
- `package-intake-review-kit.waiver-receipt.example.json`
- `package-intake-review-kit.quarantine-receipt.example.json`
- `package-intake-review-kit.incident-drill-report.example.json`
- `package-intake-review-kit.unsupported-state-receipt.example.json`

## Truth preserved
This witness is allowed to show:
- route-profile-specific review,
- waiver lineage back to one receipt,
- and one incident drill whose uncertainty remains explicit.

## Negative or partial-state posture
This witness keeps one explicit caveat and one explicit unsupported-state receipt:
- the alternate-registry drill cannot inherit crates.io protections automatically, so the drill report preserves uncertainty rather than collapsing to green.

## Refused wider interpretations
Do **not** read this witness as:
- a global trust score,
- proof that one route profile covers all publishing paths,
- or permission to auto-block every workflow.

## Refresh trigger
Refresh this witness when:
- route profile fields change materially,
- crates.io or Cargo advisory posture changes materially,
- or new provenance/capability imports become first-class in contract0.
