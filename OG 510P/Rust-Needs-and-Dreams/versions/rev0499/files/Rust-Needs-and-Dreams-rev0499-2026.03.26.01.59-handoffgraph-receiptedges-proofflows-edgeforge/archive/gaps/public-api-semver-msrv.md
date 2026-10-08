# Gap: Public API stability + SemVer + MSRV (release-boundary evidence)

Rust now has strong momentum around **public/private dependencies**, **breaking-change detection**, and **SBOM support**, but the workflow is still fragmented at the exact point where library authors need a trustworthy **release admission boundary**.

Today, teams can combine point tools to answer parts of the question:
- what is my public API?
- what changed between releases?
- is this semver-correct?
- what is my supported MSRV in practice?
- which dependencies are actually part of my public surface?

What is still missing is a **single, reviewable, portable contract** for library evolution that is strong enough to feed CI, `cargo publish`, downstream packagers, and policy tooling.

## Why this matters now
- Rust’s 2026 flagship supply-chain work explicitly centers **public/private dependencies** and **SBOM support** as part of “Secure your supply chain.”
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The public/private-dependency goal says the feature should help users catch when they unexpectedly expose implementation details and help tooling identify what constitutes an API.
  - https://rust-lang.github.io/rust-project-goals/2025h1/pub-priv.html
- Cargo’s unstable `public-dependency` support already allows dependencies to be marked public/private and feeds the `exported_private_dependencies` lint.
  - https://doc.rust-lang.org/cargo/reference/unstable.html
- The `cargo-semver-checks` integration goal explicitly says the long-term direction is SemVer checking as part of the **`cargo publish` workflow**, with an override flag when the maintainer intentionally wants to proceed.
  - https://rust-lang.github.io/rust-project-goals/2025h1/cargo-semver-checks.html
- That same goal also says **more than 90% of real-world false-positives** are traceable to cross-crate items and that type-sensitive breakage still needs better evidence.
  - https://rust-lang.github.io/rust-project-goals/2025h1/cargo-semver-checks.html
  - https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- The 2025 GSoC work on witness generation says the roadmap now includes generating separate witness crates so the compiler itself can decide whether a type change is backward-compatible. That is concrete evidence that “semantic compatibility evidence” is becoming a first-class lane rather than a vague future dream.
  - https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo’s current development work keeps moving toward structured reporting and low-level plumbing, which makes a portable API evidence surface much more plausible than it was a few years ago.
  - https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## The missing layer
The ecosystem still lacks a standard answer to:
- **Public surface:** a normalized export of what a crate exposes
- **Cross-crate provenance:** which public items are local, reexported, or dependency-sourced
- **Dependency exposure:** which dependencies are declared public, inferred public, or drifting between those states
- **SemVer reasoning:** stable reason codes for why a change is breaking / non-breaking / ambiguous
- **Witness evidence:** compiler-checked verdicts for type-sensitive compatibility questions
- **MSRV evidence:** tested, not merely declared
- **Publish admission:** a reviewable record of whether a release would pass, fail, or require an explicit override / waiver

## Why this is more than library hygiene
A good solution would help with:
- safer `cargo publish` workflows
- more trustworthy crate release notes and CI gates
- dependency-policy tools that reason about *actual* public exposure, not just manifests
- better downstream packaging, audit, and distro review
- future build-graph work such as **relink-don’t-rebuild** by making interface boundaries more explicit and diffable
  - https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html

## What “done” looks like
A Rust team shipping a library should be able to produce one portable pack that answers:
1. what is the public API surface for this release?
2. what changed from the previous release?
3. which of those changes are structurally suspicious versus semver-breaking?
4. what did witness-based compiler checks prove about type-sensitive compatibility?
5. which dependencies, features, cfgs, and toolchains were part of that evaluation?
6. would this release pass a publish-time compatibility gate, or did it require an explicit override?

See: `design/public-api-kit.md`, `design/public-api-pilot-program.md`, and `proposals/epic-public-api-kit.md`.
