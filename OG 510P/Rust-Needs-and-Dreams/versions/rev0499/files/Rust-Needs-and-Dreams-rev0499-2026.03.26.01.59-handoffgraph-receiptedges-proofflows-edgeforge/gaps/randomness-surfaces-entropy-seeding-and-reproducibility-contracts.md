# Gap: randomness surfaces, entropy sources, seeding, and reproducibility contracts

## What is missing
Rust has **real randomness diversity**, but the ecosystem still lacks a **portable way to describe what a randomness surface actually promises**.

Today there is no standard way to say:
- whether a crate draws entropy directly from the operating system, wraps a periodically reseeded thread-local generator, or is purely deterministic once seeded,
- whether the generator is infallible, fallible, or only conditionally available on some targets,
- whether the implementation claims cryptographic unpredictability, is only statistically decent, or is explicitly fast-and-insecure,
- whether outputs are portable and reproducible across platforms and releases, or deliberately non-portable so algorithms may change,
- how seeding works: direct OS entropy, parent-generator seeding, explicit seed bytes, hashable/user-facing seeds, state serialization, or fork-style child-generator derivation,
- what happens across `fork`, threads, WASM, `no_std`, unsupported targets, or custom entropy backends,
- whether distributions, sampling helpers, and sequence algorithms preserve reproducibility or are allowed to change for performance,
- and what evidence checked the claims: reproducibility vectors, target-backend vectors, fork/reseed vectors, crypto-consumer integration vectors, or fallible-entropy vectors.

That gap matters because Rust already has meaningful point solutions:
- `getrandom` provides low-level system entropy with target-specific and opt-in/custom backends,
- `rand` now clearly distinguishes `SysRng`, `ThreadRng`, `StdRng`, `SmallRng`, and portable named generators,
- `rand_core` 0.10 recently made substantial trait/API changes around `Rng` / `TryRng` and `SeedableRng::{fork, try_fork}`,
- `rand_chacha` publishes portable deterministic ChaCha generators and secure-usage guidance,
- lightweight alternatives like `fastrand` and `oorandom` deliberately optimize for simplicity, speed, or compile-time footprint instead of one grand unified story,
- and crypto-facing crates already consume `CryptoRngCore`-style contracts directly.

So the missing contribution is not one magical RNG crate.
It is a **reviewable randomness-surface layer** for publishing entropy source, seeding, reproducibility, crypto-strength posture, target/backend truth, and evidence honestly.

Sources:
- https://docs.rs/getrandom
- https://docs.rs/rand/latest/rand/rngs/
- https://docs.rs/rand/latest/rand/
- https://docs.rs/rand_core/latest/rand_core/
- https://docs.rs/crate/rand_core/latest/source/CHANGELOG.md
- https://docs.rs/rand_chacha
- https://docs.rs/fastrand
- https://docs.rs/crate/oorandom/latest
- https://docs.rs/rand_seeder/latest/rand_seeder/struct.Seeder.html
- https://docs.rs/signature/latest/signature/trait.RandomizedSigner.html
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## The current seam is awkward
Rust already spans several materially different randomness lanes, but today most of that truth is split across crate docs, migration notes, and folklore:
- `getrandom` roughly tracks the Rust standard library’s target support, but also exposes opt-in backends, custom/unsupported backends, and WebAssembly caveats that can materially change behavior,
- `rand` now explicitly publishes separate lanes for `SysRng`, `ThreadRng`, `StdRng`, `SmallRng`, and portable named generators, which is evidence that “the RNG story” has already fractured into several honest sub-stories,
- `ThreadRng` documents fork-related reseeding requirements and explicitly declines to promise stronger in-memory state protections,
- `StdRng` and `SmallRng` both document non-portability, while portable generators are pushed into named lanes like ChaCha or Xoshiro,
- `rand_core` 0.10 changed core trait names and separated more of the implementation surface from higher-level convenience layers,
- `rand_chacha` publishes deterministic generators with testing against reference vectors, but also emphasizes that secure use depends on correct seeding and comes without an audit guarantee,
- `fastrand` and `oorandom` exist precisely because many users want faster, simpler, or smaller RNG choices even when those choices are insecure or intentionally narrow,
- and crypto consumers like `signature` depend on `CryptoRngCore`-style traits directly, which means entropy/RNG choices leak into higher-level APIs.

