---
id: P-0267
title: Kubernetes CRI Interop & Evidence Kit — canonical CRI gRPC sessions + runtime compatibility matrices
status: idea
domains: [cloud, kubernetes, containers, grpc, interoperability, testing]
last_reviewed: 2026-03-05
evidence:
  - https://kubernetes.io/docs/concepts/containers/cri/
  - https://github.com/kubernetes/cri-api
  - https://kubernetes.io/blog/2024/05/01/cri-streaming-explained/
  - https://crates.io/crates/containerd-client
  - https://github.com/containerd/rust-extensions
---

## What it should provide others

A standardized way to **capture, replay, and diff** Kubernetes CRI interactions (including streaming subprotocols) to debug container runtime issues and validate CRI implementations.

The crate should give users:

- **Canonical CRI session IR**: gRPC calls, key fields (with secrets redacted), timing, and outcomes.
- **Replay harness** that can:
  - play a captured CRI workload against a runtime under test, or
  - simulate a runtime for kubelet-side testing.
- **Compatibility matrices** across runtimes and versions (containerd, CRI-O, etc.).
- **Evidence bundles** (`*.cribundle.zip`) suitable for CI and bug reports.

## Why it is missing / worth building

CRI is protobuf/gRPC-based and evolves over time; runtime bugs are often “works on my cluster” and hard to reproduce. A bundle that is **smaller than full cluster repro**, but **more faithful than logs**, would be high leverage for runtime authors and platform teams.

Rust has gRPC tooling and containerd client crates, but lacks a focused CRI interop/capture/replay kit.

## Non-goals

- Not a full runtime.
- Not a full kubelet reimplementation.

## Proposed design

### Workspace layout

- `cri-evidence-core`: IR + schema + redaction + bundle I/O
- `cri-capture`: tonic interceptors + protobuf field policies
- `cri-replay`:
  - replay driver (client-side) for captured sessions
  - mock runtime server (server-side) for kubelet-side tests
- `cri-matrix`: run captured suites across runtimes/versions

### Bundle format (`cribundle.zip`)

- `manifest.json` (api version pin, proto hash, tool versions)
- `session.ir.jsonl` (canonical gRPC events)
- `redaction.toml`
- `attachments/` (optional: kubelet/containerd logs excerpt)

## MVP (4–8 weeks)

1. Tonic interceptor capture for the core CRI RPCs (RunPodSandbox/CreateContainer/StartContainer/Stop/Remove)
2. Canonicalization + redaction presets (secrets, env vars, image creds)
3. Replay runner against containerd via `containerd-client` (or direct CRI endpoint)
4. Produce one compatibility matrix report from a small captured suite

## Maintenance plan

- Pin proto snapshots and generate compatibility layers.
- Keep bundles forward-compatible via schema versioning and strict canonicalization.
