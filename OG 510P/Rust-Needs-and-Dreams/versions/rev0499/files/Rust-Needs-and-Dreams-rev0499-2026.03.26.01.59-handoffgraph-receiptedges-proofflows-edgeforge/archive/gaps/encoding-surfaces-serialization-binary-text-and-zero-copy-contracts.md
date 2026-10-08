# Gap: encoding surfaces, serialization semantics, and reviewable binary/text contracts

## What is missing
Rust has many strong serialization and encoding building blocks, but the ecosystem still lacks a **portable way to publish what an encoding surface actually means**.

Today there is no standard way to say:
- whether a boundary uses a generic Serde-style data model, a schema-first/IDL-driven model, a zero-copy archived layout, or a lightweight format-specific model,
- whether the encoded form is text or binary, self-describing or schema-dependent, canonical or merely implementation-defined,
- whether decoding is owned, borrowed, zero-copy, validated-before-use, stream-oriented, or whole-buffer only,
- what map-order, numeric-precision, endianness, varint/fixed-int, trailing-byte, unknown-field, or framing assumptions apply,
- whether a format is viable in `no_std`, `no_alloc`, reader/writer, or async-streaming settings,
- how much of the public story comes from derives, code generation, format reflection, manual impls, or build-script toolchains,
- what migration and compatibility claims exist across releases or across alternative format families,
- and what evidence actually ran: round trips, malformed-input vectors, cross-version fixtures, canonicalization vectors, or zero-copy validation checks.

That gap matters because Rust’s encoding ecosystem is no longer a simple “just use Serde” story.
Serde is the generic substrate, but `postcard` is `no_std`-oriented, `RON` is human-readable, `ciborium` is CBOR over readers and writers, `serde_json` exposes ordering/precision feature choices, `prost` is schema/codegen-first, `rkyv` is zero-copy with validation concerns, and crates like `nanoserde` and `miniserde` deliberately trade away generality for smaller build/runtime footprints.

So the missing contribution is not another format crate.
It is a **reviewable encoding-surface layer** for publishing type-model posture, wire-format semantics, borrow/zero-copy rules, canonicality/compatibility claims, and evidence honestly.

Sources:
- https://docs.rs/serde
- https://docs.rs/postcard
- https://docs.rs/ron
- https://docs.rs/ciborium
- https://docs.rs/serde_json
- https://docs.rs/prost
- https://docs.rs/rkyv
- https://docs.rs/bytecheck
- https://docs.rs/nanoserde
- https://docs.rs/miniserde
- https://docs.rs/serde-reflection
- https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## The current seam is awkward
Rust already has several real encoding subcultures, but their semantics do not line up cleanly:
- Serde defines a generic data model and derive-driven interoperability layer across many text and binary formats,
- `serde_json` can preserve insertion order in `Value` and exposes features for arbitrary-precision numbers and raw JSON retention, so even “JSON support” is not one single posture,
- `postcard` is explicitly optimized for `#![no_std]` use in constrained environments,
- `RON` is explicitly human-readable and aims to support all of Serde’s data model,
- `ciborium` centers CBOR over reader/writer-style APIs and dynamic value handling,
- `prost` is protobuf-first and build/codegen-driven rather than “generic data model first,”
- `rkyv` is zero-copy, supports `no_std` and `no_alloc`, supports in-place mutation, and pushes validation concerns into separate lanes like `bytecheck`,
- `nanoserde` explicitly rejects Serde’s intermediate data model in favor of smaller build trees and format-specific derives,
- `miniserde` is JSON-only and intentionally supports only a restricted subset of data shapes and customization,
- and `serde-reflection` exists specifically because teams want version-controlled format descriptions to detect accidental binary-format drift.

The new reflection/comptime goal makes this even more strategic: it explicitly names serialization crates as one of the ecosystem areas hurt by trait/derive lock-in and argues that maintainers often do not want to depend on multiple serialization stacks.

