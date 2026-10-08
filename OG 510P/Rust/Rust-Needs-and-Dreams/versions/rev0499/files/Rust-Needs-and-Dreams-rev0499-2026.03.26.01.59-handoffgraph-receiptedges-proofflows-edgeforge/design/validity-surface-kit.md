# Design: Validity Surface Kit (`cargo validity`, `validity-pack/v0`)

## Goal
Define a portable contract for specifying, validating, diffing, and reviewing **validity surfaces** in Rust: type initialization invariants, invalid values and niches, byte/layout assumptions, FFI ingress expectations, unsafe field invariants, and the evidence that those claims were actually checked.

This should help answer questions like:
- can any initialized byte pattern represent this type, or only some checked subset,
- which invalid values or niches matter for this boundary,
- where are validity checks performed,
- which assumptions are type-level versus library-level,
- how do raw-byte, foreign, checked, and owned Rust forms relate,
- and what evidence exists for those claims across compile-time, runtime, and mixed-language tests.

It should **not** replace Rust’s formal semantics, sanitizers, or verification tools.
It should make validity assumptions reviewable and comparable.

## References (signals)
- The `std` contracts goal explicitly says safety contracts define preconditions, postconditions, and invariants, and that contract attributes should be convertible into runtime checks and exposed to external tools.
  https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
- The unsafe-fields goal exists because Rust currently lacks mechanisms for denoting fields that carry library safety invariants.
  https://rust-lang.github.io/rust-project-goals/2025h1/unsafe-fields.html
- The comprehensive niche-checks goal says invalid values should ideally be checked at load-time or on function entry and explicitly motivates this with unsafe Rust and FFI.
  https://rust-lang.github.io/rust-project-goals/2025h2/comprehensive-niche-checks.html
- The sanitizer stabilization goal says unsafe Rust and foreign code in mixed-language binaries do not enjoy the same safety guarantees and therefore need better sanitizer support.
  https://rust-lang.github.io/rust-project-goals/2025h2/stabilization-of-sanitizer-support.html
- The 2026 flagships explicitly elevate safety-critical tooling, specifications, and evidence for functional safety.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- `MaybeUninit` docs state that the compiler assumes values are properly initialized according to their type requirements, and give references as an example of types that must be aligned and non-null.
  https://doc.rust-lang.org/std/mem/union.MaybeUninit.html
- `zerocopy` and `bytemuck` already demonstrate that ecosystems need machine-readable vocabularies for layout validity, byte validity, zero validity, and checked bit patterns.
  https://docs.rs/zerocopy
  https://docs.rs/bytemuck
- `abi_stable` shows that load-time boundary validation matters for separately compiled code.
  https://docs.rs/abi_stable

## Core components

### 1) `validity-surface/v0`
A top-level declaration of the validity-bearing thing being described:
- crate + module identity
- type / boundary / adapter identity
- representation lane (`native-rust`, `repr-c`, `wire`, `byte-view`, `ffi-export`, `ffi-import`, `plugin-load`, `other`)
- intended consumers (Rust-only, mixed-language, zero-copy, load-time checked, etc.)
- linked profiles and attached evidence

Design rule: begin with the **surface that makes assumptions**, not the checker.

### 2) `niche-profile/v0`
Describes invalid values and bit-pattern restrictions:
- invalid discriminants / impossible enum tags
- invalid scalar values (null, zero, reserved ranges, sentinels)
- whether any bit pattern is valid, zero is valid, or only a checked subset is valid
- whether padding / uninitialized bytes are allowed internally
- endianness-sensitive conditions when relevant
- source of truth (`manual`, `derive`, `compiler`, `generated`, `other`)

Design rule: do not collapse “any bit pattern”, “checked subset”, and “valid when constructed another way” into one badge.

### 3) `layout-validity-profile/v0`
Describes layout assumptions that matter to validity:
- repr posture
- alignment assumptions
- padding posture
- metadata / DST assumptions
- size / field ordering facts when relevant
- cross-language or dynamically loaded layout expectations

Design rule: layout truth is not the same as semantic truth, but it is often a prerequisite for it.

### 4) `boundary-ingress-profile/v0`
Describes where and how invalid values are caught or assumed:
- ingress kinds (`constructor`, `parser`, `ffi-entry`, `load-time`, `deserializer`, `adapter`, `none`)
- check timing (`compile-time`, `construction`, `entry`, `load`, `lazy`, `never`)
- check engine (`manual`, `derive`, `contracts`, `sanitizer`, `miri`, `native-loader`, `other`)
- assumptions delegated to caller / producer
- mixed-language caveats

Design rule: “validated somewhere” is not enough; the timing and locus of the check matters.

### 5) `unsafe-invariant-profile/v0`
Describes library-level invariants that exceed type initialization:
- fields carrying safety invariants
- representation coupling (e.g. `len` / initialized prefix relationships)
- aliasing or ownership assumptions relevant to validity
- relationship to future `unsafe` fields or contract attributes
- red flags requiring unsafe review

Design rule: keep type validity and library invariants separate, but linked.

