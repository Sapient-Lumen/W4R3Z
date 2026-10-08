---
id: P-0054
title: ipc-kit — safe cross-platform IPC primitives with bounded framing and transport plugins
status: idea
domains: [ipc, runtime, security, systems]
last_reviewed: 2026-03-01
evidence:
  - https://github.com/servo/ipc-channel
  - https://docs.rs/shmem-ipc
  - https://docs.rs/shared_memory
---

# Problem
Rust has IPC crates, but they’re either:
- tied to specific patterns (channels), or
- OS-specific (high-perf Linux shared memory),
and many projects still reinvent **protocol negotiation, bounded framing, backpressure, and fuzzable decode**.

# Users & user stories
- Desktop app: “Split UI and worker processes; need a safe, versioned protocol.”
- Sandbox broker: “Run untrusted code; need strict message bounds and a narrow IPC surface.”
- Local agent: “Need cross-platform IPC with good ergonomics.”

# Prior art (and why it’s insufficient)
- ipc-channel provides a channel-like abstraction but isn’t a full “IPC kit” (negotiation, bounds, transport plugins).
- shmem-ipc is excellent but Linux-only by design.
- shared_memory provides wrappers but leaves synchronization and protocol safety to users.

# Design goals
- A safe IPC substrate with:
  - transport plugins (UDS / named pipes / TCP localhost opt-in / shared memory fast path)
  - handshake + version negotiation
  - bounded framing + backpressure
  - fuzz harness + conformance fixtures

# Non-goals
- Building a full RPC framework (gRPC replacement).
- Mandating a serialization format.

# Architecture & API sketch
- `ipc-kit-core`:
  - `Endpoint::connect/accept()`
  - `Handshake { protocol_id, version_range, limits }`
  - `FramedStream` with max frame size and streaming decode
- Optional modules:
  - `ipc-kit-postcard` / `ipc-kit-json` codecs
  - `ipc-kit-shmem` transport adapter (Linux) inspired by shmem-ipc patterns
- Test tooling:
  - `ipc-kit conformance` runs handshake/framing fixtures across transports.

# Security / safety model
- Peer is untrusted: strict bounds, no panics on malformed input, denial-of-service mitigations.
- Avoid implicit network; bind to localhost / UDS by default.

# Maintenance & governance plan
- Keep core tiny; transports/codecs are optional crates.
- Fuzzing as part of CI.

# Milestones
- 0.1: UDS/named-pipe transport + handshake + bounded framing.
- 0.2: shared memory fast path (Linux) + conformance suite.
- 0.3: capability annotations for sandbox brokers.

# Open questions
- Best cross-platform story for named pipes vs UDS fallback on Windows.
- Whether to standardize a “control plane” for reconnect/rekey.

# Sources
See front matter links.
