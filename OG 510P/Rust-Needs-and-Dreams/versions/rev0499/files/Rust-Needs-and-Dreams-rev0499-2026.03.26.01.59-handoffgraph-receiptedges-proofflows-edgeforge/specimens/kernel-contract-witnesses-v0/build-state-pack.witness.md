
# Contract witness: Build-State Pack

Status: **illustrative witness, not live proving-ground evidence**

## Identity
- candidate: **Build-State Evidence**
- governing packet: `packets/top-band-v0/build-state-evidence.advance.current.md`
- governing kernel: `kernels/top-band-v0/build-state-pack.v0.md`
- governing slice: `slices/top-band-v0/build-state-pack.slice0.md`
- governing contract: `contracts/top-band-v0/build-state-pack.contract0.md`
- witness role: `contract-witness/v0`

## Invocation shape
Illustrative command family:
- `build-state capture --workspace-root ./example/service --out build-session-pack.example.json`
- `build-state diff --left build-session-pack.example.json --right nightly-session-pack.example.json --out build-diff.example.json`
- `build-state doctor --diff build-diff.example.json --out build-doctor-note.example.md`

## Example files
- `build-state-pack.build-session-pack.example.json`
- `build-state-pack.build-diff.example.json`
- `build-state-pack.build-doctor-note.example.md`
- `build-state-pack.unsupported-state-receipt.example.json`

## Truth preserved
This witness is allowed to show:
- stable-only versus unstable-enhanced evidence separation,
- one bounded build-layout drift example,
- one doctor note that stays reviewable and local-first.

## Negative or partial-state posture
This witness keeps one explicit caveat and one explicit unsupported-state receipt:
- build-dir-layout-v2 observations are present but marked experimental, so the doctor note can mention them without pretending they are a stable Cargo promise.

## Refused wider interpretations
Do **not** read this witness as:
- proof that Cargo report outputs are stable,
- proof that remote telemetry or cache automation belongs in v0,
- or proof that one example workspace covers broad ecosystem diversity.

## Refresh trigger
Refresh this witness when:
- `cargo report` output posture changes materially,
- build-dir-layout testing/stabilization changes what caveats are needed,
- or the contract0 fields become materially different.
