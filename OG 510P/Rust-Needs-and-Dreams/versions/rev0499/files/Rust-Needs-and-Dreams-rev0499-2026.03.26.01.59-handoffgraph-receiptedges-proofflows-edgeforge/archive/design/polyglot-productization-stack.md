# Design note: Polyglot Productization Stack (FFI Boundary + Host Package + Wasm Component + Release Truth + Support Envelope)

## Goal
Define the **division of labor and consumer flow** between Rust native boundaries, foreign-host packages, Wasm components, shipped artifacts, and support/docs claims so the ecosystem can make **mixed-language Rust products** reviewable without anointing one universal binding framework, one package manager, or one IDL as the answer.

This is **not** a new mega-framework.
It is a stack note explaining how existing archive pieces should compose:
- [`design/ffi-boundary-kit.md`](./ffi-boundary-kit.md)
- [`design/host-package-kit.md`](./host-package-kit.md)
- [`design/wasm-component-kit.md`](./wasm-component-kit.md)
- [`design/release-pipeline-kit.md`](./release-pipeline-kit.md)
- [`design/signed-binaries-kit.md`](./signed-binaries-kit.md)
- [`design/distribution-contract-stack.md`](./distribution-contract-stack.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)
- [`design/docproof-kit.md`](./docproof-kit.md)
- [`design/schema-contract-kit.md`](./schema-contract-kit.md)

## Why this note is needed now
Rust’s current signals are no longer saying only “interop is possible.” They are saying Rust already has serious host-language lanes, but still lacks the **productization layer above them**:
- Rust’s safety-critical writeup explicitly says many teams will integrate Rust into existing C and C++ systems and carry that boundary for years, and that auditable, in-sync interfaces need better tooling.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The 2025H2 C++/Rust interop problem-mapping goal says the near-term reality is not rewriting significant C++ estates, but cooperating across language communities on the technical issues that mixed-language systems actually hit.
  https://rust-lang.github.io/rust-project-goals/2025h2/interop-problem-map.html
- Python already has a credible Rust packaging lane: PyO3 recommends `maturin`, and maturin is explicit that portability and manylinux/musllinux compliance are part of the product surface.
  https://pyo3.rs/main/
  https://www.maturin.rs/distribution.html
- Node already has a stable-ABI lane via Node-API, but the official docs also spell out that the guarantee stops at the Node-API boundary and does not automatically extend to V8, libuv, or arbitrary external libraries.
  https://nodejs.org/api/n-api.html
- UniFFI already spans Kotlin, Swift, and Python and is explicit about thread-safety and lifetime restrictions in generated bindings. That means the host-language story is real, but lane-specific.
  https://mozilla.github.io/uniffi-rs/latest/Getting_started.html
  https://mozilla.github.io/uniffi-rs/latest/internals/design_principles.html
- CXX documents both Cargo-based and other-build-system paths and even requires the Rust-side and C++-side generated bindings to use the same CXX release. That is exactly the kind of generation/runtime/build truth that should not stay trapped in prose.
  https://cxx.rs/build/cargo.html
  https://cxx.rs/build/other.html
- The WebAssembly Component Model now explicitly treats cross-language interoperability as the point, using WIT plus a standardized ABI. That is a polyglot lane too, but it should stay distinct from native ABI/package lanes.
  https://component-model.bytecodealliance.org/design/why-component-model.html
  https://component-model.bytecodealliance.org/composing-and-distributing/composing.html
- The 2025 State of Rust survey says official online docs remain canonical while organizations continue hiring Rust developers. That is a useful combination: growing structural adoption plus a need for machine-usable canonical truth rather than more README folklore.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

Together these signals justify treating polyglot productization as a **frontier-worthy ecosystem seam** instead of leaving Rust mixed-language products as a pile of binding generators, package manifests, CI upload steps, and support tickets.

## Stack layers

### 1) Boundary truth: FFI Boundary and Wasm Component stay distinct
- **FFI Boundary Kit** owns symbols, ownership/layout contracts, generated native bindings, and ABI drift.
- **Wasm Component Kit** owns WIT/package/composition/registry truth.

Design rule: **do not flatten native ABI boundaries and WIT/component boundaries into one fake universal interop model**.

