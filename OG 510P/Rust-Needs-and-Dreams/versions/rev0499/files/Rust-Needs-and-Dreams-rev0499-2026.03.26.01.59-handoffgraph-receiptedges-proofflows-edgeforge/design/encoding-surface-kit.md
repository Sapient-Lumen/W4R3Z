# Design: Encoding Surface Kit (`cargo encodecheck`, `encoding-pack/v0`)

## Goal
Define a portable contract for specifying, validating, diffing, and reviewing **encoding surfaces** in Rust: type-model posture, wire-format semantics, borrow/zero-copy rules, canonicality/compatibility claims, streaming/buffer assumptions, migration posture, and the evidence that those claims were actually checked.

This should help answer questions like:
- is this boundary using a generic Serde-style data model, a schema/IDL-first model, an archived layout, or a lightweight format-specific derive system,
- is the encoded form text or binary, self-describing or descriptor/schema-backed,
- are values decoded by allocation, borrowing, archive access, or stream processing,
- what map-order, numeric-fidelity, endianness, framing, trailing-byte, and unknown-field rules apply,
- whether the format is viable in `std`, `alloc`, `no_std`, `no_alloc`, reader/writer, or async-adapter settings,
- and what malformed-input, canonicalization, cross-version, and validation vectors actually ran.

It should **not** replace format crates, code generators, or IDLs.
It should make encoding semantics reviewable and comparable.

## References (signals)
- Serde is the generic serialization substrate and explicitly describes its split between data structures and data formats.
  https://docs.rs/serde
- The reflection/comptime goal explicitly says serialization/logging/game-engine ecosystems are hindered because maintainers do not want to depend on multiple derive/trait stacks, and names serialization as a motivating case for reflection-based interop.
  https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- The 2025 Rust survey says resource usage (including slow compile times and storage usage) remains a major productivity problem, which keeps lighter-weight or lower-overhead encoding lanes strategically relevant.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `postcard` is a `#![no_std]`-focused Serde format for constrained environments.
  https://docs.rs/postcard
- `RON` is a readable format that aims to support all of Serde’s data model.
  https://docs.rs/ron
- `ciborium` is a Serde-backed CBOR implementation with reader/writer and dynamic-value lanes.
  https://docs.rs/ciborium
- `serde_json` exposes behavior-changing feature choices like insertion-order preservation and arbitrary-precision numeric handling.
  https://docs.rs/serde_json
- `prost` is protobuf-first, codegen/build-oriented, and distinct from generic-data-model-first lanes.
  https://docs.rs/prost
- `rkyv` is a zero-copy framework with `no_std`/`no_alloc` support, archived layouts, and in-place access/mutation lanes.
  https://docs.rs/rkyv
- `bytecheck` exists because validating potentially-invalid bytes before treating them as values is a distinct concern in zero-copy/archive worlds.
  https://docs.rs/bytecheck
- `serde-reflection` extracts format descriptions and explicitly supports storing them under version control to catch unintended format drift.
  https://docs.rs/serde-reflection
- `nanoserde` and `miniserde` show that smaller or simpler alternative serialization models remain attractive, but with explicitly narrower tradeoff envelopes.
  https://docs.rs/nanoserde
  https://docs.rs/miniserde
- The current `bincode` crate page now says the crate is unmaintained and points users toward alternatives such as `postcard` and `rkyv`, which is unusually concrete evidence that migration and replacement paths in this area are not hypothetical.
  https://docs.rs/crate/bincode/latest

## Core components

### 1) `encoding-surface/v0`
Top-level identity for one published encoding boundary.

Fields:
- stable surface id
- crate / package / module ownership
- intended use (`config`, `storage`, `wire`, `ipc`, `cache`, `snapshot`, `archive`, `debug-human`, `other`)
- primary model family (`serde-generic`, `schema-idl`, `archived-layout`, `lightweight-format-specific`, `hybrid`)
- primary format family (`json`, `cbor`, `ron`, `postcard-like`, `protobuf`, `archive`, `custom-binary`, `other`)
- stability/support statement
- raw artifact attachments

