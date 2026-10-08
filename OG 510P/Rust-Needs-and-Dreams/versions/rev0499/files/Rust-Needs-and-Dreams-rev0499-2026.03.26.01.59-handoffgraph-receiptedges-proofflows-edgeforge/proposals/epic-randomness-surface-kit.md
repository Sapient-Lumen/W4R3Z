# Epic proposal: Randomness Surface Kit

## Thesis
One of the more worthy Rust ecosystem contributions now would be a **portable review layer for randomness surfaces**.

Not another RNG implementation.
Not another migration blog post.
Not another vague “secure randomness” badge.

The missing layer is a way to publish, diff, and verify:
- where randomness actually comes from,
- whether a generator is deterministic, portable, and reproducible,
- what seeding and fork behavior are promised,
- whether cryptographic unpredictability is claimed and with what caveats,
- which targets and backends genuinely work,
- and what evidence shows those claims are real.

That contribution would be unusually leveraged because it can serve simulations, games, fuzzers, benchmarking tools, crypto-adjacent code, embedded targets, WASM applications, and general application code at once.

## Why this could be epic
Rust now has unusually broad randomness diversity, but not yet a shared review layer:
- `getrandom` is a cross-platform entropy substrate with explicit supported-target tables, WebAssembly caveats, and custom/unsupported backends,
- `rand` now publishes a clearly stratified family of RNG lanes instead of pretending one generator solves every need,
- `rand_core` 0.10 made major pre-1.0 API changes, including renamed core traits and new fork-oriented helpers,
- portable deterministic generators and non-portable “best current” generators already coexist,
- lightweight/simple alternatives continue to exist because dependency budget and compile-time cost matter,
- and crypto consumers already talk in `CryptoRngCore` terms.

That is exactly the moment when a **surface contract** becomes more valuable than one more crate choice guide.

Sources:
- https://docs.rs/getrandom
- https://docs.rs/rand/latest/rand/rngs/
- https://docs.rs/crate/rand_core/latest/source/CHANGELOG.md
- https://docs.rs/rand_chacha
- https://docs.rs/fastrand
- https://docs.rs/crate/oorandom/latest
- https://docs.rs/signature/latest/signature/trait.RandomizedSigner.html

## What the contribution should look like in practice
The contribution should probably be a **tool + schema family + reference adapters + example packs**.

### 1) Tooling
A `cargo rngsurf` command that can:
- scaffold the artifact family,
- inspect a workspace for likely randomness lanes,
- run bounded reproducibility/fork/backend/consumer vectors,
- diff support claims over time,
- and export one portable `randomness-pack/v0`.

### 2) Schemas
At minimum:
- `randomness-surface/v0`
- `entropy-source-profile/v0`
- `rng-semantics-profile/v0`
- `seed-repro-profile/v0`
- `crypto-strength-profile/v0`
- `target-backend-profile/v0`
- `randomness-adapter-profile/v0`
- `randomness-vector-set/v0`
- `randomness-check-report/v0`
- `randomness-pack/v0`

### 3) Reference adapters
The project becomes much more real if it ships reference adapters for:
- `getrandom` system entropy and custom-backend lanes,
- `rand` system/thread-local/default/small generators,
- one portable deterministic lane (`rand_chacha` or named Xoshiro/PCG family),
- one lightweight/simple lane such as `fastrand` or `oorandom`,
- one crypto-facing consumer trait family.

### 4) Example packs
Ship real examples that deliberately differ in shape:
- a secure entropy-first service crate,
- a simulation/game crate with reproducible seed handling,
- a WASM or custom-target example with backend-specific caveats,
- a lightweight CLI or benchmarking crate choosing a smaller RNG surface,
- a crypto-adjacent consumer requiring `CryptoRngCore`.

Those examples should prove the surface layer can represent disagreement honestly instead of smoothing it away.

