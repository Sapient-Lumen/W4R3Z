## 2026Q1 promotion note
This gap is now promoted into the active frontier through [`design/migration-truth-contract-2026Q1.md`](../design/migration-truth-contract-2026Q1.md).
Interpret the rest of this file as the motivating underlay for a first-class **change-program / upgrade-shaping** contract, not just as a complaint about edition ergonomics.

# Gap: upgrade choreography and reviewable migrations

## What is missing
Rust has many strong point tools for change, but it still lacks a **shared migration-program contract**.

Today there is no standard way to describe, exchange, and diff:
- what source state a crate or workspace is starting from,
- what destination state it intends to reach,
- which package / target / feature / profile slices were actually exercised,
- which edits were merely suggested, which were approved, and which were applied,
- which blockers or waivers remain,
- which final support, API, docs, or downstream claims are actually backed by evidence,
- and what later release/policy/support/assistant consumers may safely import without re-deriving the migration story.

That missing layer matters because Rust migrations are rarely one command.
They are change programs assembled from compiler fixes, manifest updates, lockfile movement, toolchain pin changes, API checks, MSRV checks, docs runs, downstream tests, and human judgment.

Sources:
- https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
- https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- https://doc.rust-lang.org/cargo/reference/rust-version.html
- https://rust-lang.github.io/rustup/overrides.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## The current seam is awkward
The ecosystem already has real migration building blocks:
- the Edition Guide gives an ordered edition-upgrade recipe,
- `cargo fix` applies compiler suggestions,
- `cargo update` and `cargo upgrade` move dependency state,
- `cargo msrv`-style tools probe or verify toolchain floors,
- public-API / semver tools inspect compatibility consequences,
- docs.rs rustdoc JSON and maintainer docs/support surfaces increasingly provide machine-usable downstream evidence,
- rustup and `rust-toolchain.toml` manage toolchain selection,
- and newer `cargo fix` work is explicitly trying to improve selectivity and interaction rather than pretending the current architecture is enough.

But every real migration still gets reconstructed from:
- issue comments,
- ad hoc shell scripts,
- CI YAML,
- scattered command transcripts,
- local branch discipline,
- and maintainer memory.

The result is not that Rust lacks migration tools.
The result is that there is no portable way to say:
- “this workspace is moving from support state A to support state B,”
- “these configuration slices were actually checked,”
- “these edits were conservative tool output and these were deliberate migration choices,”
- or “these final support/API/docs/downstream claims are what we now stand behind.”

Sources:
- https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
- https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- https://doc.rust-lang.org/cargo/reference/rust-version.html

## Why this matters
This gap is larger than edition polish.
It affects:
1. **edition upgrades** — the official path is multi-step, config-sensitive, and partly manual in edge cases;
2. **dependency upgrades** — lockfile movement, manifest requirement changes, and API consequences are still fragmented across different tools;
3. **toolchain/MSRV policy** — Cargo explicitly documents that workspace verification can get complicated when multiple Rust-version policies coexist;
4. **API and package-boundary review** — public/private dependency work, rustdoc JSON, and semver-checking work mean migrations now have real publish-path consumers instead of only local compile success;
5. **support claims** — toolchain pins, docs coverage, downstream compatibility, and platform support can all shift during one migration;
6. **team coordination** — the current `cargo fix` architecture itself is under active redesign, which means the right long-term contribution is not “one winning fixer,” but a shared evidence boundary above whichever edit engine wins.

Sources:
- https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- https://doc.rust-lang.org/cargo/reference/rust-version.html
- https://rust-lang.github.io/rustup/overrides.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/

## What “good” looks like
A worthy contribution here is **not** “one magic upgrader”.
It is a shared migration boundary:
- one `migration-subject/v0` describing the starting state and scope,
- one `migration-intent/v0` describing the desired destination and compatibility posture,
- one `migration-analysis-report/v0` summarizing what existing tools found,
- one `migration-plan/v0` declaring ordered steps, approvals, and selected configurations,
- one `migration-run-report/v0` recording what actually happened,
- one `migration-outcome-report/v0` stating the final supported claim,
- optional `migration-waiver/v0` for accepted incompleteness,
- and one `migration-pack/v0` bundle for CI, review, release prep, and later archaeology.

That would let edition upgrades, dependency changes, API checks, MSRV verification, docs validation, downstream testing, support-envelope changes, and release review speak about the same migration program instead of scattering the truth across logs and lore.
