# Design: Randomness Surface Kit (`cargo rngsurf`, `randomness-pack/v0`)

## Goal
Define a portable contract for specifying, validating, diffing, and reviewing **randomness surfaces** in Rust: system entropy, thread-local reseeded generators, deterministic PRNGs, portable reproducible generators, lightweight/simple alternatives, custom target backends, and crypto-facing RNG consumers.

This should help answer questions like:
- where randomness actually comes from,
- whether the API is infallible or can fail,
- whether a generator is portable and reproducible,
- how seeding and forking are expected to work,
- whether cryptographic unpredictability is claimed and under what caveats,
- which targets/backends are genuinely supported,
- and what evidence shows the claimed semantics are real.

It should **not** replace RNG crates, bless one algorithm, or force secure, portable, lightweight, and target-specific lanes into one common denominator.

## Why now
This seam has become strategically relevant because Rust now spans several real but poorly aligned randomness shapes at once:
- `getrandom` is a clearly separate low-level entropy layer with opt-in/custom backends and target caveats,
- `rand` explicitly distinguishes system entropy, thread-local generators, non-portable “standard” generators, and portable named generators,
- `rand_core` 0.10 just made large trait/API changes before 1.0 and added first-class `fork`/`try_fork` support on `SeedableRng`,
- crypto-facing crates consume `CryptoRngCore`-style traits directly,
- lightweight alternatives keep attracting users because general-purpose randomness is not a one-size-fits-all problem,
- and WASM / `no_std` / unsupported-target / custom-backend behavior is now explicit enough to deserve first-class artifacts.

That is exactly the moment when a **randomness-surface contract** becomes more valuable than one more RNG implementation or one more migration guide.

## Design principles
1. **Do not lie about entropy.** System entropy, custom backends, and deterministic seeds are not the same story.
2. **Do not lie about portability.** Portable named generators and non-portable “best current default” generators must remain visibly different.
3. **Keep failure posture first-class.** Fallible entropy acquisition and infallible PRNG use are separate truths.
4. **Keep crypto posture first-class.** `CryptoRng` markers, audit posture, and caveats should not blur into “secure-ish”.
5. **Keep seed and fork truth first-class.** Explicit seeding, seed derivation, serialization, child-fork behavior, and reseeding strategy are public semantics.
6. **Prefer attachable evidence over folklore.** Reproducibility vectors, target/backend vectors, and consumer-integration vectors matter more than README claims.
7. **Do not flatten the ecosystem.** `getrandom`, `rand`, named portable generators, lightweight alternatives, and crypto consumers should remain visibly different.

## Artifact family
The kit should revolve around a small family of portable artifacts.

### 1) `randomness-surface/v0`
Top-level description of the randomness surface:
- package/crate identity,
- intended use cases (general-purpose, simulation, crypto-adjacent, lightweight/simple, embedded, WASM, etc.),
- major lanes exposed,
- whether the surface is entropy-first, PRNG-first, or mixed,
- artifact versioning and links to checks.

### 2) `entropy-source-profile/v0`
Describes where non-deterministic bits come from:
- OS/hardware/custom source,
- blocking/non-blocking/failure posture,
- stateless vs stateful source,
- whether the source is first-party, opt-in backend, or externally implemented,
- target restrictions and minimum platform assumptions.

### 3) `rng-semantics-profile/v0`
Describes a generator lane:
- algorithm family,
- state size / buffered-versus-unbuffered behavior,
- portability guarantee,
- expected security class,
- thread-local / shareable / cloneable posture,
- reseeding strategy,
- fork behavior and any required user action,
- whether outputs are intentionally allowed to change between releases.

### 4) `seed-repro-profile/v0`
Describes how deterministic use works:
- seed type and width,
- accepted seed sources,
- derivation APIs and parent-generator support,
- state import/export or serde posture,
- reproducibility guarantee across platforms and releases,
- migration policy when algorithms or helper methods change,
- compatibility with “user-facing seed strings” or hashable seeders.

### 5) `crypto-strength-profile/v0`
Describes crypto-facing claims:
- whether `CryptoRng` / `TryCryptoRng` is implemented,
- unpredictability claim scope,
- side-channel or state-protection caveats,
- audit/review posture,
- backtracking-resistance claims or explicit non-claims,
- suitability notes for cryptographic consumers.

