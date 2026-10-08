---
id: P-0164
title: Industrial OPC UA Deployment Kit — ops-grade OPC UA in Rust, with conformance and evidence bundles
status: idea
domains: [industrial, iot, opcua, networking, security, dx]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/async-opcua
  - https://crates.io/crates/open62541
  - https://crates.io/crates/opcua
---

# Problem
OPC UA is common in industrial control, but deploying it “correctly” is hard: certificate profiles, endpoints, node modeling, subscriptions, reconnection, and interop quirks vary by vendor. Rust has building blocks, but there’s no **ops-grade, batteries-included** kit that makes a Rust OPC UA client/server easy to ship and easy to debug.

# What this crate should provide (to other people)
A **single, opinionated deployment surface**:

- A `opcua-kit` facade that can run as:
  - `opcua-kit::server::run(config)` — secure server with modeled nodes + metrics + health
  - `opcua-kit::client::connect(config)` — resilient client w/ subscription helpers
- A stable, shareable evidence bundle: `opcua-bundle.zip`
  - connection transcript (redacted), endpoint/crypto summary, server discovery results
  - captured NodeSet2 / namespace metadata (if allowed)
  - standardized failure classification (`report.json`)
- `cargo opcua doctor` to diagnose:
  - cert chain / EKU mismatches
  - endpoint security policy mismatch
  - clock skew issues
  - subscription liveliness & reconnection loops

# Prior art (and why it’s insufficient)
- `async-opcua` and related crates give a solid async foundation, but don’t standardize deployment defaults, interop testing, or “bug bundle” capture for maintainers. citeturn0search4turn0search12turn0search16
- `open62541` bindings exist, but using bindings does not solve “golden path” ops ergonomics. citeturn0search20
- `opcua` exists, but the ecosystem lacks a unified conformance/evidence workflow. citeturn0search0turn0search8

# Design goals
- **Secure by default**: sane TLS/cert defaults and explicit “unsafe interop” switches.
- **Interop-first**: a small suite of cross-vendor scenarios (browse, read/write, subscriptions).
- **Evidence-first**: reproducible artifacts so upstream issues can be filed with minimal back-and-forth.
- **No-regret adoption**: usable as a library *or* as a sidecar “OPC UA bridge” binary.

# Architecture & API sketch
- `opcua-kit-core`: config schema + redaction + transcript/event model
- `opcua-kit-server`: node model helpers, endpoint profiles, metrics/health
- `opcua-kit-client`: resilient session/subscription manager
- `opcua-kit-cli`: `cargo opcua doctor`, bundle capture, replay

Example:
```rust
let cfg = opcua_kit::Config::from_env()?;
opcua_kit::server::run(cfg).await?;
```

# Artifact format (opcua-bundle.zip)
- `report.json` (stable schema): handshake, endpoint choice, policy set, errors (typed)
- `session.jsonl`: structured events (connect, browse, read, write, subscribe)
- `redaction.toml`: what was removed and why
- optional `nodeset2.xml` or namespace summaries (policy-gated)

# Conformance plan
- Scenario corpus: **discovery**, **browse**, **read/write**, **subscriptions**, **reconnect**
- A “compat matrix runner” that can target:
  - local demo servers (where possible)
  - lab appliances via `targets.toml` (non-public)
- CI mode that replays recorded sessions to ensure deterministic parsing + classification.

# Security / safety model
- Treat all server metadata as untrusted; strict parsing with size limits.
- Redaction is on by default for bundles (credentials, URIs, identifiers).
- Explicit allowlist to include node metadata.

# Milestones
- 0.1: client connect + browse/read + `opcua-bundle.zip` capture
- 0.2: subscriptions + reconnect semantics + doctor checks
- 0.3: server runner + minimal node modeling helpers
- 0.4: conformance suite + matrix runner
