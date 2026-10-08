# Crate capability contract lanes — producer-side support profiles, decision packs, availability matrices, and slice-tool imports (2026-03-16)

The archive now has enough adjacent crate-ecosystem ideas that future passes could easily flatten them into one fake “crate metadata” bucket.
This note exists to keep the missing-crate story honest.

## Main distinction

The new **crate capability contract lane** is about a **producer-side, machine-readable support/interop contract** published by a crate author and checked against observed facts.
It is not the same lane as task-first crate choice, whole-project target support, per-item availability matrices, or security/trust scoring.

## Separate lanes to keep distinct

### 1. Crate capability contract lane (**P-0510**)

Question answered:
- “What does this crate claim to support and expose, what can tools observe directly, and where do those differ?”

Primary artifacts:
- `capability-contract`
- `observed-capabilities.receipt`
- `interop-exports.report`
- `profile-conformance.report`
- `capability-diff.report`

This lane should own:
- producer-side support profiles
- declared versus observed claim classes
- runtime-coupling posture
- `std` / `alloc` / `core` posture
- proc-macro / build-script / native-linkage exposure
- public interop export maps

This lane should **not** own:
- task-specific crate ranking
- whole-project toolchain policy
- item-by-item cfg availability matrices
- registry-wide trust scoring
- semver witness generation by itself

### 2. Crate ecosystem pathfinder / decision-pack lane (**P-0509**)

Question answered:
- “Given this task and these constraints, which crates are the best candidates and why?”

This lane may **import** producer-side capability contracts.
It should not become the place where a crate author publishes all of their own support claims.

### 3. Item-level availability lane (**P-0451**)

Question answered:
- “Which public items exist under which feature/target combinations?”

This lane should own:
- per-item feature/target matrices
- rustdoc-JSON-driven availability diffs
- conditional API drift

A capability contract may summarize `no_std` or docs posture at a coarse level.
It should not try to replace a true availability ledger.

### 4. Whole-project toolchain/target support lane (**P-0484**)

Question answered:
- “What toolchain, component, and target matrix does this repository/project support?”

This is broader than a single crate’s producer-side contract.
Do not collapse crate support claims into workspace- or repository-level bootstrap truth.

### 5. Health / trust lanes (**P-0011** and **P-0017**)

Question answered:
- “How maintained is this crate?”
- “How much trust/risk does adopting it add?”

These should inform or be imported by capability-aware tooling, but they are different facts from runtime coupling or `no_std` posture.
A risky crate can still publish an honest capability contract; a healthy crate can still publish a misleading one.

### 6. Public-API and semver slice tools

Question answered:
- “What public API exists?”
- “Did a release violate semver?”
- “What MSRV or dependency policy is in effect?”

Examples include `cargo-public-api`, `cargo-semver-checks`, `cargo-msrv`, and `cargo-deny`.
These are adjacent and valuable, but they remain **slice tools**.
The capability-contract lane is the joined producer-side artifact above them, not a replacement for them.

## Recommended fixture pressure

A serious capability-contract proposal should include at least four scenario types:

1. **Internal runtime use versus public runtime neutrality**
   - example: Tokio used internally while public API stays `futures-core`/`tower-service` oriented
2. **Coarse `no_std` claim with docs or target caveats**
   - example: `alloc` is real but docs.rs builds with a `std` feature overlay
3. **Hidden obligations**
   - example: proc macro, `build.rs`, or `links` imply downstream adoption cost that README prose underplays
4. **Support drift across releases**
   - example: a crate silently adds native linkage or tightens runtime coupling

## Recommended archive stance

When future passes propose crate-ecosystem metadata work, they must state explicitly whether the new artifact is primarily:

1. a **producer-side capability contract**,
2. a **task-first decision pack**,
3. an **item-level availability matrix**,
4. a **whole-project toolchain support contract**,
5. a **health/trust import**,
6. or a **public-API / semver / MSRV slice tool**.

Do not let the archive silently compress those into one fake “better metadata” story.
The sharp missing value is often the **coordination artifact between them**.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://doc.rust-lang.org/cargo/reference/manifest.html
- https://doc.rust-lang.org/cargo/reference/rust-version.html
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://rust-lang.github.io/rfcs/1824-crates.io-default-ranking.html
