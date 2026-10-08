# Gap: Resolution strategy is still mostly hidden in flags, lockfiles, and maintainer memory

## Summary
Cargo is getting much better at **resolving** dependency graphs, but Rust still lacks a first-class way to review and exchange the **strategy** behind a resolution choice.

That gap is becoming sharper because Cargo is no longer solving one obvious “latest wins” problem:
- the MSRV-aware resolver is now real and tied to resolver v3 / Rust 2024 defaults;
- workspaces can carry multiple `rust-version` policies that interact in surprising ways;
- Cargo still exposes `minimal-versions` and `direct-minimal-versions` as explicit alternative objectives;
- Cargo has started experimenting with publish-time-aware “time traveling dependency resolution” and is exploring `minimumReleaseAge`-style controls;
- downstream consumers like semver analysis increasingly need accurate feature and dependency provenance, not just a final lockfile.

The ecosystem has ingredients for all of this:
- `Cargo.lock`,
- resolver docs,
- MSRV docs,
- unstable knobs,
- PubGrub groundwork,
- `cargo tree`,
- and the archive’s own **Resolution Doctor** and **Dependency Control** ideas.

What is still missing is a portable answer to questions like:
1. **What objective was this lockfile trying to satisfy?**
2. **Which acceptable alternatives were considered or deliberately excluded?**
3. **Which tradeoffs were accepted** (newer versions, lower versions, older publish dates, workspace unification, MSRV fallback, direct-minimal checks, etc.)?
4. **What uncertainty remained** because Cargo data or registry history was incomplete?
5. **Which downstream consumers** (publish review, migration, support, semver, policy) may safely import the result?

This is the gap: **Rust has chosen-graph evidence, but not yet a shared resolution-strategy substrate.**

## Why this gap is sharper now
- The PubGrub-in-Cargo goal says the work is intended to support better error messages, better MSRV support, CVE-aware resolution, and a richer ecosystem of Cargo extensions. That is strong evidence that resolution is becoming an extension surface rather than a sealed black box.
  https://rust-lang.github.io/rust-project-goals/2025h1/pubgrub-in-cargo.html
- Rust 1.84 stabilized the MSRV-aware resolver, and the Rust 2024 edition guide says `edition = "2024"` implies resolver v3 and `incompatible-rust-version = "fallback"` by default. That means selection policy is now part of ordinary project configuration, not niche nightly lore.
  https://blog.rust-lang.org/2025/01/09/Rust-1.84.0/
  https://doc.rust-lang.org/edition-guide/rust-2024/cargo-resolver.html
- Cargo's resolver docs say `Cargo.lock` generation happens as if all features of all workspace members are enabled, followed by a second pass to determine the actual features used for compilation. That is strong evidence that one final lockfile outcome is not the whole strategy story.
  https://doc.rust-lang.org/cargo/reference/resolver.html
- Cargo’s `rust-version` docs say workspaces can have multiple policies and that verification gets complicated because shared dependencies unify across policies. That is strong evidence that maintainers need more than one opaque lockfile outcome.
  https://doc.rust-lang.org/cargo/reference/rust-version.html
- RFC 3537 continues to evolve the MSRV-aware resolver and explicitly discusses shifting some failures into diagnostics and making unofficial support postures easier to express. That is a strong sign that resolution intent and acceptance posture are still an active design surface, not a settled one-time toggle.
  https://rust-lang.github.io/rfcs/3537-msrv-resolver.html
- Cargo’s unstable docs still expose `minimal-versions`, `direct-minimal-versions`, and `msrv-policy`, which are not random experiments: they are explicit alternative resolution objectives that teams already need to reason about.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo 1.93 added publish-time-aware resolution groundwork and documents “time traveling dependency resolution” plus ongoing exploration of `minimumReleaseAge`. That is exactly the kind of policy-sensitive objective that deserves a reviewable artifact layer instead of living in one-off CLI invocations.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- The July 2025 project-goals update for `cargo-semver-checks` says recursive active dependency features are still not available through the lockfile or any Cargo interface. That means downstream consumers still need clearer resolution-side provenance than the ecosystem currently exports.
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/

## What a worthy contribution would look like
A worthy contribution here is **not** a solver fork, **not** a global policy engine, and **not** one “best dependency graph” command.

It would instead provide:
- a **named objective profile** for why a resolution was performed;
- an **attachable decision report** linking objective → chosen graph → accepted tradeoffs;
- optional **candidate/alternative summaries** that stay honest about incompleteness;
- explicit **workspace / MSRV / publish-time / minimal-version posture**;
- and a portable import lane for migration, public-API, policy, support, and release consumers.

## Archive decision
Add a first-class **Resolution Strategy Kit** and promote a broader **Resolution Strategy Stack** above the existing Dependency Control layer.

The key design rule should be:
> **Resolution Doctor explains what Cargo chose; Resolution Strategy explains what objective was pursued, what alternatives mattered, and why this choice was acceptable for this consumer.**
