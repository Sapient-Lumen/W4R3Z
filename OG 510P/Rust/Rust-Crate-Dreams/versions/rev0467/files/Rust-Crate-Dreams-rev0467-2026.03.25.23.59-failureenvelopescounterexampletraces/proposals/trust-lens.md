---
id: P-0017
title: Trust Lens — identity-risk reports, assumption registers, and policy decisions for Rust dependency graphs
status: idea
domains: [security, supply-chain, ecosystem, cargo, crates-io]
last_reviewed: 2026-03-21
evidence:
  - https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  - https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
  - https://rustsec.org/advisories/RUSTSEC-2026-0027
  - https://rustsec.org/advisories/RUSTSEC-2026-0039
  - https://mozilla.github.io/cargo-vet/
  - https://arxiv.org/abs/2512.12553
  - https://arxiv.org/abs/2602.06466
---

# Problem

Rust dependency trust is no longer a question of just “is there an advisory?” and no longer a question of just “is this name spelled right?”

Today a team may have all of the following in play at once:

- confusable dependency names,
- crates.io Security-tab visibility,
- Trusted Publishing posture,
- RustSec advisories and malicious-crate removals,
- imported cargo-vet audits,
- Cargo Scan or other dangerous-effect findings,
- and research-grade trust models such as Cargo Sherlock,
- plus trust-watch channels that no longer have identical coverage (RustSec advisories/RSS, crate-page security surfaces, Trusted Publishing settings, and occasional blog posts).

Those are all useful.
But they still do **not** add up to one compact, reviewable answer to:

> what trust assumptions are we being asked to accept if we carry this dependency graph right now?

The missing crate is not merely a score calculator.
The missing crate is a **trust lens** that publishes identity risk, signal provenance, assumption registers, review debt, and local policy posture as explicit artifacts.

# What it provides

- `trust-policy.toml` — local trust posture and gates.
- `identity-risk.report.json` — confusable-name / impersonation / campaign-adjacent risk.
- `signal-basis.report.json` — which cues came from registry, advisory, audit, effect-analysis, research-model, or inference planes.
- `assumption-register.report.json` — the explicit assumptions carrying the trust posture.
- `review-debt.report.json` — unresolved dangerous-effect, context-sensitive, identity, or policy-exception work.
- `notification-channel.report.json` — which watch channels were consulted, which change classes they cover, and which decisive trust changes still have no configured route.
- `policy-decision.report.json` — `allow`, `warn`, `manual_review_required`, or `deny`.
- `cargo trust-lens capture` — capture graph and imported trust signals.
- `cargo trust-lens check` — apply local policy to the trust bundle.
- `cargo trust-lens diff` — compare trust posture across graph changes.
- `*.trustlensbundle.zip` — portable bundle for CI, review, or security triage.

# What the crate should provide other people

1. **One identity-risk answer** instead of informal “that looks suspicious” folklore.
2. **One signal-basis answer** instead of flattening crates.io, RustSec, audit imports, and local inference into one trust plane.
3. **One assumption register** instead of hiding trust posture inside a numeric result.
4. **One review-debt answer** instead of pretending imported audits erase remaining dangerous-code inspection work.
5. **One watch-coverage answer** instead of assuming blog posts, crate pages, and advisory feeds all surface the same trust changes.
6. **One policy decision** another team can review and gate on.

# Persona / who it’s for

- application teams adopting third-party crates
- platform/security teams curating approved dependency sets
- maintainers who want to publish trustworthy graph posture for downstreams
- pathfinder and policy-tool authors importing trust posture as one lane
- security researchers and audit teams who need a boring export surface above today’s substrate

# Users & user stories

- **Developer**: “Warn me if the dependency I added looks like a confusable or campaign-adjacent crate.”
- **Security reviewer**: “Show me exactly which cues came from RustSec, crates.io, cargo-vet, and local inference.”
- **Platform team**: “Gate CI on an explicit `manual_review_required` or `deny` posture rather than vibes.”
- **Audit lead**: “Import shared audits, but keep residual review debt visible.”
- **Maintainer**: “Explain why Trusted Publishing and a clean Security tab do not automatically erase trust concerns elsewhere in the graph.”

# Prior art (and why it’s insufficient)

- **crates.io Security tabs** and **RustSec** surface known vulnerability state at the point of discovery.
- **Trusted Publishing** improves release-identity posture.
- **cargo-vet** shares trusted audit work and supports deferred audits.
- **Cargo Scan** shrinks dangerous-code review scope by focusing inspection on effects and context-sensitive sites.
- **Cargo Sherlock** formalizes trust cost and explicit assumptions.

What remains missing is a **workflow-friendly joined bundle** that keeps those trust planes separate while still producing one conservative operational answer for a real dependency graph.

# Design goals

1. **Bundle, not badge** — publish reviewable trust posture rather than a shiny score.
2. **Identity risk is first-class** — confusable names and campaign-adjacent crates must stay explicit.
3. **Signal provenance matters** — registry/advisory/audit/research/inference sources must not be flattened.
4. **Assumptions must be inspectable** — trust posture should say what must be true for the result to hold.
5. **Residual review debt must survive import** — imported audits and registry signals do not erase unresolved dangerous-effect work.
6. **Composable** — pathfinder, policy, health, and off-ramp tooling should be able to import the artifacts.
7. **Watch coverage must be inspectable** — absence of a configured channel for a decisive change class must stay visible.

