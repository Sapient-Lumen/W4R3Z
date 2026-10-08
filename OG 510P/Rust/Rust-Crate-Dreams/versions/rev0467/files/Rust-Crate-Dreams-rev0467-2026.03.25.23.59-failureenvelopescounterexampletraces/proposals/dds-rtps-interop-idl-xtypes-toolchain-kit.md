---
id: P-0214
title: DDS/RTPS Interop + IDL/XTypes Toolchain Kit
status: idea
domains: [robotics, realtime, middleware, protocols, conformance, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://www.omg.org/spec/DDSI-RTPS/2.1/PDF
  - https://www.omg.org/spec/DDSI-RTPS/2.2/About-DDSI-RTPS
  - https://github.com/sjames/cyclonedds-rs
  - https://github.com/eclipse-cyclonedds/cyclonedds/issues/2183
---

# Problem

Rust robotics/realtime teams often want DDS, but the ecosystem is fragmented:

- bindings exist for major implementations, yet **interop + reproducible failure capture** is scarce,
- IDL/codegen and XTypes compatibility is still a recurring, vendor-specific pain,
- teams need a “known-good” **wire-level harness** to diagnose discovery/QoS mismatches.

The result: duplicated integration work and brittle deployments.

# What it provides

A workspace that pairs an IDL/XTypes toolchain with a conformance/interop runner.

- `dds-lab` CLI
  - compile a small IDL/XTypes subset to a stable Rust IR (codegen optional)
  - run discovery + pub/sub suites across backends (CycloneDDS first; adapters for others)
  - emit `*.rtpsbundle.zip` evidence (pcap summary + normalized RTPS message traces)

- Libraries
  - `dds-idl-ir` — parse a pragmatic IDL subset → stable IR (no vendor lock-in)
  - `dds-xtypes` — type hash/assignability helpers for common XTypes profiles
  - `rtps-trace` — decode/normalize key RTPS submessages used in suites
  - `dds-runner` — adapter traits for different DDS runtimes (CycloneDDS bindings as MVP)

# Bundle format

`rtpsbundle.zip`:
- `manifest.json` (suite id, backend versions, network mode)
- `trace.jsonl` (normalized discovery + RTPS events)
- `types.json` (IDL IR + type hashes)
- `captures/` (optional): pcapng, logs, config snapshots
- `verdict.json` (assertions + failure explanations)

# Scorecard (initial)

- Impact: 4
- Neglectedness: 4
- Feasibility: 2
- Adoptability: 3
- Sustainability: 2
- Differentiation: 4

# Minimum lovable MVP (4–8 weeks)

1. CycloneDDS adapter (via `cyclonedds-rs` style bindings) + simple pub/sub suite.
2. RTPS trace normalization for the subset exercised (discovery + heartbeat/acknack where needed).
3. `rtpsbundle.zip` emission + a minimal pcap-based replay/diff tool.

# De-risk plan

- Start with a tiny, explicit suite (single domain/participant, reliable + best-effort).
- Treat IDL as **IR-first**: codegen is optional; focus on type hashing + mismatch detection.

# Non-goals

- Replacing vendor DDS implementations.
- Implementing the full DDS spec in Rust for MVP.
