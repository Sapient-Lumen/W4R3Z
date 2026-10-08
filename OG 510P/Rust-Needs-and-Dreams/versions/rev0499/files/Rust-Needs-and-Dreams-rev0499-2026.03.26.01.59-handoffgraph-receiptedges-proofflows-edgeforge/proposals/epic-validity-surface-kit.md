# Epic proposal: Validity Surface Kit

## Thesis
One of the strongest missing ecosystem contributions in Rust is a **portable contract for validity surfaces and boundary assumptions**.

Rust is now actively investing in contracts, unsafe fields, niche checks, sanitizer support, and safety-critical evidence. But the ecosystem still lacks a reviewable way to state what values are invalid, where checks occur, which assumptions are type-level versus library-level, how byte/FFI/load-time forms map into Rust values, and which tests actually exercised those claims.

In other words: Rust needs a boring, explicit `validity-pack/v0` more than it needs one more derive macro that says “safe bytes here”.

## Why now
The timing is unusually good:
- the `std` contracts goal explicitly treats contracts as code and wants runtime-check conversion plus tool-facing interfaces;
- the unsafe-fields goal exists because library safety invariants are currently too hard to denote and review;
- the niche-checks goal wants checked loads / function-entry checks exactly because invalid values still leak across unsafe and FFI boundaries;
- the sanitizer stabilization goal says mixed-language binaries still need better checking support;
- the 2026 flagships elevate safety-critical tooling, specifications, and evidence;
- ecosystem crates like `zerocopy`, `bytemuck`, `abi_stable`, and `safer_ffi` already show that teams need machine-readable validity vocabulary today, but each only covers one slice of the problem.

That means the next major validity seam is visible before it has converged.
This is exactly when a reviewable contract is most valuable.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
- https://rust-lang.github.io/rust-project-goals/2025h1/unsafe-fields.html
- https://rust-lang.github.io/rust-project-goals/2025h2/comprehensive-niche-checks.html
- https://rust-lang.github.io/rust-project-goals/2025h2/stabilization-of-sanitizer-support.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://docs.rs/zerocopy
- https://docs.rs/bytemuck
- https://docs.rs/abi_stable
- https://docs.rs/safer_ffi

## What should be built
A first credible version should ship:
1. `validity-surface/v0`, `niche-profile/v0`, `layout-validity-profile/v0`, `boundary-ingress-profile/v0`, `unsafe-invariant-profile/v0`, `validity-adapter-profile/v0`, `validity-vector-set/v0`, `validity-check-report/v0`, and `validity-pack/v0`
2. one byte-validity pilot comparing all-bit-pattern, zero-valid, and checked-bit-pattern lanes honestly
3. one FFI pilot showing exactly what foreign inputs must satisfy and where ingress checks run
4. one dylib/plugin pilot showing load-time layout or validity checks
5. one unsafe-container pilot making field invariants and runtime checks explicit
6. docs and CI that make invalid-value classes, ingress timing, and evidence posture visible

The winning version is small, semantic, and boundary-aware.
It should make validity assumptions legible together rather than canonizing one derive family or one checker.

## Initial pilots
- **Byte-view lane** — compare `zerocopy`-style and `bytemuck`-style validity vocabularies honestly
- **FFI lane** — show exactly how C/C++ values become checked or unchecked Rust values
- **Load-time lane** — record dynamic-library layout/load assumptions and checks
- **Unsafe-internal lane** — document library invariants that extend beyond type initialization

## Milestones
1. **v0 artifacts + vocabulary**
   - publish schemas and minimal examples
   - document type-validity vocabulary, boundary-ingress vocabulary, and evidence vocabulary
2. **v0.2 byte + FFI pilots**
   - ship at least one byte-validity pilot and one FFI pilot
   - show how checked and unchecked lanes differ in artifacts
3. **v0.3 load-time + unsafe-field depth**
   - add load-time validation and explicit unsafe-invariant attachments
   - capture migration notes as contracts/unsafe-fields become more available
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the artifact family without sharing one identical checking strategy

## Success metrics
- Library authors can review invalid-value assumptions without reconstructing them from derive docs and safety comments.
- Mixed-language and zero-copy boundaries publish what they assume versus what they validate.
- Future contracts, unsafe fields, and checked-load tooling land into an ecosystem that already records validity claims.
- Safety evidence workflows can import validity packs instead of manually scraping docs and CI logs.
- Rust avoids fragmenting validity work into many incompatible “bytes-safe / ffi-safe / load-safe” slogans that hide incompatible assumptions.

## Archive fit
This proposal fills a real gap in the archive:
- **Sanitizer Battery Kit** handles runtime engines,
- **Safety Evidence Kit** aggregates assurance signals,
- **FFI Boundary Kit** handles explicit ABI/header interfaces,
- **Pointer Surface Kit** handles pointer semantics,
- **Trait Surface Kit** handles trait-family semantics.

But none of those is the portable contract for **invalid values, layout assumptions, ingress checks, library invariants, and attachable validity evidence**.
Validity Surface Kit is the missing substrate for a part of Rust that the roadmap is explicitly making more important and more checkable.
