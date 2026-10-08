---
id: P-0286
title: SNMPv3 Interop & Evidence Kit — canonical, redactable transcripts + capability matrices + replay/diff
status: idea
domains: [netops, observability, security, protocols, testing]
last_reviewed: 2026-03-05
evidence:
  - https://www.rfc-editor.org/rfc/rfc3414.html
  - https://www.rfc-editor.org/rfc/rfc3411.html
  - https://crates.io/crates/snmp-parser
---
## What it should provide others

A **portable interop and triage toolkit** for SNMPv3 that makes “works on my NMS / doesn’t work on your agent” failures *reproducible*.

Instead of shipping “another SNMP client,” this kit ships:

- A **canonical transcript format** for SNMPv3 request/response sequences (including engine discovery, time windows, auth/priv modes) with **redaction** for secrets.
- A **capability matrix runner**: probes an agent for supported security levels (noAuthNoPriv / authNoPriv / authPriv) and algorithm support, then emits a diffable report.
- **Replay and semantic diff** tooling: given two bundles (agent A vs agent B, or before vs after), pinpoint the **first divergence** in USM parameters, timeliness, or report-PDU behavior.

The kit is grounded in the SNMPv3 **User-based Security Model (USM)** definition. citeturn0search0

## Non-goals

- Not a full MIB browser UI.
- Not a replacement for existing SNMP stacks; it **wraps/adapts** them.

## Core crate/workspace shape

- `snmp-evidence` — bundle schema + redact/canonicalize + diff primitives
- `snmp-probe` — probe library + CLI for capability matrices
- `snmp-replay` — transcript replay engine (deterministic scheduling, time-window modeling)
- `snmp-adapters/*` — adapters for popular Rust SNMP crates and for pcap-derived decoders (when available)

## Evidence bundle (draft)

`*.snmpbundle.zip`:
- `bundle.toml` (metadata, versions, redaction profile)
- `transcript.jsonl` (canonical events: discovery, request, response, error, report)
- `agent_fingerprint.json` (sysDescr/sysObjectID + transport + timings)
- `matrix.json` (probed capabilities)
- `notes.md` (human context)

## MVP (4–8 weeks)

1. Canonical transcript schema + redaction
2. Capability probe runner (USM modes + basic timeliness/engineID discovery)
3. Diff tool that highlights mismatches (engineID, boots/time, auth/priv parameters, report PDUs)

## De-risk plan

- Start with **snmpv3 authNoPriv** only, add authPriv next.
- Ship with **known-fixture corpora** (synthetic transcript generator + a small open agent matrix).
