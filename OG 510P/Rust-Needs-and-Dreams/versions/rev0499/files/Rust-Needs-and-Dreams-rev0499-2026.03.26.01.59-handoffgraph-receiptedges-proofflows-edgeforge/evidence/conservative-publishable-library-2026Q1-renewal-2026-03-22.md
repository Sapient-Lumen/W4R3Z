# Renewal receipt: conservative publishable library (2026-03-22)

## Subject
- default card: `defaults/conservative-publishable-library-2026Q1.md`
- review date: 2026-03-22
- archive revision: rev0381
- scope: stable-Rust reusable libraries intended for publication or durable reuse outside one local app
- non-goal: blessing this as the default for proc-macros, `-sys` crates, or internal-only helper crates

## Renewal verdict
**add as new card**

The defaults corpus needed a library-centered card because it had become application-heavy.
The correct lane-level public answer for this scope is now:

- explicit `Cargo.toml` contract (`rust-version` plus normal package metadata),
- docs.rs-aware documentation and CI checks,
- semver review before publish,
- deliberate public error and dependency exposure,
- and exact package-identity hygiene.

## Canon import checked this round
Primary official surfaces re-read:
- Cargo `rust-version`:
  https://doc.rust-lang.org/cargo/reference/rust-version.html
- Cargo semver compatibility:
  https://doc.rust-lang.org/cargo/reference/semver.html
- Cargo publishing:
  https://doc.rust-lang.org/cargo/reference/publishing.html
- docs.rs metadata:
  https://docs.rs/about/metadata
- docs.rs builds:
  https://docs.rs/about/builds
- `cargo docs-rs`:
  https://docs.rs/crate/cargo-docs-rs/latest

Canon judgment:
- Cargo and docs.rs now expose enough explicit publish/docs contract surface to justify a maintained public library card;
- docs.rs should be treated as part of the contract for publishable crates, not only as a hosting side effect;
- the lane can stay conservative without turning into one universal release workflow.

## Registry / supply-chain import
Public review surfaces checked:
- crates.io development update:
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- RustSec advisories:
  https://rustsec.org/advisories/

Imported judgments:
- crates.io now provides Security-tab advisory surfacing, Trusted Publishing only mode, SLOC, `pubtime`, and Browse source links, so the public review surface around published crates is materially better than it was;
- exact package identity is now part of conservative release hygiene, not just style, because current RustSec advisories include multiple malicious lookalike names such as `envlogger`, `oncecell`, and `serd`;
- this receipt is still a **lane judgment**, not a package-admission verdict for any one dependency graph.

## API / compatibility import
Relevant surfaces checked:
- Rust 2026 goals / flagships:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo unstable docs (`public-dependency`):
  https://doc.rust-lang.org/cargo/reference/unstable.html
- `cargo-semver-checks` project goal:
  https://rust-lang.github.io/rust-project-goals/2024h2/cargo-semver-checks.html
- `cargo-semver-checks` crate page:
  https://crates.io/crates/cargo-semver-checks

Imported judgments:
- the public/private dependency seam is now official enough that publishable-library guidance should name it, even though the feature is still unstable;
- semver checking belongs in the lane because Cargo’s visible direction is toward stronger compatibility checks in publish workflows;
- a conservative library lane should therefore push authors toward deliberate public dependency exposure rather than accidental exposure.

## Maintenance / support-envelope import
Support-envelope signals checked:
- Rust challenges post:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust Foundation 2026-2028 strategy:
  https://rustfoundation.org/strategic-plan/

Maintenance judgment:
- the lane is justified because current official Rust signals still say navigation depends too much on tacit knowledge while docs remain canonical;
- Foundation strategy keeps stable infrastructure, sustainable maintenance, and adoption growth coupled, which supports a boring-default card that improves maintainability rather than only novelty;
- the card should stay narrow and should not collapse package-admission, docs, semver, and release automation into one false “quality” score.

## Freshness / replay notes
Fresh inputs checked on 2026-03-22:
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2024h2/cargo-semver-checks.html
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/crate/cargo-docs-rs/latest
- https://rustsec.org/advisories/

Replay notes:
- renew this receipt when public/private dependencies materially stabilize or change shape;
- renew when Cargo’s relationship to `cargo-semver-checks` changes materially;
- renew when docs.rs build/config behavior changes enough to alter CI guidance;
- renew sooner if the advisory stream or crates.io review surface changes enough to sharpen package-identity or admission guidance.

## Lane judgment
Add the card as a maintained public default.

Why:
- it fills the biggest missing center of the current defaults corpus;
- it maps directly onto current Cargo/crates.io/docs.rs motion;
- and it improves publication discipline without forcing a heavy framework story.

## Open watch items
- whether future stabilization of public/private dependencies should make “minimize accidental public deps” stronger and more machine-checkable;
- whether `cargo-semver-checks` moves close enough to Cargo integration to promote it from “strong default gate” to “expected publish path”;
- whether the corpus should later split this card into **internal durable library** versus **public crates.io library**.
