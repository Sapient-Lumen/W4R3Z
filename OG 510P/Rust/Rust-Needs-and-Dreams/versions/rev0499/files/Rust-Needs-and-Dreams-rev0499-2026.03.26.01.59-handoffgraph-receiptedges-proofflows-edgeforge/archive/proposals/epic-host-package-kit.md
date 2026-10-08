# Epic proposal: Host Package Kit (`cargo hostpkg`, `hostpkg-pack/v0`)

## One-line thesis
Build a thin Rust companion layer for **foreign-consumer package truth** that links **crate-vs-foreign-package identity**, **imported boundary artifacts**, **runtime/interpreter/ABI constraints**, **shipped/install receipts**, and **bounded downstream conclusions** into one portable review boundary without pretending Python, Node, mobile bindings, native handoff, and Wasm components are one lane. Read [`design/python-host-lane-map.md`](../design/python-host-lane-map.md) as the Python-specific split beneath this epic.

## Why this is now worth doing
Rust’s mixed-language and host-runtime adoption story is now broad enough that the missing contribution looks like a **reviewable package contract above the ingredients** rather than one more ingredient:
- Rust’s 2026 flagship slate explicitly includes **Wasm Components**, which makes foreign-consumer package/runtime lanes first-class ecosystem work rather than a niche side topic;
- the Rust/component-model docs now say native `wasm32-wasip2` support is first-class, while `cargo-component` says simple WASI-only lanes can use plain Cargo but custom-WIT lanes still need `cargo-component` and remain experimental;
- the safety-critical interop writeup says teams will integrate Rust into existing C/C++ systems and carry that boundary for years, which raises the value of auditable packaging/runtime handoff;
- the 2025H2 interop problem-map goal says mixed-language adoption is a first-class Rust problem rather than an edge case;
- maturin already spans PyO3, cffi, UniFFI, and Rust-binary Python packaging while making cross-compilation and `manylinux` / `musllinux` posture real release constraints;
- Node-API offers a stable addon ABI lane, but that guarantee is specific to the Node-API boundary rather than every external dependency or runtime assumption around the addon;
- UniFFI is explicit that exposed interfaces must be `Send + Sync` and that borrowed-return-style foreign contracts should not leak across the boundary;
- the 2025 State of Rust survey says online docs remain canonical even as some traffic shifts toward LLM/editor workflows, which strengthens the case for small machine-readable package/support artifacts.

What is still missing is the **kit-level boundary that says one host package subject was built, packaged, installed, and supported with these imported boundary facts, these runtime constraints, these shipped artifacts, and these bounded consumer handoffs**.

## Working name
- CLI: `cargo hostpkg`
- primary artifact: `hostpkg-pack/v0`

## Scope
### This epic should own
- foreign-consumer package subject identity
- crate ↔ foreign package / module / bundle / component identity mapping
- imported `ffi-pack`, component/WIT, schema, or generated-binding attachments
- runtime/interpreter/ABI/SDK constraint summaries
- shipped/install receipt truth
- diffable package-level review points across releases and host lanes
- bounded release / support / atlas / assistant handoffs

### This epic should not own
- generating bindings itself
- choosing one universal IDL
- replacing maturin, `napi-rs`, UniFFI, CXX, or component tooling
- a host-language package manager or registry service
- universal ABI modeling
- a fake one-number “Rust package support” score

## Candidate artifact family
### `hostpkg-brief/v0`
Why the subject exists, intended foreign-consumer set, lane classification, and freshness/review status.

### `hostpkg-subject/v0`
The exact Cargo package, foreign package/module/component identities, source revision, target matrix, imported boundary references, and comparison base.

### `hostpkg-manifest/v0`
The machine-readable host package declaration described in [`design/host-package-kit.md`](../design/host-package-kit.md):
- package identities
- lane classification
- imported boundary artifacts
- runtime/interpreter/ABI/SDK constraints
- shipped artifacts
- support/platform claims

### `hostpkg-report/v0`
Reviewable findings covering:
- generated-binding provenance or drift
- package metadata drift
- runtime/ABI/support changes
- shipped/install artifact changes
- imported-boundary drift
- remediation hints and explicit uncertainty

### `hostpkg-pack/v0`
The portable bundle linking:
- `hostpkg-manifest/v0`
- `hostpkg-report/v0`
- generated bindings / stubs / package manifests / packaging configs
- imported `ffi-pack` / component / schema references
- checked install/import transcripts
- local waivers, caveats, and integrity metadata

### `hostpkg-diff/v0`
What changed between two review points, with separate sections for:
- foreign package identity drift
- generated-binding provenance drift
- runtime/interpreter/ABI/SDK drift
- shipped/install receipt drift
- support/documentation drift
- bounded downstream conclusion drift

### `hostpkg-handoff/v0`
Bounded consumer summaries for:
- release review
- support / incident intake
- downstream package maintainers
- ecosystem atlas / adoption review
- assistant/editor rendering

## Recommended rollout
1. Python lane family (full-API extension → `abi3` limited API → free-threaded extension → `asyncio` bridge)
2. Node addon lane
3. UniFFI-generated mobile-binding lane
4. native handoff lane importing `ffi-pack`
5. Wasm component lane importing component/WIT truth
6. bounded consumer handoff lane

This should be driven by [`design/host-package-kit.md`](../design/host-package-kit.md), with Polyglot and Extension productization stacks importing the resulting package anchor rather than replacing it.

## What makes this epic “epic” rather than incremental
An incremental tool would improve one lane:
- better wheel metadata,
- better prebuild tooling,
- better generated mobile bindings,
- better C/C++ packaging glue,
- or better component packaging.

An epic contribution here instead gives Rust one **portable foreign-package contract** above those lanes.
That is strategically different because it can:
- make Python/Node/mobile/native/component reviews share the same package subject boundary;
- let lane-specific tools stay specialized without pretending any one defines the whole package story;
- keep crate identity, foreign package identity, imported boundary truth, runtime constraints, install receipts, and support conclusions distinct but linked;
- and give release/support/atlas/assistant consumers a bounded artifact to import instead of re-scraping READMEs, CI logs, package-manager manifests, and issue-thread archaeology.

## Design principles
- **Crate identity is not foreign package identity.**
- **Imported boundary truth stays imported.**
- **Runtime/interpreter/ABI constraints are first-class, not footnotes.**
- **Install receipts do not replace support truth.**
- **Partial lane coverage is explicit.**
- **Consumer summaries are lossy on purpose and say so.**
- **The kit remains thin.**

## Success conditions
This epic is succeeding when Rust teams can say:
- “this is the exact foreign-consumer package subject,”
- “here are the package/module/component identities users actually install or import,”
- “here are the imported boundary artifacts and generated-binding facts we reviewed,”
- “here are the runtime/interpreter/ABI/SDK constraints that actually matter,”
- “here is what was shipped and how it was checked,”
- and “here is what release/support/atlas/assistant consumers may safely conclude,”

without inventing a bespoke packaging/support schema for every repository.

## Read this with
- `gaps/polyglot-host-packages-runtime-and-support-contracts.md`
- `design/host-package-kit.md`
- `design/polyglot-productization-stack.md`
- `design/polyglot-productization-pilot-program.md`
- `design/extension-productization-stack.md`
- `design/ffi-boundary-kit.md`
- `design/wasm-component-kit.md`
- `design/release-truth-stack.md`
- `design/support-envelope-kit.md`
