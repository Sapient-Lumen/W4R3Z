---
id: P-0191
title: Terraform Provider Rust SDK Kit
status: idea
domains: [iac, infra, tooling, interop, devtools]
last_reviewed: 2026-03-05
evidence:
  - https://developer.hashicorp.com/terraform/plugin/terraform-plugin-protocol
  - https://github.com/hashicorp/terraform/blob/main/docs/plugin-protocol/README.md
  - https://developer.hashicorp.com/terraform/plugin/framework
  - https://developer.hashicorp.com/terraform/plugin/how-terraform-works
---

# P-0191 — Terraform Provider Rust SDK Kit

## Problem / why now

Terraform providers are executable plugins that talk to Terraform Core over a **versioned plugin protocol** (gRPC-based since Terraform 0.12). Most providers are written in Go, because the official SDKs are Go-centric and the ecosystem assumes Go tooling. citeturn0search0turn0search4turn0search20

**What’s missing in Rust is not “a gRPC client”:** it’s a cohesive *provider authoring experience* that covers schema modeling, state handling, diagnostics, acceptance tests, release packaging, and protocol-version compatibility tracking.

## What this crate/tooling should provide other people

A “golden path” to build and ship Terraform providers in Rust:

1. **Protocol adapters (core)**  
   - Rust bindings and helpers for Terraform plugin protocol versions (start with v6/v5 compatibility surface).  
   - Version negotiation and capability declaration helpers aligned with registry compatibility metadata expectations. citeturn0search0turn0search20

2. **Schema & type system layer (ergonomics)**  
   - Derive macros to declare provider/resource/data-source schemas with:
     - rich validation
     - computed/optional/required semantics
     - plan modifiers (“force new”, etc.)  
   - A stable “diff explanation” surface to emit high-quality diagnostics.

3. **State & drift model (correctness)**  
   - A typed “resource instance state” API:
     - `plan -> apply -> read -> diff` as explicit phases
     - stable serialization that avoids “surprise null vs unknown vs absent” footguns

4. **Acceptance-test harness & fixtures (operational)**  
   - Local test runner that can run **Terraform acceptance tests** and store reproducible artifacts:
     - Terraform CLI version
     - provider binary hash
     - protocol version
     - request/response traces (redacted)
     - logs  
   - Output as `*.tfbundle.zip`.

5. **Codegen hooks (optional, but huge)**  
   - Bridges: from OpenAPI/JSON Schema to resource scaffolding
   - Import existing provider schemas and generate Rust stubs.

## Artifact-first design: `tfbundle.zip`

A `tfbundle.zip` is a redacted, shareable bug report for a failing acceptance test:

- `manifest.json` (versions, OS/arch, terraform version, provider git SHA)
- `trace/` (normalized protocol traces with sensitive fields redacted)
- `logs/`
- `state/` (sanitized state snapshots and diffs)
- `repro.sh` (best-effort repro script)

## MVP → v1 plan

### MVP (4–8 weeks of focused implementation)
- Minimal protocol bindings + runner that can act as a provider plugin.
- Basic schema declarations + resource lifecycle scaffolding.
- `cargo terraform-provider test` producing `tfbundle.zip`.

### v1 (production viability)
- Compatibility matrices (Terraform versions, protocol versions).
- Diagnostics, drift/deletion edge cases.
- Conformance suite: “golden traces” per protocol version.
- Release tooling: signing, checksums, publish automation.

## Testing, conformance, and guardrails

- **Interop tests**: run a “known-good” reference provider in Go and compare observable behavior.
- **Fuzz redaction**: ensure traces cannot leak secrets.
- **Determinism**: normalize timestamps and nondeterministic IDs in traces to make diffs meaningful.

## Prior art / evidence

- Terraform Plugin Protocol overview and versioning. citeturn0search0turn0search20
- Terraform’s own protocol `.proto` definitions and gRPC note. citeturn0search4
- Official SDK framing (Go-first plugin framework). citeturn0search12
