---
id: P-0212
title: OPC UA Conformance & Interop Lab Kit
status: idea
domains: [industrial, iot, protocols, conformance, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://opcfoundation.org/developer-tools/certification-test-tools/opc-ua-compliance-test-tool-uactt/
  - https://opcfoundation.org/developer-tools/certification-test-tools
  - https://crates.io/crates/open62541
  - https://docs.rs/open62541
  - https://docs.rs/crate/opcua/latest
  - https://github.com/FreeOpcUa/async-opcua
  - https://www.basyskom.de/en/opc-ua-and-rust-in-2025/
---

# Problem

Rust has **multiple OPC UA paths** (pure-Rust stacks and bindings to popular C implementations), but teams still lack a:

- practical **interop harness** (client↔server matrices across stacks),
- portable way to capture failures as shareable artifacts,
- “profile-first” test suites that map to common UA feature profiles without requiring membership-gated tooling.

As a result, orgs rebuild proprietary test rigs and rarely contribute reusable fixtures back.

# What it provides

A crate + CLI workbench that turns OPC UA behavior into **diffable evidence bundles**.

- `opcualab` CLI
  - run scenario suites against servers/clients (read/write, subscriptions, keepalive/lifetime, method calls, browsing, security policies)
  - generate compatibility matrices (JSON + HTML)
  - emit `*.opcua-bundle.zip` (redactable, replayable repro artifacts)

- Rust library
  - scenario DSL (`Suite`/`Step`/`Assertion`) + runner traits
  - adapters for:
    - `open62541` bindings (via `open62541` crate)
    - pure Rust stacks (`opcua`, `async-opcua`) where available
  - deterministic transcript normalization (timestamps, status codes, service faults, selected nodes)

# Bundle format

`opcua-bundle.zip`:
- `manifest.json` (suite id, env, UA profile target, security config)
- `trace.jsonl` (normalized events: service request/response summaries, status, timing)
- `endpoints.json` (discovered endpoints + security policies)
- `captures/` (optional): pcap summary pointers, server logs (redacted), cert chain hashes

# Scorecard (initial)

- Impact: 4
- Neglectedness: 4
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 4

# Minimum lovable MVP (4–8 weeks)

1. Scenario runner (single-process) + basic suites: browse/read/write + subscription smoke.
2. Adapters: `open62541`-based client runner + `opcua`-based server runner.
3. `opcua-bundle.zip` emission + `opcualab diff` between two runs.
4. A small public fixture pack: known-bad + known-good interop cases.

# De-risk plan

- Prototype **normalization** first: pick two stacks, run the same suite, ensure transcripts compare meaningfully.
- Build one “hard” case early (subscriptions w/ reconnect) to validate the bundle format and runner design.

# Why this is still missing

The OPC Foundation’s Compliance Test Tool exists but is not an open, crate-friendly harness, and access may be constrained to membership contexts. This proposal focuses on **open interop evidence**, adapters, and reproducible diagnostics, not replacing certification.
