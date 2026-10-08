# Kernel slice 0: Build-State Pack

## Identity
- candidate: **Build-State Evidence**
- governing kernel: `kernels/top-band-v0/build-state-pack.v0.md`
- current verdict context: `advance`
- slice codename: `build-state-pack/slice0`

## Why this slice first
This slice should prove one thing only: **a local team can capture two build sessions, diff them, and get one bounded doctor explanation without relying on Cargo internals as if they were stable APIs**.
That is a better first milestone than timings dashboards, remote storage, or cache automation because Cargo's build-analysis and build-dir surfaces are still moving.

## Exact deliverables
Ship only:
1. `schemas/build-state-pack-v0.schema.json`
2. `crates/build-state-cli/` with three subcommands:
   - `capture`
   - `diff`
   - `doctor`
3. `fixtures/sessions/` with at least:
   - one stable-only session pair,
   - one nightly `-Zbuild-dir-new-layout` comparison pair
4. `docs/proving-grounds.md`
5. one `unsupported-states.md` note covering unstable-report and layout-caveat posture

## Acceptance checks
The slice counts as done when it can:
- capture two real sessions from the same workspace using only documented Cargo seams;
- render a machine-readable diff with changed packages, targets, features, and artifact-path caveats;
- emit one doctor note for a bounded class of changes such as build-dir layout or rebuild-cause surprises;
- and clearly label whether the run was stable-only or unstable-enhanced.

## Proving grounds
Start with:
- one medium local workspace on stable,
- one same-workspace nightly run using `-Zbuild-dir-new-layout`,
- one local editor/Cargo contention scenario where capture still completes.

## Imports and dependencies
Allowed imports:
- `cargo metadata --format-version=1`
- `--message-format=json`
- explicit environment/config receipts
- optional unstable `cargo report *` surfaces with caveat labels

## Postponed work
Do **not** include yet:
- remote storage or telemetry
- cache pruning or cache movement features
- visual dashboards
- broad performance scoring
- Cargo-as-a-library integration

## Failure receipts
Ship unsupported-state receipts for:
- missing unstable report data
- mixed-tool output that is not reliable JSON
- path/layout assumptions that cannot be normalized safely

## Next-slice trigger
Take slice 1 only after slice 0 works across at least three proving-ground runs and the doctor note is useful without pretending unstable imports are guaranteed.
