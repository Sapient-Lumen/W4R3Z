# Gap: Feature Graph Control & Explainability (minimal feature sets, unification policy, diffs)

## Summary
Cargo features are a powerful “optional compilation” mechanism, but they create systemic pain:
- Feature unification can silently pull in capabilities you did not intend (bloat, extra dependencies, unsafe optional codepaths).
- Users often ask: *“Why is this feature enabled?”* and the answers are not consistently available in CI artifacts.
- Teams struggle to enforce “minimal features” discipline, and regressions are hard to catch during dependency upgrades.

Cargo has improved tooling (`cargo tree` can show why features are enabled), and the resolver has evolved (new feature resolver, work on feature-unification controls).
But the ecosystem still lacks a **standard workflow + report artifacts** for:
- computing minimal viable feature sets for a target build,
- diffing feature-graph changes across PRs,
- enforcing org policy around unification and “feature creep”.

## Ecosystem signals
- Cargo Book: features are unified (union) when a dependency is used by multiple packages.  
  https://doc.rust-lang.org/cargo/reference/features.html
- Rust 2021 Edition Guide: `cargo tree` can show which features are enabled and why.  
  https://doc.rust-lang.org/edition-guide/rust-2021/default-cargo-resolver.html
- RFC 2957 stabilized the “new feature resolver” behavior (features not always unified the same way).  
  https://rust-lang.github.io/rfcs/2957-cargo-features2.html
- Cargo unstable: `-Z feature-unification` and `resolver.feature-unification` provide knobs for controlling feature unification (tracking issue referenced there).  
  https://doc.rust-lang.org/cargo/reference/unstable.html
- RFC 3692 proposes giving users control over feature unification across selected packages.  
  https://github.com/rust-lang/rfcs/blob/master/text/3692-feature-unification.md
- Community discussions keep resurfacing “opt-out of feature unification” requests in workspaces.  
  https://internals.rust-lang.org/t/feature-unification-opt-out-in-workspace-crate/20507

## What “good” looks like
- A single tool that can:
  - compute effective features for a build target,
  - compute a “minimal features” recommendation,
  - diff feature graphs between commits,
  - enforce org policy (deny risky features, require explicit allowlists).
- Portable reports that Policy/Trust/Perf tools can ingest.
