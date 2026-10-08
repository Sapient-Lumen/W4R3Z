# Epic proposal: Encoding Surface Kit

## Thesis
One of the more worthy ecosystem contributions in Rust now would be a **portable review layer for encoding surfaces**.

Rust code constantly crosses boundaries between JSON, CBOR, human-readable config formats, compact binary formats, protobuf descriptors, archived zero-copy data, and lightweight specialized alternatives. But today those semantics are usually published only through crate names, derive attributes, build scripts, and bug lore.

Rust does not need one more generic serialization crate nearly as much as it needs a boring, explicit `encoding-pack/v0`.

## Why now
The timing is unusually good:
- Serde is still the dominant generic substrate,
- the reflection/comptime goal explicitly names serialization as an ecosystem area harmed by trait/derive lock-in,
- zero-copy/archive lanes like `rkyv` are increasingly serious and carry distinct validation semantics,
- `postcard` and similar crates keep `no_std` / constrained-environment encoding as a first-class need,
- lighter alternatives like `nanoserde` and `miniserde` show continued demand for different compile-time/runtime tradeoffs,
- `serde-reflection` shows users want version-controlled format descriptions,
- and the current `bincode` maintenance state is a concrete reminder that migration and replacement artifacts in this space are not optional theory.

That means the next major serialization seam is visible before it has converged.
This is exactly when a reviewable contract is more valuable than another implementation.

Sources:
- https://docs.rs/serde
- https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- https://docs.rs/postcard
- https://docs.rs/rkyv
- https://docs.rs/bytecheck
- https://docs.rs/nanoserde
- https://docs.rs/miniserde
- https://docs.rs/serde-reflection
- https://docs.rs/crate/bincode/latest
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## What should be built
A first credible version should ship:
1. `encoding-surface/v0`, `type-model-profile/v0`, `wire-format-profile/v0`, `borrow-zero-copy-profile/v0`, `canonicality-compat-profile/v0`, `stream-buffer-profile/v0`, `encoding-adapter-profile/v0`, `encoding-vector-set/v0`, `encoding-check-report/v0`, and `encoding-pack/v0`
2. one Serde-backed text-format pilot (JSON or RON)
3. one compact-binary / `no_std` pilot (`postcard`-style)
4. one schema/codegen-first pilot (`prost`-style)
5. one zero-copy/archive pilot (`rkyv` + validation)
6. one lighter-weight alternative pilot (`nanoserde` or `miniserde`-style)
7. docs and CI that make ordering, precision, compatibility, validation, and resource posture visible

The winning version is compact, semantic, and boundary-aware.
It should make encoding semantics legible together rather than canonizing one crate family.

## Initial pilots
- **Readable lane** — publish map-order, numeric-fidelity, and human-edit posture explicitly
- **Compact constrained lane** — publish `no_std`, no-allocation, and size-limit assumptions honestly
- **Schema/codegen lane** — publish descriptor/build-script/codegen assumptions and compatibility posture explicitly
- **Archive lane** — publish validation-before-use, layout/endian assumptions, and borrow-vs-own access truth
- **Migration lane** — record semantic differences when moving between dominant families or feature configurations

## Milestones
1. **v0 artifacts + vocabulary**
   - publish schemas and minimal examples
   - document model-family, wire-format, validation, and compatibility vocabulary
2. **v0.2 format-family pilots**
   - ship at least one readable, one compact, and one zero-copy pilot
   - show how ordered/canonical vs implementation-defined lanes differ in artifacts
3. **v0.3 schema/codegen + migration depth**
   - add descriptor/codegen and migration evidence
   - capture build-script/runtime/feature-flag dependencies explicitly
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the artifact family without sharing one identical format stack

## Success metrics
- Library authors can review encoding behavior without reconstructing it from derive attributes, README prose, and test fixtures.
- Applications can distinguish human-readable config, compact binary, schema/codegen, and archive/zero-copy lanes explicitly.
- Migrations between families or feature configurations become diffable instead of surprising.
- Embedded and constrained systems can publish resource-relevant encoding posture without inventing their own support matrix.
- Validation requirements for zero-copy/archive lanes become attachable capability claims instead of hidden assumptions.

## Archive fit
This proposal fills a real gap in the archive:
- **Schema Contract Kit** handles contract identity and evolution,
- **Protocol Surface Kit** handles transport/session/security posture,
- **Validity Surface Kit** handles invalid-value and layout-safety truth,
- **Runtime Settings Kit** handles configuration-source semantics,
- **Time Surface Kit** handles temporal meaning,
- **Diagnostic Surface Kit** handles failure/reporting surfaces.

But none of those is the portable contract for **what encoding model was chosen, what the bytes/text mean, what borrow/validation/canonicality assumptions apply, and what evidence backs those claims**.
Encoding Surface Kit is the missing substrate above Rust’s increasingly fragmented and increasingly strategic encoding ecosystem.
