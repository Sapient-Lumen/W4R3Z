---
id: P-0016
title: Audit Lens — effect-focused dependency auditing artifacts that compose with cargo-vet
status: idea
domains: [security, auditing, supply-chain, cargo]
last_reviewed: 2026-03-01
evidence:
  - https://arxiv.org/abs/2602.06466
  - https://mozilla.github.io/cargo-vet/
  - https://mozilla.github.io/cargo-vet/how-it-works.html
  - https://github.com/google/rust-crate-audits
---

# Problem
`cargo-vet` helps track and share audits, but it does not reduce the core pain: **auditing large dependency DAGs is expensive**.
Recent work (“Cargo Scan”) suggests that *effect- and context-aware analysis* can dramatically reduce the amount of code humans must inspect, producing composable audit files.
The ecosystem is missing a stable, tool-agnostic artifact format and workflow glue so these analyses can become a shared, interoperable auditing layer.

# Users & user stories
- **Org security teams**: “Focus audits on the few crates/effects that matter and reuse results across repos.”
- **Maintainers**: “Provide a machine-checkable ‘audit surface map’ for my crate.”
- **CI owners**: “Fail builds if a dependency introduces new high-risk effects that aren’t audited.”

# Prior art
- Cargo Scan research prototypes produce audit files, but there is no widely adopted standard schema + diff tooling.
- `cargo-vet` is a natural home for human trust decisions; we should complement, not replace it.

# Design goals
- Stable schema for **effect maps** and **audit decisions** that:
  - is tool-agnostic (Cargo Scan first; others later),
  - is diffable and composable,
  - supports context-dependent safety (call-site dependent effects).
- Provide ergonomic review tools:
  - “what changed since last release?”
  - “why does this dependency fail policy?”

# Architecture & API sketch
## Crates
- `audit_lens_schema` (no heavy deps): types + serde for `AuditMap`, `Effect`, `Context`, `Decision`
- `audit_lens_cli`
  - `audit-lens import cargo-scan <path>`
  - `audit-lens diff <old> <new>`
  - `audit-lens check --policy policy.toml`
- Optional: `audit_lens_vet` adapter to emit `cargo-vet` compatible entries / criteria hints.

## Core data model (sketch)
- `EffectKind`: `unsafe`, `ffi`, `io`, `net`, `process`, `fs`, `crypto`, `alloc_unbounded`, ...
- `Effect { id, kind, span?, summary, provenance }`
- `AuditMap { crate, version, effects: Vec<Effect>, edges: Vec<CallEdge>, decisions: Vec<Decision> }`
- `Decision { effect_id, verdict, justification, reviewer, date, constraints }`

# Workflow
1) Analyzer produces effect map.
2) Humans audit the small set of effects.
3) CI checks that new effects have decisions or are blocked.

# Security / safety model
- Audit artifacts are security-sensitive; support signing (future: reuse `cargo-attest` signing interface).
- Ensure deterministic ids and stable sorting for diffs.

# Maintenance & governance plan
- Keep schema stable; use versioned JSON.
- Maintain golden fixtures based on popular crates (hyper et al) as suggested by the Cargo Scan evaluation.

# Milestones
- **0.1**: schema + diff tool + policy check
- **0.2**: Cargo Scan importer + review UX
- **0.3**: cargo-vet adapter + examples importing public audits (e.g., Google’s)
- **1.0**: stable schema v1 + signed artifacts + docs

# Scorecard (0–5)
- Impact: 5
- Neglectedness: 4
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 5

# Sources
- https://arxiv.org/abs/2602.06466
- https://mozilla.github.io/cargo-vet/
- https://mozilla.github.io/cargo-vet/how-it-works.html
- https://github.com/google/rust-crate-audits
