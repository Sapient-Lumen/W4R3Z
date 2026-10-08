# Cargo build-script delegation frontier — 2026-03-22

This note sharpens **P-0508 Cargo Build Script Delegation Kit** into the archive’s newer artifact-rich style.

## Main judgment

The missing value is not “make build scripts easier to write”.
The missing value is to make delegated / split / overridden build behavior **reviewable by other people**.

Right now the real pain is not only author pain.
It is receiver pain:

- reviewers cannot easily tell which build unit produced which output,
- downstream packagers cannot easily tell when `links` override config replaced live probing,
- CI owners cannot easily compare old single-unit flows against new delegated flows,
- and tool authors still end up reconstructing build behavior from logs and conventions.

That is why this lane should be framed as a **support contract**.

## Five truths this lane must keep separate

1. **unit topology** — what units exist and in what order;
2. **output lane** — what metadata, env exports, generated files, or staged artifacts each unit owns;
3. **override authority** — live execution, config override, delegate package, imported observation, or manual-review judgment;
4. **bridge posture** — stable local `OUT_DIR`, nightly artifact bridge, or unsupported/manual-review lane;
5. **drift** — what changed across releases, targets, or toolchains.

If those collapse into one sentence like “build scripts are delegated”, the lane has failed.

## Why now

The official substrate now has enough shape to justify a real crate plan:

- build scripts already have order-sensitive outputs and `OUT_DIR` constraints;
- Cargo external-tools JSON already provides machine-readable observations;
- multiple-build-scripts makes per-unit order and output identity explicit;
- Cargo config’s `target.<triple>.<links>` override route means live execution is not the only honest authority route;
- and Cargo 1.93’s artifact-dir discussion makes collision authority a first-class design constraint.

## Receiver-facing artifact set

This lane should now revolve around:

- `unit-topology.receipt.json`
- `output-lane.receipt.json`
- `override-authority.receipt.json`
- `delegate-bridge.report.json`
- `delegation-drift.diff.json`
- `build-script-support-bundle.manifest.json`

## What this lane is not

It is not:

- a replacement for Cargo build scripts,
- a new native-dependency package manager,
- a sandbox/jail design,
- a general build-graph profiler,
- or a logging UI.

## Adjacent lanes it must not absorb

- **P-0046 buildscript-ux-kit** — diagnosis and human-scale summaries;
- **P-0059 buildscript-testkit** — hermetic fixture/testing substrate;
- **P-0484 toolchain/target support** — host/target execution truth and support classes;
- **P-0495 artifact-dependency adoption** — target/artifact consumption posture after build outputs exist;
- **P-0121 FFI boundary kit** — runtime boundary truth after artifacts are built.
