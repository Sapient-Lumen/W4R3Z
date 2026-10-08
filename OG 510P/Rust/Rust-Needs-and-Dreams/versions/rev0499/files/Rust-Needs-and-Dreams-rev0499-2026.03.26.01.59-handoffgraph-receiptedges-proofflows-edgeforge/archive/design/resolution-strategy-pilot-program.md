# Design: Resolution Strategy Pilot Program

## Why this pilot program exists
The archive now has enough evidence to treat **resolution strategy** as a distinct seam above ordinary dependency-control facts.

Without a pilot program, this area is likely to fall into one of four traps:
1. **flag theater** — strategy hidden in one CI command or local config file;
2. **lockfile theater** — reviewers see only the outcome and not the objective;
3. **policy theater** — teams jump straight to verdicts without first describing the strategy they wanted;
4. **migration theater** — upgrades look like random graph churn instead of named strategy changes.

A worthy contribution should prove a smaller and stronger claim:
> Rust projects can attach enough strategy evidence that reviewers know *what kind of resolution was intended*, *which tradeoffs were accepted*, and *what downstream consumers may reuse*.

## Primary signals
- PubGrub-in-Cargo is explicitly groundwork for better MSRV support, CVE-aware resolution, and richer extensions:
  https://rust-lang.github.io/rust-project-goals/2025h1/pubgrub-in-cargo.html
- Rust 2024 / resolver v3 makes MSRV fallback part of ordinary project posture:
  https://doc.rust-lang.org/edition-guide/rust-2024/cargo-resolver.html
- Cargo’s `rust-version` docs say mixed-policy workspaces are complicated:
  https://doc.rust-lang.org/cargo/reference/rust-version.html
- Cargo unstable docs expose `minimal-versions`, `direct-minimal-versions`, and `msrv-policy` as real alternative objectives:
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo 1.93 is actively exploring publish-time-aware resolution and minimum-release-age ideas:
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- `cargo-semver-checks` still needs better dependency-feature provenance from Cargo interfaces:
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/

## Shared pilot artifacts
- `resolution-objective/v0`
- `resolution-decision-report/v0`
- optional `resolution-candidate-report/v0`
- optional `resolution-strategy-diff/v0`
- imported `resolve-report/v0` / `feature-report/v0`
- `resolution-strategy-pack/v0`

## Ranked rollout
### Pilot 1 — Direct-minimal validation lane
Use one ordinary library crate that wants to verify lower bounds honestly.

Must prove:
- a named objective profile for `direct-minimal-check`;
- imported chosen-graph and feature truth;
- explicit accepted tradeoffs when the direct-minimal lane diverges from latest;
- explicit note that lockfile generation posture and compile-time feature posture are related but not identical;
- no policy or semver overclaiming.

Why first:
- it is concrete and teachable;
- Cargo already exposes the lane;
- it forces the archive to separate “strategy” from “graph outcome”.

### Pilot 2 — Workspace multi-MSRV lane
Use one workspace with different `rust-version` expectations across members.

Must prove:
- per-selection objective reports;
- explicit unification/split-selection truth;
- clear notes on which member policy constrained which shared dependency;
- honest partial or awkward outcomes.

Why second:
- Cargo’s own docs say this case is complicated;
- it is where strategy becomes obviously more than a single lockfile.

### Pilot 3 — Publish-time / release-age lane
Use one registry-backed package set where historical selection matters.

Must prove:
- explicit publish-time posture;
- bounded confidence notes about registry-history gaps, mirror gaps, or yanked-history limits;
- candidate comparison between ordinary latest and time-bounded resolution;
- honest notes about what was reconstructed versus directly observed;
- no false promise of perfect historical replay.

Why third:
- Cargo 1.93 makes this newly real;
- it proves the kit can model emerging objectives without pretending they are already settled.

### Pilot 4 — Release-admission / semver handoff lane
Use one package approaching release review.

Must prove:
- the strategy report can hand off to Public API / Package Admission consumers;
- recursive dependency-feature needs are stated honestly;
- semver or publish conclusions are imported later, not silently baked into strategy.

Why fourth:
- it connects strategy work to an ecosystem-critical consumer without flattening boundaries.

### Pilot 5 — Migration / support / policy consumer lane
Use one upgrade or long-support case.

Must prove:
- strategy diffs across revisions;
- migration consumers can import strategy evidence without replacing their own source→destination logic;
- support/policy users can tell what was intended without pretending strategy equals approval.

Why fifth:
- this is high leverage but only after earlier boundaries are proven.

## Success criteria
The pilot program is working when reviewers can see:
- what strategy profile was active,
- what Cargo-native facts were imported,
- what tradeoffs were accepted,
- what alternatives mattered,
- and what downstream consumers may legitimately reuse.

## Failure modes to avoid
- Starting with a global “best graph” optimizer.
- Smuggling policy verdicts into objective profiles.
- Pretending publish-time or candidate comparison is complete when registry history is incomplete.
- Flattening workspace multi-policy cases into one graph narrative.
- Making downstream consumers re-derive chosen-graph truth anyway.