So the ecosystem is not missing raw encode/decode implementations.
It is missing the **artifact family that records which encoding model a public surface actually chose, what invariants and tradeoffs it assumes, and what evidence checked those claims**.

Sources:
- https://docs.rs/serde
- https://docs.rs/serde_json
- https://docs.rs/postcard
- https://docs.rs/ron
- https://docs.rs/ciborium
- https://docs.rs/prost
- https://docs.rs/rkyv
- https://docs.rs/bytecheck
- https://docs.rs/nanoserde
- https://docs.rs/miniserde
- https://docs.rs/serde-reflection
- https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html

## Why this matters
This gap matters because encoding semantics cut across a huge share of the Rust ecosystem at once:
1. **public configuration, storage, and wire formats** — “serialize this type” is not the same as specifying map order, numeric fidelity, or future compatibility;
2. **resource-constrained systems** — `no_std`, no-allocation, and small-build-tree choices materially change what formats are viable;
3. **schema-driven systems** — protobuf or registry-backed systems care about codegen, descriptors, and compatibility reasoning that do not fit generic data-model-only thinking;
4. **zero-copy and high-performance systems** — archived layouts, validation-before-use, and endian/layout assumptions are public support claims, not internal implementation details;
5. **human-facing workflows** — debugability, editability, and transcript readability differ sharply between JSON/CBOR/RON/binary archive lanes;
6. **migration risk** — changing formats or even feature flags can silently change ordering, precision, canonicality, or compatibility behavior.

A worthy contribution here is therefore not another derive crate or binary codec.
It is a way to treat **encoding surfaces as reviewable ecosystem infrastructure**.

Sources:
- https://docs.rs/serde
- https://docs.rs/postcard
- https://docs.rs/ron
- https://docs.rs/ciborium
- https://docs.rs/prost
- https://docs.rs/rkyv
- https://docs.rs/nanoserde
- https://docs.rs/miniserde
- https://docs.rs/serde-reflection
- https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html

## What “good” looks like
A worthy contribution here is **not** one fake universal serialization badge.
It is a shared encoding-surface boundary:
- one `encoding-surface/v0` describing the top-level encoding family and intended use,
- one `type-model-profile/v0` describing generic-data-model vs schema/IDL vs archived-layout vs lightweight-format-specific posture,
- one `wire-format-profile/v0` describing text/binary/self-describing/schema-dependent framing, integer/endianness/ordering rules, and size limits,
- one `borrow-zero-copy-profile/v0` describing owned/borrowed/archive access, validation requirements, and alignment/layout assumptions,
- one `canonicality-compat-profile/v0` describing deterministic ordering, precision/canonical forms, unknown-field and trailing-byte policy, and compatibility expectations,
- one `stream-buffer-profile/v0` describing reader/writer, incremental, slice-only, and async-adapter posture,
- one `encoding-adapter-profile/v0` describing bridges between Serde, protobuf/codegen, archive/zero-copy, and lightweight alternative stacks,
- one `encoding-vector-set/v0` describing round-trip, malformed-input, canonicalization, cross-version, and validation vectors,
- one `encoding-check-report/v0` recording which vectors actually ran,
- and one `encoding-pack/v0` bundle for docs, CI, migration notes, fixtures, and archaeology.

That would let Rust teams reason about encoding choices with **explicit artifacts** instead of a brittle mix of derive attributes, crate names, feature flags, and folklore.

## Non-goals
This gap should not be used to:
- replace Serde, protobuf implementations, archive/zero-copy frameworks, or existing format crates,
- define one canonical byte format for the ecosystem,
- flatten schema-first, generic-data-model, archive-layout, and lightweight-specialized lanes into one fake manifest,
- or pretend that compatibility, canonicality, and validation are solved by a single “serialize/deserialize” trait pair.

The job is smaller and sharper:
**make encoding surfaces legible, honest, and checkable across text/binary/schema/zero-copy/lightweight lanes.**
