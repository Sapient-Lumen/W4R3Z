# Crate decision lanes — discovery, health, trust, façade crates, and starter-set policy (2026-03-16)

The archive now has enough adjacent ecosystem-selection ideas that future passes could easily blur them together.
This note exists to keep the missing-crate story honest.

## Main distinction

The new **crate decision/pathfinder lane** is about producing a **task-oriented decision artifact**.
It is not the same lane as per-crate metadata, security scoring, or façade-crate curation.

## Separate lanes to keep distinct

### 1. Crate ecosystem pathfinder / decision-pack lane

Question answered:
- “Given this task and these constraints, what are the most plausible crate choices, why, and where is the uncertainty?”

Primary artifacts:
- `task-profile`
- `candidate-import.report`
- `interop-surface.report`
- `decision-pack.report`
- `starter-set.lock`

This lane should own:
- task-first comparisons
- explicit eliminations and trade-offs
- interop/runtime/target lock-in analysis
- reviewable starter-set selection for a specific team or task

This lane should **not** own:
- registry-wide trust scoring
- general sustainability metadata
- façade reexports
- Rust-project-level blessing politics

### 2. Crate health lane (**P-0011**)

Question answered:
- “How maintained, governed, and MSRV-explicit is this crate?”

This lane should own:
- maintenance state
- succession/governance posture
- MSRV and support policy
- security/fuzzing posture metadata

It may be imported by the pathfinder lane, but it should not be collapsed into “which crate should I choose?”
A well-maintained crate can still be the wrong fit for a task.

### 3. Trust/risk lane (**P-0017**)

Question answered:
- “How much supply-chain or naming risk does this dependency choice add?”

This lane should own:
- confusable detection
- trust-cost scoring
- policy gates
- security-oriented explanations

It should inform pathfinder outputs, but it is not the whole decision story.
The safest-looking crate may still have the wrong interop surface, runtime coupling, or migration cost.

### 4. Dependency-minimal façade lane (**P-0006**)

Question answered:
- “Can we publish one small, curated battery pack or façade crate for common tasks?”

This lane should own:
- reexports / wrapper APIs
- dependency budgets
- profile features like `::cli` or `::net`
- curation policy for a single published façade

This is downstream of a pathfinder-style decision, not a substitute for it.
A façade crate is one possible output of ecosystem curation, not the full comparison artifact.

### 5. Generic discovery substrate lane (crates.io / Cargo / docs.rs)

Question answered:
- “How do users search, browse, and fetch package metadata in the general ecosystem?”

This lane should own:
- registry search behavior
- categories/keywords metadata
- docs browsing
- package add/fetch ergonomics

A pathfinder crate may import or sit above this lane, but should not pretend it is replacing crates.io itself.

### 6. Official blessing / stdlib expansion / interop-trait lane

Question answered:
- “Should Rust officially bless more building blocks, expand the standard library, or standardize more interop traits?”

This is primarily an RFC/project-governance lane, not an archive crate-design lane.
A pathfinder crate can reduce the pain in the meantime without claiming to settle the political question.

## Recommended fixture pressure

A serious crate-decision/pathfinder proposal should include at least three kinds of scenarios:

1. **Two plausible winners with different lock-in costs**
   - example: async service stack where runtime coupling is a first-order decision
2. **A newcomer-friendly default versus expert-optimized stack**
   - example: CLI baseline where teaching ergonomics and long-term extensibility differ
3. **Task split across incompatible support surfaces**
   - example: `no_std` embedded lane where `alloc` / proc-macro / host-tool assumptions sharply divide candidates

## Recommended archive stance

When future passes propose crate-discovery work, they must say explicitly whether the new artifact is primarily:

1. a **task-first decision pack**,
2. a **per-crate health import**,
3. a **trust/risk import**,
4. a **façade crate / battery pack**,
5. or a **governance-level blessing / standards** argument.

Do not let the archive silently compress those into one fake “crate curation” bucket.
The sharp missing value is often the **coordination artifact between them**.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/cargo/reference/manifest.html
- https://doc.rust-lang.org/cargo/commands/cargo-search.html
- https://doc.rust-lang.org/cargo/commands/cargo-add.html
- https://github.com/rust-lang/crates.io/discussions/9325