### 2) Host package truth: what foreign consumers actually install/import
**Host Package Kit** owns the package/module/bundle layer foreign consumers see:
- package names/scopes/modules/namespaces
- generated JS/TS stubs, Swift/Kotlin packages, Python wheels/sdists
- imported boundary artifacts
- runtime / interpreter / ABI / SDK matrices
- checked install/import evidence

Design rule: **crate identity is not the same thing as foreign package identity**.

### 3) Data/type truth: schemas and lifted/lowered types
Where foreign lanes depend on structured data or generated type surfaces, **Schema Contract** should attach:
- record/enum/message identities
- evolution posture
- cross-language type lossiness
- generated type-surface evidence

Design rule: **host package truth must not silently become the owner of semantic data-schema truth**.

### 4) Release/install truth: what got shipped and where
**Release Truth** and **Distribution Contract** own:
- artifact publication
- signatures/provenance
- channel/fallback/install receipts
- mirror/offline posture where relevant

This layer answers questions like:
- “Which wheel/prebuild/component/staticlib/header set was actually shipped?”
- “What did the consumer install?”
- “Which provenance or signature evidence exists?”

Design rule: **host-package metadata alone does not prove artifact provenance or install behavior**.

### 5) Support/docs truth: what is actually supported
**Support Envelope** and **DocProof** own:
- runtime floors and support matrices
- source-build vs released-artifact posture
- docs/examples/import transcripts
- cfg/target/platform caveats
- support conclusions for humans and tools

Design rule: **one successful local import or demo app run is not the support contract**.

### 6) Downstream consumers
The stack becomes worthy when real consumers can import it without flattening it:
- **Release/review** consumers can attach polyglot product facts to releases.
- **Support/docs** consumers can explain interpreter/ABI/platform caveats honestly.
- **Atlas/commons** consumers can map Rust’s host-language lanes without pretending there is one winner.
- **Policy/trust** consumers can reason about shipped foreign artifacts and support claims with provenance.

Design rule: **consumers import selected evidence; they do not redefine polyglot truth**.

## What an epic contribution should look like in practice
A worthy contribution here is not “build the universal Rust bindings framework.”
It is a portable, reviewable stack with clear boundaries:
1. prove one host-package lane (Python or Node) end to end;
2. attach explicit runtime/threading/ABI/support truth;
3. import native or component boundary artifacts rather than redefining them;
4. attach release/install/support evidence;
5. show one downstream consumer (support, release, policy, atlas) can ingest the results honestly.

An eventual aggregate artifact may exist, but it should be a **thin pack of referenced artifacts**, not a new truth engine that erases the lane boundaries.


## Reference proposal direction
The stack now also has an explicit proposal-layer candidate: [`proposals/epic-polyglot-productization-stack.md`](../proposals/epic-polyglot-productization-stack.md).
That proposal keeps the stack thin by introducing `cargo poly-product` / `polyglot-product-pack/v0` above imported `hostpkg-pack`, `ffi-pack` or component/WIT facts, release/install receipts, and support/docs evidence rather than replacing any lane-specific generator or package tool.

## Ranked first execution lanes
1. **Python package lane family** — split first by full-API extension, then `abi3`, then free-threaded, then async-bridge posture; see [`design/python-host-lane-map.md`](./python-host-lane-map.md)
2. **Node addon lane** — strong ABI lesson with explicit caveats
3. **UniFFI mobile binding lane** — exposes thread/lifetime/generated-binding reality clearly
4. **C/C++ handoff lane** — imports FFI truth into external build/release/support flows
5. **Wasm component lane** — imports WIT/component truth into the same release/support conversation

## Non-goals
- one universal IDL or generated-binding framework;
- replacing PyO3, maturin, `napi-rs`, UniFFI, CXX, or component-model tooling;
- flattening Python, Node, mobile bindings, native handoff, and components into one fake “bindings supported” badge;
- treating package metadata alone as support, release, or provenance truth.

## Archive implications
- The archive should now treat **FFI Boundary + Host Package + Wasm Component + Release Truth + Support Envelope** as a coupled **Polyglot Productization Stack** in frontier discussions.
- Future revisions should prefer **crate-vs-foreign-package identity, binding provenance, runtime/init/threading truth, shipped-artifact truth, and support/docs truth** over another lane-specific package wrapper or universal binding dream.
- When Release, Support, Atlas, Policy, or Trust work cites mixed-language readiness, they should import **boundary truth**, **package truth**, **artifact truth**, and **support truth** separately.