### 6) `validity-adapter-profile/v0`
Describes conversion lanes and their costs:
- raw bytes → checked Rust form
- raw bytes → unchecked Rust form
- foreign ABI form → checked Rust form
- dynamically loaded form → checked ABI-stable wrapper
- zero-copy borrowed form ↔ owned normalized form
- what validation is added, skipped, or deferred

Design rule: adapters should publish **what they prove** and **what they merely assume**.

### 7) `validity-vector-set/v0`
A catalog of checks that should run:
- compile-fail misuse vectors
- unit/property/fuzz vectors for invalid values
- Miri vectors
- sanitizer vectors
- mixed-language ingress vectors
- load-time / plugin / dylib vectors
- checked-load or contract vectors when available

### 8) `validity-check-report/v0`
Portable outcome artifact:
- toolchain / engine / version info
- vectors attempted and outcome (`passed`, `failed`, `unsupported`, `inconclusive`, `skipped`)
- failure classes (`invalid-value-ingress`, `layout-mismatch`, `unchecked-padding`, `aliasing-violation`, `contract-failure`, `other`)
- attachments to logs or repro packs
- comparability metadata for diffs

### 9) `validity-pack/v0`
Bundle format:
- `validity-surface/v0`
- zero or more `niche-profile/v0`
- zero or more `layout-validity-profile/v0`
- zero or more `boundary-ingress-profile/v0`
- optional `unsafe-invariant-profile/v0`
- zero or more `validity-adapter-profile/v0`
- one `validity-vector-set/v0`
- one or more `validity-check-report/v0`
- raw attachments (generated headers, byte fixtures, failing samples, dylib manifests, contract annotations, logs)

## Reference UX: `cargo validity`
- `cargo validity inspect`
  - discover candidate validity surfaces, derives, reprs, known boundary types, and adapters
- `cargo validity check`
  - run declared vectors and emit `validity-check-report/v0`
- `cargo validity diff <A> <B>`
  - compare two packs or versions and explain drift
- `cargo validity doctor`
  - explain missing instrumentation, unsupported mixed-language vectors, or overclaims
- `cargo validity pack`
  - bundle a `validity-pack/v0`

`cargo validity` should begin as an orchestrator / validator / packer. It should avoid becoming a new verifier or a new sanitizer.

## Default policy
- **Surface-first, not checker-first.**
- **Invalid-value classes must be explicit.**
- **Type-level invariants and library invariants stay distinct.**
- **Mixed-language and separately compiled lanes are first-class.**
- **Unsupported and assumed-only are valid outcomes.**
- **Attachments may preserve engine-specific richness; fake flattening is not allowed.**

## What the kit should provide to others
- **Unsafe abstraction authors:** a way to publish invariants and evidence without forcing one verification stack.
- **Zero-copy / parsing libraries:** a shared vocabulary for all-bit-pattern, zero-valid, and checked-bit-pattern claims.
- **FFI / plugin teams:** a boundary artifact showing what foreign inputs must satisfy and where checks actually happen.
- **Safety evidence workflows:** a narrower, attachable validity/evidence family they can import instead of reconstructing from prose.
- **Future language/toolchain work:** a landing zone for contracts, unsafe fields, checked-load experiments, and sanitizers.

## Overlap boundaries
- **Not Sanitizer Battery Kit:** that kit runs and normalizes runtime checking engines broadly; this kit models the validity assumptions those engines are meant to test.
- **Not Safety Evidence Kit:** that kit aggregates assurance claims; this kit contributes one concrete validity/evidence family.
- **Not FFI Boundary Kit:** that kit owns explicit ABI/header/bindgen surfaces; this kit can attach to those surfaces when the problem is invalid values, layout assumptions, or ingress checks.
- **Not Pointer Surface Kit:** pointer ownership/aliasing semantics live there; only the validity-bearing representation assumptions live here.
- **Not Trait Surface Kit:** trait-family semantics live there; validity of concrete values and boundary forms lives here.
- **Not Formal Verification Kit:** proof backends stay there, though their artifacts may populate `validity-check-report/v0` attachments.

## Hard problems (explicitly scoped)
1. **Ambiguous boundary between type validity and library invariants**
   - v0 must keep them separate but linked.
2. **Tool heterogeneity**
   - contracts, Miri, sanitizers, and load-time checkers will never be identical.
3. **Cross-language realism**
   - mixed-language vectors are valuable precisely because pure-Rust tools cannot see everything.
4. **False confidence**
   - the kit must make “assumed only” or “unchecked in mixed-language paths” easy to say.
5. **Evolving language semantics**
   - the kit should not freeze today’s incomplete understanding into false permanence.

## Evaluation plan
Pilot on:
1. one `zerocopy`-style byte-backed type family,
2. one `bytemuck`-style checked-bit-pattern family,
3. one FFI boundary using generated headers or wrappers,
4. one dynamically loaded/plugin boundary using load-time layout checks,
5. one unsafe collection or container with explicit field invariants.

Success bar:
- projects can publish validity assumptions without inventing their own schema,
- reviewers can tell which invalid values are checked and where,
- mixed-language and load-time gaps become visible before production,
- and future contracts / unsafe-fields / checked-load work can land into a ready-made evidence surface.