### 2) `type-model-profile/v0`
Describe the conceptual model of serialization.

Fields:
- derivation mode (`derive`, `manual`, `codegen`, `reflection-extracted`, `mixed`)
- type vocabulary source (`rust-types`, `serde-data-model`, `descriptor-schema`, `archived-layout`, `other`)
- whether external schemas/descriptors exist
- customization lanes (attributes, manual impls, codegen options, plugin hooks)
- shape restrictions (for example: struct-only, enum restrictions, no generics, no custom impls)
- feature/channel/MSRV posture

### 3) `wire-format-profile/v0`
Describe encoded representation semantics.

Fields:
- representation family (`text`, `binary`, `mixed`)
- self-description / schema dependence
- framing mode (`whole-value`, `stream`, `delimited`, `length-prefixed`, `descriptor-coupled`, `other`)
- map-order / field-order posture
- numeric posture (float precision, arbitrary precision, integer encoding, endianness)
- trailing-byte / unknown-field / duplicate-key policy
- size/limit controls
- human-edit/debug posture

### 4) `borrow-zero-copy-profile/v0`
Describe how bytes become usable values.

Fields:
- decode posture (`owned`, `borrowed`, `archive-access`, `mixed`)
- allocation requirements (`std`, `alloc`, `no_alloc` compatibility)
- validation requirement (`none`, `recommended`, `required-before-use`)
- alignment/layout/endian assumptions
- mutable-in-place posture
- invalidation / aliasing notes
- attachment to Validity Surface Kit artifacts if applicable

### 5) `canonicality-compat-profile/v0`
Describe determinism and compatibility truth.

Fields:
- canonical-form claim (`none`, `best-effort`, `strict`)
- order/precision determinism notes
- cross-version policy (`same-version-only`, `same-major`, `explicit-vector-only`, `descriptor-compat`, `other`)
- unknown-field compatibility posture
- schema / descriptor / reflection attachment ids
- migration notes / successor hints

### 6) `stream-buffer-profile/v0`
Describe operational I/O posture.

Fields:
- input/output shapes (`slice`, `Vec`, `Read`, `Write`, `Buf`, `BufMut`, async adapter, in-memory only)
- incremental parsing / emission support
- buffering/backpressure assumptions
- maximum-size / limit-enforcement posture
- fallibility / error-detail posture
- embedded / constrained-environment notes

### 7) `encoding-adapter-profile/v0`
Describe bridges between ecosystems.

Fields:
- source family and destination family
- lossy vs lossless classification
- preserved and dropped semantics (ordering, precision, descriptors, zone/calendar information for dependent domains, canonical form)
- build/codegen/runtime requirements
- performance / allocation / validation caveats
- migration suitability

### 8) `encoding-vector-set/v0`
Portable test vectors.

Fields:
- round-trip vectors
- malformed-input vectors
- canonicalization / deterministic-output vectors
- cross-version / compatibility vectors
- stream/buffer vectors
- validation-required vectors for zero-copy lanes
- adapter parity vectors

### 9) `encoding-check-report/v0`
Results of running declared vectors.

Fields:
- vector ids executed
- environment (OS, target, Rust toolchain, feature flags, endianness if relevant)
- participating crate versions
- outcomes (`pass`, `fail`, `unsupported`, `inconclusive`, `skipped`)
- failure classes (`ordering-drift`, `precision-loss`, `unknown-field-mismatch`, `trailing-byte-mismatch`, `validation-failure`, `allocation-mismatch`, `other`)
- fixture attachments / logs

### 10) `encoding-pack/v0`
Bundle format:
- `encoding-surface/v0`
- one or more `type-model-profile/v0`
- one or more `wire-format-profile/v0`
- zero or more `borrow-zero-copy-profile/v0`
- one or more `canonicality-compat-profile/v0`
- zero or more `stream-buffer-profile/v0`
- zero or more `encoding-adapter-profile/v0`
- one `encoding-vector-set/v0`
- one or more `encoding-check-report/v0`
- raw fixtures / schemas / descriptors / reflection dumps / migration notes

