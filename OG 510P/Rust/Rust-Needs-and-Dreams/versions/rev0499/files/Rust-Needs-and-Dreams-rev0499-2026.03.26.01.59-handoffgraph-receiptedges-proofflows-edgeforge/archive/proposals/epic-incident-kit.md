# Epic Proposal: Incident Kit (cargo incident)

## One-sentence pitch
Make Rust supply-chain incident response drillable and automatable by standardizing exposure analysis, mitigation workflows, and portable incident evidence packs.

## Deliverables
- `cargo-incident` reference implementation
- Schemas: `incident-report/v0`, `incident-pack/v0`
- Integrations:
  - RustSec advisory ingestion adapter
  - `cargo sbom` precursor ingestion
  - `cargo policy` and Trust Signals ingestion
  - Credentials Kit integration for “rotate secrets” evidence
- Scenario corpus + CI drills
- Templates:
  - incident runbook markdown
  - postmortem outline that links artifacts

## Why now
- crates.io is shifting toward RustSec advisories as the primary user notification channel for most malicious crates, making advisory-to-action tooling more important.  
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- 2026 goals emphasize supply-chain controls and SBOM generation, which are key enablers for exposure analysis and repeatable remediation.  
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html  
  https://github.com/rust-lang/cargo/issues/16565

## Non-goals
- Replacing RustSec or crates.io processes
- Publishing sensitive incident data by default
- Mandating one organization’s policy

## Milestones
1) v0: advisory ingestion + exposure scan + `incident-report/v0`
2) v0.2: mitigation helpers (pin/ban) + rebuild checklist generator
3) v0.3: `incident-pack/v0` + drill scenarios + CI templates
4) v1: stable schemas + ecosystem integrations + public regression corpus
