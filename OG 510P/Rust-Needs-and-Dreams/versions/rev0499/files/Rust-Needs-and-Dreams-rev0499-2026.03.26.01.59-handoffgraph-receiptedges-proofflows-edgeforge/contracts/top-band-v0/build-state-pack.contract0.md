# Kernel interface contract 0: Build-State Pack

## Identity
- candidate: **Build-State Evidence**
- governing kernel: `kernels/top-band-v0/build-state-pack.v0.md`
- governing slice: `slices/top-band-v0/build-state-pack.slice0.md`
- current verdict context: `advance`
- contract codename: `build-state-pack/contract0`

## Contract scope
Fix the first explicit local surface for build-session capture, diffing, and bounded diagnosis.
This contract is for **local companion tooling**.
It does not claim a stable upstream Cargo API.

## Public surfaces
### Commands
1. `build-state capture --workspace-root <path> --out <pack.json>`
2. `build-state diff --left <pack.json> --right <pack.json> --out <diff.json>`
3. `build-state doctor --pack <pack.json> --out <note.md|note.json>`
   or
   `build-state doctor --diff <diff.json> --out <note.md|note.json>`

### Rendered/operator surfaces
- one machine-readable session pack
- one machine-readable diff
- one bounded doctor note
- one unsupported-state receipt when evidence is partial or caveated

## Required inputs
- workspace root path
- Cargo and rustc version receipts
- package-selection scope if not default workspace scope
- target/profile/features receipts when non-default
- captured Cargo JSON message stream or stored equivalent
- optional config/environment receipt with redacted sensitive values

## Emitted artifact families
- `build-session-pack/v0`
- `build-diff/v0`
- `build-doctor-note/v0`
- `unsupported-state-receipt/v0`

Minimum pack fields should include:
- schema family + contract version
- capture timestamp
- tool versions
- workspace root / manifest root identity
- selected packages / targets / features
- command receipt
- artifact path observations
- imported stable evidence blocks
- imported experimental evidence blocks
- warnings / caveats

## Stable imports
Allowed stable imports:
- `cargo metadata --format-version=1`
- Cargo/rustc `--message-format=json`
- explicit config and environment receipts
- manifest / lockfile snapshots

## Optional experimental imports
Allowed but caveated imports:
- `cargo report rebuild-reasons`
- `cargo report timing`
- nightly build-dir-layout-v2 observations
- Cargo SBOM pre-cursor JSON outputs

Rule: experimental imports must live in separately labeled fields and must never silently upgrade the stable contract claim.

## Versioning and compatibility posture
- `contract0` is additive-first.
- Unknown fields must be ignored by readers.
- Removing or renaming required fields is out of bounds inside `contract0`.
- Stable-import-only packs must remain readable even when experimental blocks are absent.

## Negative states / receipts
The contract must preserve receipts for:
- mixed JSON / non-JSON output streams
- end-of-stream ambiguity or truncated capture
- artifact path observations that cannot be normalized safely
- missing unstable report data
- nightly-only layout observations
- cross-tool contention cases where only partial evidence was captured

## Proving-ground invocation
A valid proving-ground run should include:
1. one stable-only capture + diff on a medium local workspace;
2. one nightly run with `-Zbuild-dir-new-layout` clearly labeled as experimental;
3. one doctor note for a bounded class of change such as rebuild-cause drift or layout caveat drift.

## Refused expansions
Do **not** treat `contract0` as permission for:
- remote telemetry or central storage,
- live dashboards,
- cache mutation or cache movement,
- or Cargo-as-a-library coupling.

## Exit criteria
This contract may widen only after:
- at least three real proving-ground runs succeed,
- stable-only and unstable-enhanced posture are clearly distinguishable in practice,
- and the doctor note improves at least one real local decision without hidden scraping.
