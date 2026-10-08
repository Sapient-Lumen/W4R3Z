# Epic proposal: Polyglot Productization Stack (`cargo poly-product`, `polyglot-product-pack/v0`)

## One-line thesis
Build a thin stack-level Rust companion layer for **mixed-language productization** that links **host-package truth**, **native or component boundary truth**, **release/install truth**, and **support/docs truth** into one portable review boundary without collapsing Python, Node, mobile, C++, and component lanes into one fake “interop supported” badge.

## Why this is now worth doing
Rust has real mixed-language lanes now, but they still live in different planes:
- PyO3 + maturin can produce Python packages and wheels;
- Node-API gives a stable addon ABI lane;
- UniFFI gives generated mobile bindings and foreign-language packaging hooks;
- CXX gives serious Rust/C++ handoff paths across Cargo and external build systems;
- Wasm Components and WIT give a distinct language-neutral component lane.

What is still missing is the **stack-level boundary that says one mixed-language product subject was built, packaged, shipped, and supported with these imported truths, these caveats, these runtime assumptions, and this bounded handoff to consumers**.

## Working name
- CLI: `cargo poly-product`
- primary artifact: `polyglot-product-pack/v0`

## Scope
### This epic should own
- mixed-language product subject identity
- crate ↔ foreign package/component identity mapping
- imported host-package / FFI / component / release / support attachments
- diffable review points across releases / package lanes / platform matrices
- bounded release / support / policy / atlas / assistant handoffs
- verification of pack integrity and import references

### This epic should not own
- generating bindings itself
- choosing one universal IDL
- replacing PyO3, maturin, `napi-rs`, UniFFI, CXX, or component tooling
- registry hosting or package publication services
- universal ABI modeling
- a one-number interop/product score

## Candidate artifact family
### `polyglot-product-brief/v0`
Why the product exists, intended foreign-consumer set, lane classification, and freshness/review status.

### `polyglot-product-subject/v0`
The exact Cargo package / foreign package / module / bundle / addon / component identities, source revision, target matrix, and comparison base.

### `polyglot-product-pack/v0`
The portable bundle linking:
- imported `hostpkg-pack` attachments
- imported `ffi-pack` or component/WIT attachments
- imported release / distribution / signature / install attachments
- imported support/docs/import-transcript attachments
- local notes, waivers, and caveats
- integrity metadata

### `polyglot-product-diff/v0`
What changed between two review points, with separate sections for package identity, binding provenance, runtime/threading/lifetime posture, shipped artifacts, install receipts, and bounded downstream conclusions.

### `polyglot-product-handoff/v0`
Bounded consumer summaries for:
- release review
- support review
- policy / trust review
- atlas / adoption review
- assistant/editor rendering

## Recommended rollout
1. Python wheel lane
2. Node addon lane
3. UniFFI-generated mobile-binding lane
4. Rust/C++ handoff lane
5. Wasm component lane
6. bounded consumer handoff lane

This should be driven by [`design/polyglot-productization-pilot-program.md`](../design/polyglot-productization-pilot-program.md).

## What makes this epic “epic” rather than incremental
A merely incremental tool would improve one lane:
- better wheel metadata,
- better prebuild tooling,
- better generated mobile bindings,
- better C++ bridge ergonomics,
- or better component packaging.

An epic contribution here instead gives Rust one **portable mixed-language product contract** above those lanes.
That is strategically different because it can:
- make release/support/adoption consumers share the same subject and evidence boundary;
- let lane-specific tools stay specialized without pretending they define the whole product;
- keep native ABI, generated bindings, package metadata, install receipts, and support claims distinct but linked;
- and give atlas/policy/assistant consumers a bounded surface to import instead of re-scraping READMEs, CI logs, and package-manager folklore.

## Design principles
- **No fake one-lane winner.**
- **Imported boundary truth stays imported.**
- **Crate identity is not foreign package identity.**
- **Install receipts do not replace support truth.**
- **Partial lane coverage is explicit.**
- **Consumer summaries are lossy on purpose and say so.**
- **The stack remains thin.**

## Success conditions
This epic is succeeding when Rust teams can say:
- “this is the exact mixed-language product subject,”
- “here are the foreign package/component identities users actually install or import,”
- “here are the generated-binding, ABI/component, runtime, release, and support facts we imported,”
- “here are the package/install caveats and platform limits,”
- “here is what changed from the prior release,”
- and “here is what release/support/policy/atlas consumers may safely conclude,”

without inventing a bespoke packaging/support schema for every repository.

## Read this with
- `gaps/mixed-language-product-boundaries-crate-package-binding-runtime-and-support-truth.md`
- `design/polyglot-productization-stack.md`
- `design/polyglot-productization-pilot-program.md`
- `design/host-package-kit.md`
- `design/ffi-boundary-kit.md`
- `design/wasm-component-kit.md`
- `design/support-envelope-kit.md`
