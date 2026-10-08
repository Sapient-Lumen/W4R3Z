---
id: P-0023
title: vet-workbench
status: idea
domains: [security, supply-chain, tooling, ux]
last_reviewed: 2026-03-01
evidence:
  - https://github.com/mozilla/cargo-vet/issues/554
  - https://github.com/mozilla/cargo-vet/issues/552
  - https://mozilla.github.io/cargo-vet/how-it-works.html
  - https://lwn.net/Articles/897435/
---

# Problem
`cargo-vet` is a powerful approach to sharing audit work, but adoption is limited by *workflow friction*:
- doing audits is inherently hard, and
- the UX around creating, reviewing, and managing audits (and “violations”) often doesn’t fit how teams actually work.

There are explicit requests for a **web frontend / workbench** for certify workflows, better source graph UX, and practical handling of violations.

# Users & user stories
- **Security engineer**: “I need to certify and review unsafe code audits with a UI that can render diffs reliably.”
- **Maintainer**: “I want to adopt cargo-vet, but violations and graph complexity are blocking.”
- **Organization**: “We need a repeatable workflow that fits PR review and can run offline.”

# Prior art (and why it’s insufficient)
- `cargo-vet` CLI and docs: strong core, intentionally minimal UI.
- Ad-hoc internal tools: expensive to build and not shareable.
- General code review UIs: not tailored to crate graph + audit semantics (certs, exemptions, violations).

# Design goals
1. **First-class UX** for certify workflows: “what do I review, why, and what changed?”
2. **Source graph clarity**: consistent diffs, vendored sources, and “empty repo” edge cases.
3. **Practical violation handling** with explicit, auditable exceptions (without weakening the policy model).
4. **Pluggable analyzers**: allow importing “audit-lens” artifacts (effects / unsafe summaries) to reduce human review.
5. **Offline-first**: run locally; optional integration with GitHub/GitLab.

# Non-goals
- Replacing cargo-vet or changing its data model by force.
- Becoming a generic SCA product.

# Architecture & API sketch
## Components
- `vet-workbench-core` (library): parses cargo-vet stores, resolves sources, computes review sets and diffs.
- `vet-workbench-cli`: `serve`, `review`, `certify` helpers.
- `vet-workbench-ui` (optional): web UI (can be a separate crate/binary).

## UX primitives
- **Review session**: a bundle of crate versions + diffs + notes + decision.
- **Evidence pack**: optional attachments (links, notes, analyzer outputs) stored alongside the audit.

## Commands (MVP)
- `vet-workbench serve` — local web UI over a workspace
- `vet-workbench review <crate> <from..to>` — generate a review session bundle
- `vet-workbench certify <session>` — emit the cargo-vet certification (with guardrails)

# Security / safety model
- Runs locally by default; no code upload.
- Optional VCS tokens are read-only where possible.
- Evidence packs are content-addressed to discourage tampering.

# Maintenance & governance plan
- Target tight integration with cargo-vet versions; track changes via CI fixtures.
- Encourage extension crates for analyzers and org-specific policies.
- Provide a “minimum viable UI” that is easy to fork, not a monolith.

# Milestones
- **0.1**: core library to load vet store + resolve crate sources + stable diff rendering (git + registry).
- **0.2**: local web UI + review sessions + certify output.
- **0.3**: violation handling UI + policy explanations (explicit exceptions).
- **0.4**: analyzer plugin interface + import of effect/unsafe summaries.
- **1.0**: stable session format + GitHub PR integration guide.

# Open questions
- Should it embed a browser UI, or only output portable bundles that can be opened by any UI?
- How to standardize analyzer outputs without freezing innovation?

# Sources
- Feature request: web frontend for certify — https://github.com/mozilla/cargo-vet/issues/554
- Adoption pain: dealing with violations — https://github.com/mozilla/cargo-vet/issues/552
- cargo-vet design principles — https://mozilla.github.io/cargo-vet/how-it-works.html
- Ecosystem context: “Vetting the Cargo” — https://lwn.net/Articles/897435/
