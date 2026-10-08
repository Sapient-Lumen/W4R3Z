---
id: P-0196
title: Chunked OHTTP & Privacy Gateway Ops Kit — streaming, rate limits, and intermediation “doctor” tooling
status: idea
domains: [networking, privacy, http, security, operations]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/wg/ohai/
  - https://datatracker.ietf.org/doc/rfc9292/
  - https://crates.io/crates/ohttp-gateway
  - https://github.com/payjoin/ohttp-relay
  - https://divviup.org/blog/ohttp-now-available/
needs:
  - Production-grade patterns for operating privacy gateways (OHTTP) under real constraints (streaming bodies, abuse protection, observability).
  - A standard “privacy gateway incident bundle” to debug failures without leaking user content.
risks:
  - Streaming/partial-body semantics are easy to get wrong; conformance must be strong and conservative.
  - Gateways sit on the boundary of privacy and abuse; unclear defaults could harm users or operators.
---

# Problem

Many real deployments want privacy-preserving HTTP forwarding, but not all traffic is small, single-shot requests. Gateways need:

- streaming / chunked request and response bodies
- strict rate limiting and abuse controls
- observability without violating privacy invariants
- intermediation patterns (relay + gateway + target) that are testable

The IETF OHAI work is actively discussing extensions like chunked OHTTP. Meanwhile, Rust has gateway/relay code emerging, but lacks an ops-focused “kit” that bakes in safety checks and reproducible troubleshooting.

# Users & user stories

- **Gateway operators**: “I need to enforce abuse controls and still preserve unlinkability.”
- **Protocol implementers**: “I need conformance tests for streaming semantics and error handling.”
- **Privacy reviewers**: “I want ‘privacy invariants’ automatically checked in CI.”

# Prior art (and why it’s insufficient)

- OHAI group materials focus on protocol spec evolution, not operator tooling.
- `ohttp-gateway` and existing relay repos are helpful but not standardized, and often lack reusable incident artifacts and conformance suites.
- Deployments like Divvi Up show practical gateway use, but not reusable tooling.

# Design goals / non-goals

**Goals**
- Provide a reference “ops layer” around gateway/relay components:
  - streaming/chunking adapters
  - rate limiting / abuse mitigation hooks
  - privacy-preserving observability
- Ship deterministic incident bundles and a replay harness.
- Provide conservative default configurations with explicit “unsafe” opt-ins.

**Non-goals**
- Replace any specific reverse proxy or L7 edge; integrate via adapters.
- Solve anonymity beyond the OHTTP model.

# Architecture & API sketch

Workspace crates:

- `privacy-gateway-core`: common types, policies, privacy invariants, error taxonomy.
- `privacy-gateway-stream`: chunking/streaming adapter layer for bhttp/OHTTP message bodies.
- `privacy-gateway-ops`: rate limit interface + metrics/logging redaction helpers.
- `privacy-gateway-bundle`: artifact format.
- `cargo privacy-gateway`: CLI
  - `doctor` (policy checks, config lint, privacy invariant checks)
  - `capture` (produce `*.pgbundle.zip`)
  - `replay` (reproduce verdicts offline)

# Bundle format: `*.pgbundle.zip`

Top-level:
- `report.json` (schema_version, scenario, verdicts, invariant checks)
- `trace/` (timing + structured events, no raw payload)
- `wire/` (post-redaction bhttp chunks, size/timing metadata)
- `policy/` (rate limits, redaction config, allowlists)

# Security / safety model

- Explicit “no cleartext payload logging” invariant; `doctor` fails builds if violated.
- Ensure chunk ordering/length invariants; replay harness catches nondeterminism.
- Fuzz the streaming parser and chunk reassembly.

# Maintenance & governance plan

- Follow OHAI WG changes; maintain “profiles” for RFC vs draft semantics.
- Keep bundle schemas permissive early; stabilize after interop feedback.

# Milestones (0.1 / 0.2 / 1.0)

**0.1**
- doctor + bundle format + replay harness for non-streaming
- ops policy layer (rate limit interface, redaction helpers)

**0.2**
- streaming/chunking adapters + conformance suites for chunk ordering, truncation, errors

**1.0**
- stable `pgbundle` schema + published interop corpora + recommended deployment profiles

# Open questions

- How to represent streaming semantics in a reproducible artifact without storing content?
- Should “abuse signals” be modeled as a standard event taxonomy?

# Sources

- https://datatracker.ietf.org/wg/ohai/
- https://datatracker.ietf.org/doc/rfc9292/
- https://crates.io/crates/ohttp-gateway
- https://github.com/payjoin/ohttp-relay
- https://divviup.org/blog/ohttp-now-available/
