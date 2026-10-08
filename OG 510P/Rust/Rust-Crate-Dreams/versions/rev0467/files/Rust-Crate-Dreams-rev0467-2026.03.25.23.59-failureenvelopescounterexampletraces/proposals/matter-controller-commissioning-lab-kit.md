---
id: P-0208
title: Matter Controller + Commissioning Lab Kit — reproducible commissioning/control scenarios and portable matter bundles
status: idea
domains: [iot, smart-home, matter, interoperability, testing]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/project-chip/connectedhomeip
  - https://project-chip.github.io/connectedhomeip-doc/development_controllers/chip-tool/chip_tool_guide.html
  - https://crates.io/crates/rs-matter
  - https://github.com/project-chip/rs-matter
---
# P-0208: Matter Controller + Commissioning Lab Kit

**One-liner:** A reproducible, redaction-friendly **commissioning + control lab** for Matter devices in Rust—turning device onboarding and interaction into **portable `*.matterbundle.zip` test cases**.

## Why this is missing (the gap)
The Matter ecosystem has:
- an official reference stack/tooling in `connectedhomeip` (incl. **CHIP Tool** controller) and docs for controller workflows
- a serious pure-Rust embedded-focused implementation (**rs-matter**)

But Rust teams building hubs/controllers still lack a unified crate that:
- models commissioning flows as **testable scenarios**
- captures traffic/attestation/cluster interactions into reproducible artifacts
- provides “explain why commissioning failed” diagnostics across transports and fabrics

## Target users
- Smart-home hub vendors building Rust services
- Device makers writing test rigs (manufacturing QA)
- Integrators validating device firmware across updates
- CI farms running conformance-like suites

## Core idea: scenario DSL + bundles
Introduce:
- `matter_scenario`: a small DSL for commissioning/control steps (discover, open-commissioning-window, pair, read/write clusters, subscribe, etc.)
- `*.matterbundle.zip`: capture inputs + deterministic transcripts + redacted crypto material

Bundle contents (redactable):
- setup payload / onboarding inputs (QR/manual) (optionally hashed)
- transcripts of interactions (message summaries + timing)
- commissioner configuration (fabric, CASE config, transport info)
- verdicts + error taxonomy + “likely fix” hints
- optional packet capture references (not mandatory)

## Crate shape (workspace)
- `matter_bundle` — bundle IO, normalization, redaction presets
- `matter_scenario` — scenario DSL + runner traits
- `matter_controller` — async controller façade (Tokio) with transport plugins
- `matter_diag` — failure classifiers (commissioning stages), “explain” output
- `matter_fixtures` — golden bundles, vendor-neutral minimal device sims
- `cli` — `matterlab` for running scenarios, collecting bundles, producing reports

## MVP (4–8 weeks)
1. Define bundle v0.1 and scenario DSL v0.1
2. Implement controller runner using `rs-matter` for a minimal subset:
   - discovery
   - commissioning to fabric (happy path)
   - read a small set of clusters
3. Produce deterministic transcripts + diff tool for two runs
4. Redaction presets (no private keys; keep public attestation summaries)

## De-risk plan
- Start with *controller-only* focus (no device stack)
- Use a small device matrix (e.g., 2–3 popular dev boards) and store bundles as regression tests
- Keep transport abstractions so future backends can wrap `chip-tool`/connectedhomeip as a comparison oracle

## Scorecard (0–5)
- Impact: 4
- Neglectedness: 3
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 5

## References
- Matter reference implementation repository: project-chip/connectedhomeip (github.com/project-chip/connectedhomeip)
- CHIP Tool guide: “Working with the CHIP Tool” (project-chip.github.io/connectedhomeip-doc/…/chip_tool_guide.html)
- rs-matter: pure-Rust, async-first Matter implementation (github.com/project-chip/rs-matter; crates.io/crates/rs-matter)
