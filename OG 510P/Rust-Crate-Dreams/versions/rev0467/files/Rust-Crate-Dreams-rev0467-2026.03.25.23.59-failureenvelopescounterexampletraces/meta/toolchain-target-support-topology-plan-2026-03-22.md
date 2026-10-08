# Toolchain & target support topology plan — 2026-03-22

This note deepens **P-0484 Toolchain & Target Support Contract Kit** around a specific product question:

> How should a support-contract crate describe *where evidence comes from* and *which machine/runtime actually exercised it*?

## Product stance

The crate should stay read-first and reviewer-facing.
It should not try to mutate CI, install SDKs, or fix linker problems automatically.
It should emit compact artifacts that let a maintainer, integrator, or release reviewer answer:

- how did this workflow find its artifact,
- is that route stable or brittle,
- which steps happened on the host,
- which steps genuinely exercised the target,
- and what external runner/device/service still sat in the loop.

## New first-class artifacts

### `artifact-route.receipt.json`
For each notable output, record:

- artifact kind (`bin`, `cdylib`, `docs`, `test-report`, `support-bundle`, ...),
- producer phase,
- discovery basis,
- stability posture,
- optional host/target relation,
- locator details,
- evidence,
- review notes.

### `host-target-topology.receipt.json`
For a lane, record:

- host triple,
- target triple,
- phase-by-phase execution topology,
- runner requirements,
- device/emulator/service dependencies,
- notes on partial or mixed exercise.

## CLI / workflow sketch

- `cargo support-contract capture` — existing bundle capture, now optionally emitting topology and route receipts.
- `cargo support-contract route` — inspect how a release/test/docs workflow locates artifacts and classify route stability.
- `cargo support-contract topology` — record host-vs-target execution phases and runner requirements.
- `cargo support-contract doctor` — flag brittle build-dir spelunking, hidden host-only steps, and target claims that outrun evidence.

## Receiver-facing value

### For maintainers
Catch brittle release/test scripts before Cargo or CI changes break them.

### For contributors
Understand whether “cross target support” means real runnable support or only compile coverage.

### For downstream integrators
See which parts of a lane depend on runners, emulators, or platform-owner review.

### For regulated teams
Separate official target tier, project support class, and evidence topology into one auditable bundle.

## MVP boundaries

### Include
- Cargo JSON-message artifact routes.
- Target-dir / build-dir layout risk classification.
- Host/build-script/proc-macro/target/test/docs phase capture.
- Runner requirement reporting.

### Exclude
- Automatic fixes for brittle scripts.
- End-to-end emulator orchestration.
- Native-toolchain installation.
- Full docs.rs replay.

## Good first fixture set

1. A release workflow that breaks when build-dir layout changes because it spelunks Cargo internals.
2. A cross-target lane where proc macros and build scripts are host-only and tests require a custom runner.
3. A target whose Rust-project tier changed, forcing the project to restate its support class explicitly.

## Sources

- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- https://docs.rs/about/metadata
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://rust-lang.github.io/rustup/cross-compilation.html
- https://rust-lang.github.io/rustup/overrides.html