## Design principles
1. **Do not lie about entropy source.** System entropy, custom backends, and deterministic seeds are different stories.
2. **Do not lie about reproducibility.** Portable output and “algorithm may change next release” should remain visibly different.
3. **Do not lie about crypto posture.** Secure markers and caveats must remain explicit.
4. **Keep fork and reseed truth first-class.** Child-process behavior matters in real systems.
5. **Keep target/backend truth first-class.** WASM, unsupported targets, and custom entropy hooks are not edge trivia.
6. **Prefer attachable evidence over folklore.** Reproducibility vectors, backend vectors, and consumer integration matter more than slogans.
7. **Do not flatten the ecosystem.** `getrandom`, `rand`, portable named generators, and lightweight alternatives should remain visibly different.

## Why existing projects are not enough
The point projects are real, but they leave a coordination gap:
- `getrandom` solves entropy acquisition, not release/report semantics,
- `rand` solves high-level generation and sampling, not support-diff artifacts,
- `rand_core` defines traits, not public evidence bundles,
- `rand_chacha` and other portable generators solve implementation lanes, not ecosystem comparison,
- lightweight crates solve narrower needs, not shared vocabulary,
- and crypto consumers can demand RNG traits without publishing target/reseed/backtracking caveats in one portable form.

The ecosystem therefore still lacks a common answer to “what exactly does this crate promise about randomness, portability, and security, and how do we know?”

## Likely first users
- simulation and game crates needing stable seed stories,
- benchmarking and statistical tooling with reproducibility requirements,
- WASM and embedded applications with target/backend caveats,
- service crates with forking or subprocess behavior,
- crypto-adjacent code that wants auditable RNG requirements,
- library teams wanting to document why they use `rand`, a named portable generator, or a lightweight alternative.

## Risks
- **Too much detail:** randomness is easy to overspecify.
  - Response: focus on public support truth, not theoretical purity.
- **Too much churn:** RNG crates and traits are still evolving.
  - Response: keep the contract lane-aware and migration-friendly.
- **Security theater:** people may try to reduce it to one badge.
  - Response: make caveats, audit posture, and non-claims first-class.
- **Benchmark theater:** people may try to turn it into a speed leaderboard.
  - Response: bias toward semantic vectors and optional raw evidence.

## Phased plan
### Phase 1: representation
- finalize schemas,
- implement scaffold/inspect/export,
- ship adapters for `getrandom`, `rand`, one portable named generator family, one lightweight/simple crate, and one crypto consumer.

### Phase 2: checking
- add reproducibility/fork/backend/consumer vectors,
- emit `randomness-check-report/v0`,
- add diff support for semantic regressions.

### Phase 3: ecosystem composition
- integrate with FuzzPack, Replay, DST, Runtime Capability Kit, Encoding Surface Kit, and crypto-adjacent workflows,
- let downstream crates attach `randomness-pack/v0` in release and CI flows,
- add archaeology/migration support for generator or backend changes.

## Interaction with the rest of this archive
This proposal should stay distinct from:
- **Runtime Capability Kit** — that kit owns permission to access host entropy sources; this kit owns randomness semantics after access is chosen.
- **FuzzPack / Replay / DST** — those kits consume seeds or randomization; this kit owns the upstream entropy/RNG truth.
- **Time Surface Kit** — time owns clocks and deterministic time; this kit owns deterministic randomness and entropy.
- **Encoding Surface Kit** — encoding may serialize seeds or state; this kit owns seed/reproducibility semantics.
- **Crypto or protocol kits** — those own higher-level security/protocol semantics; this kit owns RNG suitability and evidence.

## Bottom line
A genuinely worthy Rust contribution here would be:

> **Randomness Surface Kit** — one reviewable boundary for entropy-source posture, PRNG semantics, seeding and reproducibility, crypto-strength claims, target/backend truth, and evidence across `getrandom`, `rand`, `rand_core`, portable named generators, lightweight alternatives, and crypto-facing consumers.

That would be “epic” not because it replaces today’s projects, but because it could make the whole Rust randomness story far easier to publish, compare, verify, and build on.