# MVP surface

- Minimal types: `IdentityRiskReport`, `SignalBasisReport`, `AssumptionRegisterReport`, `ReviewDebtReport`, `NotificationChannelReport`, `PolicyDecisionReport`
- Minimal functions:
  - `capture_identity_risk()`
  - `capture_signal_basis()`
  - `capture_assumption_register()`
  - `capture_review_debt()`
  - `capture_notification_channels()`
  - `check_policy()`
  - `write_bundle()`
- Feature flags:
  - `cratesio-import`
  - `rustsec-import`
  - `cargo-vet-import`
  - `cargo-scan-import`
  - `bundle`

# Compatibility story

- Starts with resolved graphs plus a small set of imported registry/advisory/audit signals.
- Treats Cargo Sherlock-style trust cost as an **optional derived view**, not the contract.
- Treats Cargo Scan-style effect results as **review debt input**, not as the whole tool.
- Can be consumed by pathfinder or org-policy tooling without becoming a recommender.
- Degrades honestly to `manual_review_required` when identity or review posture is unclear.

# Conformance & fixtures

- recent campaign-adjacent confusable names
- blog-only malware watch with no RustSec RSS or equivalent advisory feed configured
- Security-tab and Trusted Publishing imports without an always-on malware-removal watch route
- clean security/advisory posture but unresolved identity review
- imported cargo-vet audit with unresolved context-sensitive review debt
- graph with strong publishing identity but weak trust conclusions
- popularity/release activity that would mislead if treated as the verdict

# Path to boring stability

- Stabilize `identity-risk`, `signal-basis`, `assumption-register`, `review-debt`, and `policy-decision` before expanding analytics.
- Keep `manual_review_required` as a first-class honest outcome.
- Prefer importing a few boring signals well over scraping every soft metric.
- Keep pathfinder choice, crate health, and off-ramp planning as adjacent but separate lanes.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 24/30**

# Minimum lovable MVP

A crate that captures one resolved dependency graph, imports a small set of registry/advisory/audit signals, emits identity-risk / signal-basis / assumption-register / review-debt reports, and produces a conservative policy-decision verdict another team can actually review.

# De-risk plan

1. Keep `0.1` focused on identity risk, trust-plane provenance, assumptions, and review debt.
2. Treat any numeric trust cost as secondary to explicit artifacts.
3. Keep audit/effect-analysis importers modular and optional.
4. Prove usefulness first on policy-gated internal dependency workflows.

# Non-goals

- Not a global trust leaderboard.
- Not a crates.io moderation or takedown engine.
- Not a replacement for cargo-vet, cargo-audit, Cargo Scan, or Cargo Sherlock.
- Not a popularity score with security branding.

# Architecture & API sketch

```rust
pub fn capture_identity_risk(input: &TrustInput) -> Result<IdentityRiskReport>;
pub fn capture_signal_basis(input: &TrustInput) -> Result<SignalBasisReport>;
pub fn capture_assumption_register(input: &TrustInput) -> Result<AssumptionRegisterReport>;
pub fn capture_review_debt(input: &TrustInput) -> Result<ReviewDebtReport>;
pub fn check_policy(bundle: &TrustBundle, policy: &TrustPolicy) -> Result<PolicyDecisionReport>;
pub fn write_bundle(bundle: &TrustBundle, out: &Path) -> Result<()>;
```

Bundle draft: `trust-policy.toml`, `identity-risk.report.json`, `signal-basis.report.json`, `assumption-register.report.json`, `review-debt.report.json`, `notification-channel.report.json`, `policy-decision.report.json`, `notes.md`.

# Security / safety model

- Do not treat absence of advisories as proof of safety.
- Do not treat Trusted Publishing as proof of code trustworthiness.
- Keep imported audits and effect findings auditable and versioned.
- Avoid scraping unstable or private maintainer data.
- Prefer explicit `manual_review_required` outcomes over weak auto-approval.

# Maintenance & governance plan

- Version the trust artifacts carefully.
- Keep importers modular.
- Publish lane boundaries so future revisions do not flatten trust into crate health, pathfinder, or registry policy.
- Prefer explicit assumptions over hidden magic numbers.

# Milestones

## 0.1
- identity-risk report
- signal-basis report
- assumption register
- review-debt report
- policy decision

## 0.2
- richer audit/effect import adapters
- optional Cargo Sherlock cost export
- org-policy helpers and decision diff support

## 1.0
- stable artifact core
- ecosystem integration guidance
- reviewed fixture corpus across real graph shapes

# Open questions

- Which confusable-name heuristics should be hard gates versus warnings?
- How much audit import should be considered enough before review debt moves from `manual_review_required` to `warn`?
- Which weak signals are useful tie-breaks without becoming score theatre?

# Sources

- crates.io development update: https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io malicious crate notification policy update: https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- `tracings` RustSec advisory: https://rustsec.org/advisories/RUSTSEC-2026-0027
- `chrono_anchor` RustSec advisory: https://rustsec.org/advisories/RUSTSEC-2026-0039
- Cargo Vet book: https://mozilla.github.io/cargo-vet/
- Cargo Sherlock paper: https://arxiv.org/abs/2512.12553
- Auditing Rust Crates Effectively / Cargo Scan paper: https://arxiv.org/abs/2602.06466
