---
id: P-0006
title: stdx-curated — dependency-minimal “missing batteries” facade
status: idea
domains: [dx, stdlib, dependencies]
last_reviewed: 2026-02-28
evidence:
  - https://users.rust-lang.org/t/stdx-the-missing-batteries-of-rust/2015
  - https://www.reddit.com/r/rust/comments/1dukybe/rust_has_a_huge_supply_chain_security_problem/
  - https://00f.net/2025/10/17/state-of-the-rust-ecosystem/
---

# Problem
Rust’s ecosystem is powerful but can feel like “import 400 crates for basics.” People have long asked for a “missing batteries” layer, and supply-chain / abandonment concerns amplify the cost of deep dependency trees.

# Users & user stories
- Teams with strict dependency policies: “We need a small, audited set of crates.”
- Newcomers: “What’s the default choice for common tasks?”
- Tool authors: “I want standard utilities without pulling in the world.”

# Prior art (and why it’s insufficient)
- Past `stdx` efforts highlight demand, but macro reexports and long-term curation are hard.
- Ecosystem stats show many crates become “one-shot” or stale, increasing risk.

# Design goals
- A curated facade that:
  - reexports a small set of “golden path” crates
  - enforces MSRV + semver policies
  - publishes a “dependency budget” report
- Works with macros:
  - provide wrapper macros or module-level reexports where possible
- Provide “profiles” via features:
  - `stdx-curated::net`, `::cli`, `::serde`, etc.

# Non-goals
- Becoming a competing standard library.
- Reexporting *everything*.

# Architecture & API sketch
- `stdx-curated` as a facade crate.
- A `curation/` directory with:
  - selection criteria
  - threat model
  - deprecation and replacement policy

# Security / safety model
- RustSec + vetting integration in CI.
- Minimal default features; explicit opt-ins.

# Maintenance & governance plan
- Curation committee + transparent criteria.
- “Adopted crates” policy with succession plan.

# Milestones
- 0.1: initial facade + 10–20 carefully chosen crates
- 0.2: macro strategy + docs
- 0.3: automated dependency budget + security gates
- 1.0: stable “golden path” with release notes

# Sources
- https://users.rust-lang.org/t/stdx-the-missing-batteries-of-rust/2015
- https://www.reddit.com/r/rust/comments/1dukybe/rust_has_a_huge_supply_chain_security_problem/
- https://00f.net/2025/10/17/state-of-the-rust-ecosystem/
