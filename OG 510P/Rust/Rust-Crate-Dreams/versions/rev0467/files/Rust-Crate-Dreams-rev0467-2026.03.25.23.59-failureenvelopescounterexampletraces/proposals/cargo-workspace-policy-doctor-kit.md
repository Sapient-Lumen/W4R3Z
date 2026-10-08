---
id: P-0109
title: Cargo Workspace Policy Doctor Kit
status: idea
domains: [cargo, devtools, supply-chain, policy, ci]
last_reviewed: 2026-03-05
evidence:
  - https://rustsec.org/
  - https://github.com/EmbarkStudios/cargo-deny
  - https://mozilla.github.io/cargo-vet/
  - https://doc.rust-lang.org/cargo/commands/cargo-vendor.html
  - https://internals.rust-lang.org/t/is-it-possible-to-standardize-additional-config-file-naming/23900
---

# Problem

Rust projects that take supply-chain and compliance seriously end up assembling a **stack of tools and config files**:
`cargo-audit`/RustSec advisories, `cargo-deny` policies, `cargo-vet` audits, vendoring/offline builds, SBOM generation, rustfmt/clippy/toolchain config, etc.

The pieces are good — but the *integration experience* is often ad-hoc, inconsistent across repos, and hard to keep “green” as teams scale.

# What it provides

A crate + cargo subcommand that turns best practices into a **repeatable, explainable workflow**:

1. **A “policy bundle” format** (`policy/` directory with a versioned manifest):
   - advisories policy (RustSec)
   - deny policy (licenses/bans/sources)
   - vet policy (criteria + subtree rules)
   - offline/vendoring expectations
   - toolchain/MSRV policy (optional)
   - a single `policy.lock.json` produced by the doctor for CI

2. **A cargo-native UX**: `cargo policy <cmd>`
   - `cargo policy init` generates sane defaults
   - `cargo policy check` runs the configured checks and emits:
     - `policy-report.json` (stable, diffable)
     - `policy-report.md` (human summary)
   - `cargo policy doctor` suggests fixes (missing config, common miswires)

3. **Interoperability adapters** (don’t replace tools):
   - call out to `cargo-deny`, `cargo-audit`, `cargo-vet`, `cargo vendor` as configured
   - normalize outputs into a single report schema

4. **CI profiles**
   - “PR fast lane” (advisories + minimal checks)
   - “weekly deep lane” (licenses, bans, full vet, vendor drift)

# Users & user stories

- **Maintainers**: “I want contributors to run one command and get consistent policy results.”
- **Platform/security teams**: “I want enforceable policy + stable reporting + diff in CI.”
- **Downstream packagers**: “I want a machine-readable summary of dependency risk posture.”

# Prior art (and why it’s insufficient)

- RustSec provides the advisory DB and `cargo-audit` guidance, but doesn’t standardize workspace policy bundles. (See evidence.)
- `cargo-deny` is powerful but repo-to-repo config varies widely. (See evidence.)
- `cargo-vet` helps with audits and policies, but integrating with the rest of the policy stack is still bespoke. (See evidence.)
- Ongoing discussions about config sprawl show persistent friction. (See evidence.)

# Design goals

- **No reinvention**: orchestrate and normalize, don’t compete with established tools.
- **Stable artifacts**: diffable JSON for CI + PR review.
- **Incremental adoption**: start with advisories + deny, add vet and vendor later.

# Non-goals

- Not a new vulnerability database or audit system.
- Not a replacement for organization-specific governance.

# Architecture & API sketch

- Crate: `workspace_policy`
  - parse bundle, run checks, normalize to `PolicyReport`
- CLI: `cargo-policy`
  - subcommands: `init`, `check`, `doctor`, `report`
- Output: `target/policy/` with last-run artifacts

# Security / safety model

- Treat tool outputs as untrusted (defensive parsing).
- Hash inputs (Cargo.lock, policies, tool versions) into report metadata.

# Maintenance & governance

- Version the policy bundle schema.
- Publish “recommended baselines” for small OSS, startups, and enterprises.

# References

See evidence links in frontmatter.