### 6) `target-backend-profile/v0`
Describes target support:
- `std` / `alloc` / `no_std` posture,
- WASI / Emscripten / `wasm32-unknown-unknown` handling,
- `getrandom` backend choice and opt-in flags,
- unsupported-target behavior,
- custom-backend extension points,
- nightly-only or feature-gated target behavior.

### 7) `randomness-adapter-profile/v0`
Describes interop:
- bridges between `getrandom`, `rand`, `rand_core`, portable PRNG crates, and lightweight alternatives,
- trait-version compatibility,
- crypto-consumer integration,
- seed conversion and derivation adapters,
- migration shims.

### 8) `randomness-vector-set/v0`
Executable checks covering claims such as:
- reproducibility across targets/toolchains,
- fork/reseed behavior,
- failure behavior when entropy is unavailable,
- WASM/custom-backend integration,
- seed/state import/export roundtrips,
- crypto-consumer compatibility,
- release-to-release semantic diffs.

### 9) `randomness-check-report/v0`
Machine-readable results of running vectors:
- what ran,
- on which targets,
- with which backends/features,
- pass/fail/skip reasons,
- hashes or attachments for reproducibility evidence.

### 10) `randomness-pack/v0`
Bundle containing the surface description, profiles, vectors, reports, migration notes, and human-readable summaries.

## Tooling shape
A `cargo rngsurf` command should be able to:
- scaffold the artifact family,
- inspect a workspace for likely randomness lanes,
- detect direct `getrandom`, `rand`, `rand_core`, or lightweight-RNG usage,
- record target/backend and feature-gating posture,
- run bounded reproducibility/fork/backend/consumer vectors,
- diff support claims between releases,
- and export one portable `randomness-pack/v0`.

## Why this is better than today
Today, downstream users infer randomness behavior from vague phrases like “uses secure randomness”, “portable RNG”, “seedable”, “fast RNG”, or “supports WASM”.
Those phrases hide the most important questions:
- does this use OS entropy or a deterministic generator,
- what happens on unsupported targets,
- whether output is stable across releases,
- whether child processes must reseed,
- what “secure” actually claims,
- and which checks were ever run.

Randomness Surface Kit makes those questions first-class without forcing the ecosystem to converge on one RNG implementation.

## Boundaries with nearby kits
- **Not Validity Surface Kit:** validity owns invalid values and byte/layout assumptions; this kit owns entropy and RNG semantics.
- **Not Time Surface Kit:** time owns clocks, zones, calendars, and deterministic-time posture; this kit owns randomness/reproducibility posture.
- **Not FuzzPack / Replay / DST:** those kits may consume seeds and randomization, but this kit owns the upstream RNG/entropy contract itself.
- **Not Runtime Capability Kit:** that kit owns whether host entropy access is allowed; this kit owns what happens once a randomness lane is chosen.
- **Not Encoding Surface Kit:** encoding may serialize RNG state or seeds, but this kit owns seeding/reproducibility semantics.
- **Not Crypto libraries themselves:** this kit records RNG suitability and evidence; it does not define signatures, KDFs, ciphers, or protocol soundness.

## Non-goals
- No attempt to define one universal RNG trait beyond what the ecosystem already exposes.
- No attempt to replace `getrandom`, `rand`, `rand_core`, `rand_chacha`, `fastrand`, `oorandom`, or crypto-consumer traits.
- No attempt to reduce randomness choice to benchmark charts or one security badge.
- No attempt to hide meaningful differences in entropy source, portability, or failure semantics.

## MVP shape
The first practical MVP should target five lanes:
1. system entropy via `getrandom`,
2. `rand` general-purpose RNGs (`SysRng`, `ThreadRng`, `StdRng`, `SmallRng`),
3. portable deterministic generators via `rand_chacha` or named portable families,
4. one lightweight/simple alternative (`fastrand` or `oorandom`),
5. one crypto-facing consumer using `CryptoRngCore`.

That MVP would already be enough to prove whether one reviewable artifact family can sit above today’s fragmented Rust randomness ecosystem without flattening it.
