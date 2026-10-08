---
id: P-0093
title: Differential Privacy Application Kit (OpenDP-powered) — budgets, policy, reports, and cargo doctor tooling
status: idea
domains: [privacy, data, devtools, governance, safety]
last_reviewed: 2026-03-05
evidence:
  - https://docs.rs/opendp/latest/opendp/
  - https://github.com/opendp/opendp
  - https://opendp.org/tools/
  - https://docs.opendp.org/
  - https://docs.opendp.org/en/stable/contributing/development-environment.html
---

# Problem
Differential privacy (DP) is “easy to misuse”: the math is subtle and the “sharp edges” are often in *application glue*:
- budget management and composition
- policy constraints and auditing
- safe defaults and guardrails
- reproducible reporting suitable for CI and review

Rust has a serious DP foundation via OpenDP, but most Rust teams still lack a standard, ergonomic application kit.

# What it provides
A crate suite focused on “DP done right in production”:

- **Budget accounting**
  - `BudgetLedger` with named spends and composition rules (ε, δ)
  - fail-closed behavior when overspending or missing constraints
- **Policy surface**
  - declarative policies (allowed releases, min group size, sensitivity bounds)
  - exportable policy + spend reports for review (`*.dpreport.json`)
- **Pipeline ergonomics**
  - safe builders for common releases (count/sum/mean/histogram/quantiles)
  - adapters to common Rust data containers
- **Testing hooks**
  - “privacy unit tests”: assert spend totals, required clamps, required min group size
- **Cargo UX**
  - `cargo dp-doctor`: checks common footguns (e.g., opting into risky floating-point modes without explicit acknowledgment)
  - `cargo dp-report`: generate CI-ready reports

# Users & user stories
- **Data/analytics teams in Rust services**: “Add DP to a metrics pipeline without becoming DP experts.”
- **Security/privacy reviewers**: “See a machine-readable privacy report; reject unreviewed changes.”
- **Platform teams**: “Standardize privacy budgets and enforcement across microservices.”

# Prior art (and why it’s insufficient)
OpenDP is a strong core library, but it intentionally does not solve all application-layer concerns (policy, budgets, end-to-end workflows). The OpenDP “Commons” direction underscores the need for tooling layers.

# Design goals
- Fail-closed defaults; explicit opt-in for sharp edges.
- Artifact-first: produce reports that can be versioned and reviewed.
- Integration-first: fit into existing Rust services and CI pipelines.

# Non-goals
- Replacing OpenDP’s core primitives.
- Building a full SQL planner (future layer possible).

# Architecture & API sketch
- `dp_kit_core`
  - `BudgetLedger`, `Policy`, `Report`
- `dp_kit_opendp`
  - safe wrappers/builders mapping to OpenDP
- `dp_kit_cli`
  - doctor + report generation

# Security / safety model
- Clear “modes” that annotate risk and require explicit acknowledgment.
- Reports designed to avoid leaking sensitive raw data.

# Maintenance & governance plan
- Version artifact formats.
- Require privacy-review notes for any API that changes privacy semantics.

# Milestones
- 0.1: budgets + policy + report + basic OpenDP adapters
- 0.2: doctor checks + more release builders
- 0.3: integration examples for common service stacks
- 1.0: stable report format + compatibility policy

# Open questions
- Best representation of policies (Rust types vs TOML/JSONSchema).
- How to expose guarantees for non-experts without oversimplifying.

# Sources
- See evidence links above.
