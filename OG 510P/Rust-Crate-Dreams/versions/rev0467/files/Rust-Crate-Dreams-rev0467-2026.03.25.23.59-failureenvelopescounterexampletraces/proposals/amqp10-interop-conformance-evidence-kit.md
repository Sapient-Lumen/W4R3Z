---
id: P-0261
title: AMQP 1.0 Interop & Conformance Evidence Kit
status: idea
domains: [messaging, enterprise, interop, conformance, evidence-bundles]
last_reviewed: 2026-03-05
evidence:
  - https://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-overview-v1.0-os.html
  - https://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-complete-v1.0-os.pdf
  - https://www.rabbitmq.com/docs/amqp
  - https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-amqp-overview
---

# Problem

AMQP 1.0 is a mature, standardized wire protocol used across enterprise messaging systems. Rust has clients and some integrations, but it lacks:

- a **conformance/interop harness** that tests behavior across brokers and client implementations
- a canonical way to share failures (link credit semantics, settlement, flow control, idle timeouts, SASL/auth) as portable artifacts
- a “diffable transcript” format that lets teams compare behavior across versions/vendors

# What it provides

A Rust workspace that delivers:

- **`amqp-ir`**: canonical model of AMQP performatives/frames, links, sessions, and delivery state.
- **`amqp-capture`**: capture adapters:
  - in-process instrumentation for Rust AMQP clients
  - TCP capture → protocol decode (optional, with redaction)
- **`amqp-matrix`**: runner that executes scenario packs across a matrix (client × broker × auth mode).
- **`amqp-explain`**: divergence explanations (settlement mismatch, credit exhaustion, attach properties mismatch, timeout mismatch).
- **`amqpbundle`** (`*.amqpbundle.zip`): signed, redactable evidence bundles (Evidence Bundle Core) containing:
  - canonical transcripts
  - broker/client version fingerprints
  - scenario definition + parameters
  - normalized divergences + repro recipe

# Users & user stories

- **Enterprise platform teams**: “Prove our Rust client behaves correctly against Service Bus and RabbitMQ AMQP 1.0.”
- **Broker vendors / integrators**: “Run the same scenario pack and share bundles for failures.”
- **Library authors**: “Add a scenario fixture to prevent regressions.”

# Prior art (and why it’s insufficient)

- Specs exist, but most interop happens via ad-hoc integration tests.
- Vendor docs describe AMQP usage, but do not provide portable evidence artifacts.

# Design goals

- **Scenario packs** that encode real workloads (RPC, pub/sub, competing consumers, retries).
- **Portability**: bundle artifacts are stable across OSes and CI.
- **Redaction**: SASL/usernames/tokens are stripped by default.
- **Matrix-first**: support multi-broker runs as a primary workflow.

# Non-goals

- Replace a full AMQP implementation; start as harness + adapters.

# Architecture & API sketch

```rust
let matrix = amqp_matrix::Matrix::new()
  .with_broker(amqp_matrix::Broker::AzureServiceBus { namespace: "...".into() })
  .with_broker(amqp_matrix::Broker::RabbitMQ { url: "amqp://...".into() })
  .with_client(amqp_matrix::Client::Rust("my-client-bin"))
  .with_scenarios(amqp_matrix::ScenarioPack::load("scenarios/core.yaml")?);

let report = matrix.run()?;
amqpbundle::emit(report, "out/run.amqpbundle.zip")?;
```

# Security / safety model

- Token redaction profiles.
- Optional encrypted “private addendum” stored locally only.

# Maintenance & governance plan

- Maintain scenario packs as the core asset; accept broker-specific adapters.
- Establish a compatibility matrix page generated from CI bundles.

# Milestones

## MVP (4–8 weeks)
1. `amqp-ir` + bundle schema + CLI validate/diff
2. One scenario pack (connect/auth, basic send/receive, settlement modes)
3. One Rust client adapter + one broker runner (container-based)
4. Explain reports for common mismatches

## Next
- TCP capture decode adapter
- More brokers (Qpid Proton-based, ActiveMQ Artemis, etc.)
- Property-based tests for protocol corner cases

# Sources

- OASIS AMQP 1.0 overview and complete specification.
- Vendor documentation describing AMQP 1.0 usage in practice.
