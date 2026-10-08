# Toolchain & target support artifact-route boundaries — 2026-03-22

This note exists to keep **P-0484 Toolchain & Target Support Contract Kit** sharp after the latest Cargo and target-support signals.

## Main judgment

**P-0484** should now explicitly own two additional truths:

- **artifact route** — how a lane finds the artifacts it depends on;
- **host-target topology** — which phases compile or execute on the host, target, docs service, CI service, runner, or device.

Without those truths, many support claims remain folklore.

## The two new truths P-0484 should keep separate

### 1. Artifact route
A project may find outputs via:

- stable Cargo JSON messages,
- cargo metadata or other documented interfaces,
- docs.rs metadata / landing-page conventions,
- CI artifact naming,
- `target/` path conventions,
- or Cargo-internal build-dir layout assumptions.

Those are not equally stable and should not be flattened into one vague “release script works”.

### 2. Host-target topology
A supposedly cross-target lane can still have mixed execution topology:

- build scripts compile for and run on the host,
- proc macros compile for and run on the host,
- target artifacts compile for the target,
- tests or runs may require a runner, emulator, simulator, Rosetta, board, or device farm,
- docs builds may happen on docs.rs rather than the project’s own CI.

Those are not the same support claim.

## What P-0484 must stay separate from

### Separate from Cargo-internals reverse engineering
P-0484 can record that a workflow relies on internal layout.
It should not become a giant Cargo archaeology crate.

### Separate from full docs.rs parity replay
P-0484 can record docs posture and hosted artifact route.
Reproducing docs.rs failures remains a neighboring lane.

### Separate from native-linker diagnosis
P-0484 can say a runner or linker is required.
It should not absorb every platform-specific failure explainer.

## Two `0.1` artifacts worth promoting now

### `artifact-route.receipt.json`
A receiver-facing artifact for:

- artifact kind,
- producer phase,
- discovery basis,
- stability posture,
- host/target relation,
- locator details,
- evidence and risk notes.

### `host-target-topology.receipt.json`
A receiver-facing artifact for:

- host triple,
- target triple,
- phase-by-phase execution lane,
- runner requirements,
- and notes about mixed host/target truth.

## Anti-flattening reminders

Do not say:

- “The artifact is in `target/`, so the route is obvious.”
- “Cross target tests passed” when only host build scripts and proc macros were exercised.
- “docs.rs shows the API, therefore the target lane is supported.”
- “The target still downloads, so the support class is unchanged.”
- “Build-dir layout is internal, so nobody depends on it.”

Those are exactly the assumptions P-0484 should make visible.

## Sources

- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://docs.rs/about/metadata
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://blog.rust-lang.org/2025/05/26/demoting-i686-pc-windows-gnu/
- https://blog.rust-lang.org/2025/08/19/demoting-x86-64-apple-darwin-to-tier-2-with-host-tools/
