# Cross-language interop frontier map — 2026-03-22

This note exists so future archive passes keep the interop territory broad **without** duplicating the same crate idea under ten different packaging stories.

## Core judgment

The archive’s best interop opportunities now split into **four distinct layers**.

### Layer 1 — shared boundary-contract truth
This is **P-0121 FFI Boundary & Bindings Conformance Kit**.

It should own the questions another downstream team asks first:

- what representation crosses the boundary,
- who is the source of truth for that representation,
- how ownership/teardown work,
- how errors/panics/exceptions cross,
- and which surfaces are actually checked.

### Layer 2 — specialized delivery / shipkit workflows
These are language- or platform-specific packaging lanes such as:

- Apple XCFramework / SwiftPM shipping,
- Node-API package prebuilds,
- JNI/JAR shipping,
- NuGet native interop,
- R package native shipping,
- RubyGems native extension shipping.

These lanes should **reuse** P-0121 boundary vocabulary where possible instead of re-specifying ownership/error/layout truth from scratch.

### Layer 3 — plugin / component boundaries
These are not just “another FFI.”
They add lifecycle, capabilities, sandboxing, and composition concerns.

- **P-0081 Stable Plugin Host Kit**
- **P-0002 Wasm Plugin Kit**
- component-model / WIT distribution lanes

These should stay distinct from P-0121 even when they borrow some boundary vocabulary.

### Layer 4 — language-runtime attachment lanes
These are cases where the boundary is inseparable from a language runtime or host process model.
Examples include Python interpreter attachment, Java/JNI lifecycle rules, Node event-loop expectations, or other VM/runtime obligations.

These may deserve their own shipkits or support contracts, but they should still import the common truths from P-0121 where possible.

## Why this map got sharper

Current official and ecosystem sources make the layer split more believable than before:

- the Rust project is explicitly organizing around **Cross-language interop** as an application area;
- the safety-critical Rust write-up explicitly treats C/C++ boundaries as long-lived audit surfaces;
- `cxx` now makes shared-vs-opaque representation differences concrete;
- UniFFI documents explicit object-reference, async, and error paths;
- Diplomat documents explicit opacity and limited supported surface area;
- WIT and the Canonical ABI make interface/type authority explicit for components.

## Practical ranking inside interop

1. **P-0121 FFI Boundary & Bindings Conformance Kit**
2. **P-0081 Stable Plugin Host Kit**
3. **P-0002 Wasm Plugin Kit**
4. language-specific shipkits that reuse the above vocabulary

## What a worthy interop crate should provide other people

A worthy interop crate should usually give another team at least one of these:

- a compact receipt that replaces README folklore,
- a conservative report that exposes weaker/manual-review zones,
- a diff artifact for release review,
- or a portable handoff bundle that survives CI and organizational boundaries.

If a candidate cannot produce one of those, it is often still a useful tool — but not yet the kind of “epic missing crate” this archive is prioritizing.

## Freshness anchors

- program-management update — https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- safety-critical Rust — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- `cxx` docs — https://cxx.rs/
- UniFFI docs — https://mozilla.github.io/uniffi-rs/
- Diplomat book — https://rust-diplomat.github.io/book/
- component model docs — https://component-model.bytecodealliance.org/
