---
id: P-0034
title: cargo-update-policy — safer dependency upgrades via holds, forbid-lists, and publish-time (“pubtime”) gating
status: idea
domains: [cargo, supply-chain, enterprise, policy, tooling]
last_reviewed: 2026-03-01
evidence:
  - https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
  - https://github.com/rust-lang/cargo/issues/15491
  - https://internals.rust-lang.org/t/zminimal-versions-cargo-update-and-cargo-upgrade/21335
needs:
  - Teams need gradual rollouts (avoid upgrading to “brand new” releases immediately).
  - Teams need “hold” or “forbid this version” mechanisms to mitigate regressions or supply-chain events.
  - CI needs deterministic, explainable decisions about why an update was (not) applied.
risks:
  - Overlaps with (future) built-in Cargo behavior; must integrate cleanly and degrade gracefully.
  - Registry publish-time data may be incomplete for non-crates.io registries; design for partial data.
  - Policy complexity can become a footgun; must have safe defaults and clear explanations.
---

## Problem
Cargo’s dependency update experience is optimized for “get me the newest compatible versions”, but real-world teams also need **safe rollout control**:
- *Delay upgrades* until versions are “old enough” (catch bad releases / compromised packages).
- *Hold* specific dependencies at known-good versions.
- *Forbid* known-bad versions (hotfix response).
- Make update decisions **auditable and explainable** (why was this chosen, why was that blocked?).

Cargo itself has signaled interest in publish-time-aware resolution (“pubtime”) for gradual rollouts, and the registry index is considering adding release dates—so the ecosystem is ready for tooling that makes this workflow usable now.

## Users & user stories
- **Security-conscious teams:** “Don’t upgrade any dependency unless it’s at least 14 days old, unless it fixes a CVE.”
- **Library maintainers:** “Hold back a transitive dep bump that breaks MSRV, while allowing other updates.”
- **Release engineers:** “Roll out updates gradually across services; attach a policy report to the PR.”

## Prior art (and why it’s insufficient)
- `cargo update` updates the lockfile but doesn’t provide policy primitives like “min age”, “hold”, “forbid”.
- `cargo-edit`/`cargo upgrade` focuses on editing manifests, not **update governance**.
- Renovate/Dependabot can approximate some rules, but they’re not Cargo-native and don’t integrate with local workflows or non-GitHub setups.

## Design goals
- **Explainability first:** every decision has a reason string and evidence (e.g., publish-time, policy rule, advisory exception).
- **Local-first, deterministic:** no telemetry; decisions depend only on local inputs + registry data.
- **Composable with Cargo:** produce an *update plan* that can be applied with normal Cargo commands.
- **Gradual adoption:** works in “report-only” mode first.

### Non-goals
- Replace Cargo’s resolver.
- Decide “what is secure” globally; this is a policy engine, not a security oracle.

## Architecture & API sketch
### CLI shape (Cargo plugin)
- `cargo update-policy plan [--format json|md]`  
  Outputs an **Update Plan**: allowed/blocked updates, reasons, and suggested commands.
- `cargo update-policy apply`  
  Applies the plan (runs `cargo update -p ...`, optionally `cargo check/test`).
- `cargo update-policy explain <pkg>`  
  Shows why the current version is held, why newer versions are blocked, etc.

### Policy file
`CargoUpdatePolicy.toml` (or `.cargo/update-policy.toml`):
- `min_age_days = 14`
- `holds = { "serde" = ">=1.0,<1.0.200" }` (freeze within a range) or `holds = ["serde"]` (freeze at current)
- `forbid = { "time" = ["0.3.35"] }`
- `exceptions = { advisory = ["RUSTSEC-..."], allow_unaged = ["tokio"] }`

### Data sources
- Prefer registry index metadata if it contains publish time (future-friendly).
- Fallback to crates.io API for publish time when needed (pluggable provider interface).

## Security / safety model
- Treat registry metadata as *untrusted input*; validate and explain missing/ambiguous dates.
- Provide a “paranoid mode”: require verified sources (pairs well with TUF/mirroring efforts).
- Always show what the tool *assumed* (e.g., “publish time unknown; treated as too new”).

## Maintenance & governance plan
- Dependency-minimal (avoid huge HTTP stacks if possible; keep an optional feature for API lookups).
- Tight test fixtures with synthetic registries (unit) + real-workspace smoke tests (integration).
- Publish policy schema versioning (avoid breaking configs).

## Milestones
### 0.1
- Policy file parsing + `plan` (report-only).
- Publish-time fetcher for crates.io (API) + cache.
- Holds + forbid list + min-age rule.

### 0.2
- `apply` mode + CI-friendly output (SARIF/JSON).
- Exception mechanism for advisories (pluggable, can integrate later with RustSec).

### 1.0
- Registry-agnostic publish-time support (index metadata when available).
- “Update windows” (e.g., allow upgrades only on weekdays), optional.

## Open questions
- Where should policy live: repo root vs `.cargo/`?
- Should “age gating” apply only to **new** versions, or also to yanked versions?
- Best UX for holds: freeze-at-current vs freeze-within-range?

## Sources
- https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- https://github.com/rust-lang/cargo/issues/15491
- https://internals.rust-lang.org/t/zminimal-versions-cargo-update-and-cargo-upgrade/21335
