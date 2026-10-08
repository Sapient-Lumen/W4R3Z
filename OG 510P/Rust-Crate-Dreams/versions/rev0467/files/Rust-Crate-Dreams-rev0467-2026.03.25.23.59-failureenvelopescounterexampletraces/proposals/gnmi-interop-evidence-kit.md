---
id: P-0273
title: gNMI (gRPC Network Management Interface) Interop & Evidence Kit (gnmibundle)
status: idea
domains: [networking, grpc, telemetry, interop, testing]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/openconfig/reference/blob/master/rpc/gnmi/gnmi-specification.md
  - https://github.com/openconfig/reference/blob/master/rpc/gnmi/README.md
  - https://datatracker.ietf.org/doc/html/draft-openconfig-rtgwg-gnmi-spec-01
  - https://github.com/openconfig/gnmi
---

## What it should provide others

A standard, Rust-first way to do **gNMI interop testing and troubleshooting** by producing portable evidence bundles:

- canonical Subscribe/Get/Set transcripts (protobuf decoded, with encoding pins)
- capability matrices (supported encodings, models, Subscribe modes)
- replay/diff harness to compare devices and collectors
- redaction presets for network inventory safety

Deliverable: `*.gnmibundle.zip` for CI and vendor/device interop.

## Why this is needed

gNMI is widely used for network device management and telemetry. Real deployments hit issues around:
- path semantics and schema model mapping
- Subscribe stream behavior (updates vs sync_response, sample/on_change nuances)
- encoding differences (JSON_IETF vs PROTO vs bytes)
- vendor quirks that are hard to reproduce without a deterministic transcript

Rust has strong protobuf/gRPC tooling; the missing piece is a **portable, agreed-upon evidence artifact**.

## Design sketch

### Workspace layout

- `gnmibundle` — schema + redaction + IO
- `gnmi-ir` — canonical model:
  - Path normalization + prefix handling
  - Notification stream events (update/delete, timestamps)
  - encoding metadata + schema pins
- `gnmicapture` — capture:
  - tonic interceptors (client side)
  - proxy capture (grpc)
- `gnmireplay` — replay Set/Get sequences; Subscribe playback to test collectors
- `gnmiverify` — conformance checks:
  - path well-formedness and prefixing rules
  - timestamp monotonicity expectations (profile-based)
  - Subscribe mode semantics per profile

### Evidence bundle: `*.gnmibundle.zip`

- `manifest.json` (target type, profile, encoding, schema refs)
- `rpc.ndjson` (canonical events)
- `models/` (YANG/module ids or references; optional hashes)
- `reports/` (diff + explain)
- `redaction.json` (hostname/IP hashing, path allowlists)

### MVP (6–10 weeks)

1. capture Get/Set and Subscribe transcript to `rpc.ndjson`
2. canonical Path + prefix normalization
3. minimal verify profiles: “baseline”, “telemetry-collector”
4. replay runner for Set/Get and Subscribe playback

## Adoption plan

- Ship a “device capability inventory” mode: probe and emit matrix
- Provide fixtures for common vendors and reference implementations (as available)
