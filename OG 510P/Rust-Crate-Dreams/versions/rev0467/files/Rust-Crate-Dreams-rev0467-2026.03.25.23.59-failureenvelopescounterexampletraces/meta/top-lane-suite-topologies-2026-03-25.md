# Top-lane suite topologies — 2026-03-25

This note turns the leading lanes into **package-family plans**.
It is more concrete than a frontier scan and more packaging-specific than the earlier product-blueprint note.

## Suite A — P-0509 + P-0536 + minimal P-0535
### Working family
- `pathfinder-core`
- `pathfinder-schemas`
- `cargo-pathfinder`
- `pathfinder-importers` *(0.3)*
- `pathfinder-corpus` *(0.3)*

### Receiver surfaces
- platform or project lead runs `cargo-pathfinder`
- integrator embeds `pathfinder-core`
- reviewer and adjacent tooling depend on `pathfinder-schemas`

### `0.1` shape
Ship only:
- core decision logic,
- review packet types,
- basis lock types,
- one CLI workflow for explain/freeze/reopen.

### Why this shape works
- selection logic is stable enough to deserve a core crate;
- packet meaning deserves a schemas crate;
- crates.io/docs.rs/Cargo ingestion can stay behind importer boundaries.

## Suite B — P-0472 + P-0484
### Working family
- `support-envelope-core`
- `support-envelope-schemas`
- `cargo-support-envelope`
- `support-envelope-docsrs` *(0.3)*
- `support-envelope-targets` *(0.3)*
- `support-envelope-corpus` *(0.3)*

### Receiver surfaces
- maintainer or release engineer runs the CLI
- platform/integration tooling embeds the core
- review systems and downstream checks consume the schemas

### Key doctrine
Do not bury docs.rs/build/target/toolchain packet semantics inside importer code.
The core package should speak in stable support-envelope language such as:
- documented,
- built,
- cross-compiled,
- locally observed,
- unknown,
- refused.

## Suite C — P-0486
### Working family
- `debug-support-core`
- `debug-support-schemas`
- `cargo-debug-support`
- `debug-support-probes` *(later)*
- `debug-support-corpus` *(later)*

### `0.1` restraint
At first, do not try to model every debugger and platform.
Instead ship:
- matrix packet types,
- limited probe/import routes,
- explicit degraded outputs,
- clear claim ceilings.

### Why package splitting matters here
Debug probes and environment collection will churn faster than the meaning of support packets.
Keep them separate.

## Suite D — P-0431 + P-0496 + P-0125
### Working family
- `carryforward-core`
- `carryforward-schemas`
- `cargo-carryforward`
- `carryforward-source-parity` *(optional adapter)*
- `carryforward-boundary` *(optional adapter)*
- `carryforward-sbom` *(optional adapter)*
- `carryforward-corpus`

### Receiver surfaces
- release/supply-chain operator runs the CLI
- governance or tooling team embeds the core
- review/audit systems consume the schemas

### Package rule
Keep source-parity, public-boundary, and SBOM precursor logic separate unless they truly share packet semantics.
Shared workflow is not enough reason to merge meanings.

## Suite E — P-0537
### Working family
- `iteration-feedback-core`
- `iteration-feedback-schemas`
- `cargo-iteration-feedback`
- `iteration-feedback-corpus`

### Planning note
This family should stay compact until Cargo build-analysis surfaces settle more.
A narrow `cargo report`-adjacent helper is better than premature ecosystem sprawl.

## Suite F — P-0538
### Working family
- `concurrency-contract-core`
- `concurrency-contract-schemas`
- `cargo-concurrency-contract`
- `concurrency-contract-corpus`

### Planning note
The corpus matters as much as the code here.
If semantics differ across runtimes/channels/primitives, the corpus must remain first-class from day one.

## Cross-suite shared rule

The archive should prefer package families where:
- the CLI is thin,
- the core owns meaning,
- the schemas own reviewable structure,
- adapters absorb substrate churn,
- and the corpus defends the claims.

That is now a stronger answer to “what should the crate provide other people?” than saying “a really good API”.
