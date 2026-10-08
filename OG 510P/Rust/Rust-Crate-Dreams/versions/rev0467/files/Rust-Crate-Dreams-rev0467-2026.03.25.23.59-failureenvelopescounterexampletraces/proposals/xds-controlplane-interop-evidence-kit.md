---
id: P-0263
title: xDS Control-Plane Interop & Evidence Kit — ADS/delta stream capture, replay, and semantic diffs
status: idea
domains: [service-mesh, control-plane, xds, networking, interoperability, testing]
last_reviewed: 2026-03-05
evidence:
  - https://www.envoyproxy.io/docs/envoy/latest/api-docs/xds_protocol
  - https://crates.io/crates/xds-api
  - https://github.com/jpittis/rust-control-plane
---
# P-0263 — xDS Control-Plane Interop & Evidence Kit (Envoy/gRPC)

**Codename:** `xdslab`  
**Bundle:** `*.xdsbundle.zip`  
**Primary surface:** xDS delta/ADS streams, CSDS snapshots, semantic diffs

## Why this is missing
The xDS protocol is the de-facto dynamic configuration/control-plane interface for Envoy and an increasing set of clients (including gRPC “proxyless” clients). citeturn1search0turn1search12

In practice, teams debug xDS issues with ad-hoc logs and pcap captures. But xDS is a long-lived streaming protocol (ADS and delta xDS), and failures often depend on subtle ordering, nonce handling, resource naming, versioning, and ACK/NACK behavior.

Rust has early xDS crates (client + bindings) but lacks a **portable evidence artifact** and **interop matrix runner**.

## What the crate should provide
1. Capture xDS streams (gRPC and REST-JSON) and convert them into a canonical event IR.
2. Normalize + redact secrets (SDS, credentials) deterministically.
3. Replay streams against control planes and clients.
4. Compute semantic diffs for:
   - resource contents (proto Any unpacked)
   - subscription state
   - ACK/NACK sequences
   - delta resource adds/removes
5. Export `*.xdsbundle.zip` evidence bundles for CI/bug reports.

## Scope and non-goals
**In scope**
- v3 xDS transport protocol, including streaming gRPC and REST-JSON citeturn1search0turn1search8
- ADS, delta xDS, and a minimal CSDS snapshot capture/export
- resource-type support starting with LDS/RDS/CDS/EDS/SDS

**Non-goals**
- a full control plane implementation
- replacing Envoy’s proto APIs (`data-plane-api` is the source of truth) citeturn1search1

## Proposed architecture

### Crate layout
```
xdslab/
  xdslab-core/         # canonical IR, redaction, diff engine
  xdslab-proto/        # pinned/provisioned protos (data-plane-api)
  xdslab-capture/      # tonic interceptors + REST capture
  xdslab-replay/       # deterministic replayer for stream semantics
  xdslab-runner/       # topology/scenario DSL + matrix runner
  xdslab-bundle/       # bundle I/O + schema versions
  xdslab-cli/          # `cargo xdslab` + standalone
```

### Canonical IR (stream semantics)
Events:
- `OpenStream{transport, peer}`
- `DiscoveryRequest{type_url, node, resource_names, response_nonce, error_detail, delta_subscribe, delta_unsubscribe}`
- `DiscoveryResponse{type_url, version_info, nonce, resources(summary + hashes), removed_resources}`
- `Ack{nonce}` / `Nack{nonce, status}`
- `CloseStream{reason}`

### Proto strategy
- Pin `envoyproxy/data-plane-api` protos to a known commit (record in bundle manifest) citeturn1search1
- Provide a “compat decode” mode that treats unknown Any types as opaque bytes + stable hashes

## Bundle format (`*.xdsbundle.zip`)
- `manifest.json` (proto commit pin, redaction policy, capture mode, versions)
- `streams.ndjson.zst` (canonical IR)
- `resources/` (optional unpacked resource JSON, normalized)
- `csds.json` (optional)
- `diff/semantic.json` (optional)
- `fixtures/` (scenario DSL + topology)

## MVP plan (4–8 weeks)
1. tonic interceptor capture (client + server) + canonical IR
2. proto pinning + Any unpacking for common resources
3. redaction for SDS secrets
4. replay engine for a single stream + ACK/NACK verification
5. CLI: `capture`, `replay`, `diff`, `summarize`

## Existing ecosystem to integrate (not replace)
- Envoy’s xDS protocol documentation citeturn1search0
- `envoyproxy/data-plane-api` protos citeturn1search1
- Rust bindings (`xds-api`) and early client crates as adapters citeturn1search13turn1search2