## Reference UX: `cargo encodecheck`
- `cargo encodecheck inspect`
  - discover likely model families, format crates, features, descriptor/codegen use, and zero-copy/validation lanes
- `cargo encodecheck check`
  - run declared vectors and emit `encoding-check-report/v0`
- `cargo encodecheck diff <A> <B>`
  - compare two packs or versions and explain semantic drift
- `cargo encodecheck doctor`
  - explain likely ambiguity points: map ordering, precision loss, borrow-vs-own decode, validation requirements, stream-vs-buffer mismatch
- `cargo encodecheck pack`
  - bundle an `encoding-pack/v0`

`cargo encodecheck` should begin as an orchestrator / validator / packer. It should avoid becoming a new format crate, schema registry, or universal derive framework.

## Default policy
- **Model family must be explicit.**
- **Text/binary and self-describing/schema-dependent posture must be explicit.**
- **Borrowed/zero-copy lanes must publish validation requirements.**
- **Canonicality and compatibility claims must be attached, not implied.**
- **Feature-flag-driven semantic differences must be recorded.**
- **Unsupported or intentionally lossy adapters are valid outcomes if they are made explicit.**

## What the kit should provide to others
- **Application authors:** a way to publish whether a boundary is human-readable, compact binary, schema-first, or archive-like.
- **Library authors:** a way to document public encoding behavior without forcing a single ecosystem monopoly.
- **Embedded teams:** a way to record `no_std`, no-allocation, and constrained-I/O posture honestly.
- **Storage / wire / cache maintainers:** a way to state what ordering, precision, and compatibility guarantees actually hold.
- **Migration work:** a way to compare Serde-based, protobuf-based, archive-based, and lightweight alternatives explicitly.

## Overlap boundaries
- **Not Schema Contract Kit:** that kit owns contract identity, compatibility reports, and raw schema/service boundary artifacts; Encoding Surface Kit owns the meaning of the concrete encoded representation once a type model or schema exists.
- **Not Validity Surface Kit:** that kit owns invalid-value and layout-safety truth; this kit only records where validation and archived-layout assumptions intersect public encoding behavior.
- **Not Protocol Surface Kit:** that kit owns transport/session/security posture; this kit owns message representation semantics.
- **Not Runtime Settings Kit:** that kit owns setting sources and precedence; this kit owns how settings are concretely represented and parsed once serialized.
- **Not Time Surface Kit:** that kit owns the semantics of temporal values; this kit owns how any values, including temporal ones, are represented over bytes/text.

## Hard problems (explicitly scoped)
1. **One “serialization” word hides multiple ecosystems**
   - generic-data-model, schema-first, archive-layout, and lightweight-specialized lanes must remain distinct.
2. **Feature flags can change semantics**
   - ordering, precision, or validation posture may differ without changing crate names.
3. **Zero-copy is not just “fast deserialization”**
   - alignment, endian, and validation assumptions have to be published or teams will overclaim safety.
4. **Migration is often semantic, not syntactic**
   - swapping formats or libraries may alter compatibility, human readability, and failure modes.
5. **Build/runtime costs matter**
   - derive-heavy and zero-dependency alternatives are both real ecosystem strategies, not edge cases.

## Evaluation plan
Pilot on:
1. one Serde + JSON or RON human-readable config boundary,
2. one `postcard` or similar compact `no_std` lane,
3. one `prost` or other schema/codegen-driven wire boundary,
4. one `rkyv` + `bytecheck` zero-copy/archive lane,
5. one lighter-weight alternative such as `nanoserde` or `miniserde` where reduced scope is part of the public tradeoff.

Success bar:
- projects can publish encoding assumptions without inventing their own schema,
- reviewers can tell generic-data-model, schema-first, archive, and lightweight-specialized lanes apart,
- ordering/precision/compatibility/validation drift becomes visible before release,
- and the ecosystem gets a reusable boundary above today’s fragmented encoding stacks without flattening meaningful differences.