These are not minor implementation details.
They determine security posture, reproducibility, platform support, compile-time cost, fork safety, API compatibility, and whether downstream users can reason about randomness honestly.

Sources:
- https://docs.rs/getrandom
- https://docs.rs/rand/latest/rand/rngs/
- https://docs.rs/rand/latest/rand/rngs/struct.ThreadRng.html
- https://docs.rs/rand/latest/rand/rngs/struct.StdRng.html
- https://docs.rs/rand/latest/rand/rngs/struct.SmallRng.html
- https://docs.rs/crate/rand_core/latest/source/CHANGELOG.md
- https://docs.rs/rand_chacha
- https://docs.rs/fastrand
- https://docs.rs/crate/oorandom/latest
- https://docs.rs/signature/latest/signature/trait.RandomizedSigner.html

## Why this matters
This gap matters because randomness choices cut across several important Rust futures at once:
1. **security and cryptography** — cryptographic consumers need auditable entropy and `CryptoRng`-style posture rather than vague “secure enough” prose.
2. **simulation, testing, and reproducibility** — deterministic replay depends on portable generators, explicit seed derivation, and stability claims.
3. **portability and restricted environments** — WASM, `no_std`, embedded, custom-target, and unsupported-target lanes need explicit backend truth.
4. **performance and build ergonomics** — some users need the broader `rand` ecosystem while others deliberately choose simpler crates for compile-time or dependency reasons.
5. **library composability** — generator traits, crypto-consumer traits, seed derivation helpers, and entropy backends are all real but poorly compared.

A worthy contribution here is therefore not another “best RNG” argument.
It is a way to treat randomness surfaces as **reviewable ecosystem infrastructure**.

Sources:
- https://docs.rs/rand/latest/rand/rngs/
- https://docs.rs/getrandom
- https://docs.rs/rand_chacha
- https://docs.rs/rand_seeder/latest/rand_seeder/struct.Seeder.html
- https://docs.rs/fastrand
- https://docs.rs/crate/oorandom/latest
- https://docs.rs/signature/latest/signature/trait.RandomizedSigner.html
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## What “good” looks like
A worthy contribution here is **not** one universal RNG abstraction that erases meaningful differences.

It is a shared randomness-surface boundary:
- one `randomness-surface/v0` describing the top-level surface identity, intended use, and whether the package is entropy-source-first, general-purpose RNG-first, reproducibility-first, crypto-first, lightweight/simple, or mixed,
- one `entropy-source-profile/v0` for OS/hardware/custom entropy source, blocking/failure posture, and target availability,
- one `rng-semantics-profile/v0` for algorithm family, state size, portability, thread/fork behavior, and reseeding strategy,
- one `seed-repro-profile/v0` for seed type, derivation, serialization/import/export, stable output guarantees, and release-to-release change posture,
- one `crypto-strength-profile/v0` for `CryptoRng` / `TryCryptoRng` claims, side-channel caveats, audit posture, and backtracking-resistance notes,
- one `target-backend-profile/v0` for `std` / `no_std` / WASM support, `getrandom` backend choice, custom backend hooks, and unsupported-target behavior,
- one `randomness-adapter-profile/v0` for bridges between `getrandom`, `rand`, `rand_core`, portable PRNG crates, lightweight alternatives, and crypto-facing consumers,
- one `randomness-vector-set/v0` for reproducibility, fork/reseed, target-backend, fallible-entropy, and consumer-integration vectors,
- one `randomness-check-report/v0` recording which vectors actually ran on which targets/channels,
- and one `randomness-pack/v0` bundle for docs, CI, migration notes, and archaeology.

That would let Rust teams review “secure RNG”, “portable seed”, or “WASM-supported randomness” claims using explicit artifacts instead of guessing from README prose, blog posts, or implementation folklore.

## Non-goals
This gap should not be used to:
- define all randomness or cryptography in Rust,
- replace `getrandom`, `rand`, `rand_core`, `rand_chacha`, `fastrand`, `oorandom`, or crypto-consumer traits,
- flatten system entropy, periodically reseeded thread-local RNGs, deterministic portable generators, and lightweight insecure PRNGs into one fake universal model,
- or turn RNG choice into a shallow benchmark or “security badge” leaderboard.

The job is smaller and sharper:
**make randomness surfaces legible, honest, and checkable across entropy sources, PRNG families, portability lanes, crypto claims, and evidence.**
