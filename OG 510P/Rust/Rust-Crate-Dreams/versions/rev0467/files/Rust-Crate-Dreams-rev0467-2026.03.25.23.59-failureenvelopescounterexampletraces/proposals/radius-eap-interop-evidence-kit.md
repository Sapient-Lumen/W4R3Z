---
id: P-0287
title: RADIUS + EAP Interop & Evidence Kit — canonical exchange bundles + attribute registries + replay/diff
status: idea
domains: [netops, security, enterprise, protocols, testing]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/html/rfc2865
  - https://www.iana.org/assignments/radius-types/radius-types.xhtml
---

## What it should provide others

A practical toolkit for debugging and validating **RADIUS interoperability** across NAS devices, proxies, and AAA servers.

Core needs this crate should satisfy:

- **Canonical RADIUS exchange transcripts** (Access-Request/Accept/Reject/Challenge) with structured parsing of attributes and safe redaction of secrets.
- **Registry-pinned attribute decoding** (packet and attribute type codes evolve; ship snapshots and diffs).
- **Replay + semantic diff**: compare behavior across environments (e.g., “why is server X sending Access-Challenge here?”).

This is anchored to the RADIUS protocol definition citeturn0search1 and the IANA RADIUS Types registry. citeturn0search17

## Non-goals

- Not a full AAA server implementation.
- Not a Wi-Fi supplicant; focus is **protocol evidence** and interop testing surfaces.

## Core crate/workspace shape

- `radius-evidence` — bundle schema + redaction + canonicalization + semantic diff
- `radius-decode` — registry-pinned decoder/encoder (with snapshot workflow)
- `radius-scenarios` — scenario DSL (PAP/CHAP, EAP pass-through, challenge flows)
- `radius-replay` — replay engine for deterministic reproduction
- `radius-adapters/*` — integrate with existing Rust RADIUS clients/servers where practical

## Evidence bundle (draft)

`*.radiusbundle.zip`:
- `bundle.toml`
- `exchanges.jsonl` (canon events)
- `registry_snapshot/` (type + attribute tables used for decode)
- `diff_report.md` (optional)
- `redaction.toml`

## MVP (4–8 weeks)

1. Canonical transcript + redaction
2. Registry snapshot pipeline + decoder
3. Replay + diff for core auth flows (Access-Request/Accept/Reject/Challenge)

## De-risk plan

- Start with **UDP** and single-server flows.
- Add proxy-chain modeling later (Agent/Server, Proxy-State).
