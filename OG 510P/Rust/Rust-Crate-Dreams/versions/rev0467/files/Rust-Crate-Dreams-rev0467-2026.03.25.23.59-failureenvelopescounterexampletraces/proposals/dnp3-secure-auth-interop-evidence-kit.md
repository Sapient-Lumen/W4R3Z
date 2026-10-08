---
id: P-0289
title: DNP3 Secure Authentication Interop & Evidence Kit — canonical, redactable SA transcripts + capability matrices + replay/diff
status: idea
domains: [ics, scada, energy, security, protocols, testing]
last_reviewed: 2026-03-05
evidence:
  - https://www.dnp.org/Portals/0/Public%20Documents/DNP3%20Secure%20Authentication%20Talking%20Points.pdf
  - https://standards.ieee.org/wp-content/uploads/import/documents/other/iot.pdf
  - https://crates.io/crates/dnp3
---

## What it should provide others

A **portable interop and triage toolkit** for DNP3 **Secure Authentication (SA)** and common field deployments:
- Capture **application-layer SA exchanges** (challenge/response, roles, replay protection) into a canonical, diffable transcript.
- Produce **capability matrices** (master/outstation features, SA versions/modes, role models, TLS-on-IP usage where present).
- Emit shareable, privacy-safe **evidence bundles** that reproduce failures in CI or another lab.

Why this matters: DNP3 SA is explicitly framed as **end-to-end cryptographic authentication at the application layer**, distinct from transport encryption, and positioned to meet **IEC 62351** expectations (incl. RBAC), while TLS may still be used for IP networks. (DNP Users Group talking points)  
IEEE materials also identify **IEEE 1815 (DNP3)** as the relevant standard for power systems communications.  

## Proposed crate/workspace shape

- `dnp3-sa-evidence` — canonical transcript IR + redaction policy + hashing/signing hooks
- `dnp3-sa-runner` — scenario runner (master/outstation) with pluggable backends
- `dnp3-sa-adapters` — adapters over existing Rust DNP3 implementations (start with `dnp3`)
- `dnp3-sa-fixtures` — minimal corpora (success + known failure modes)
- `dnp3-sa-cli` — `capture`, `replay`, `diff`, `matrix`, `explain`

### Bundle format: `*.dnp3bundle.zip`
Minimal contents:
- `manifest.json` (versions, timestamps, toolchain hash, redaction profile id)
- `topology.json` (master/outstation roles, serial/IP, clock assumptions)
- `transcript.ndjson` (canonical events: SA messages, sequence counters, auth status)
- `capabilities.json` (feature bits, SA mode/version, role model)
- `verdict.json` (“expected/observed”, first divergence index + explanation)

## MVP (4–8 weeks)

1. **Transcript IR + redaction**: stable event schema, deterministic ordering, secrets stripped.
2. **Capture+Replay** against one Rust stack (adapter over `dnp3`) with two scenarios:
   - SA happy path
   - deliberate replay / counter mismatch
3. **Diff+Explain**: pinpoint first divergence with human-readable hints (clock skew, role mismatch, counter window).

## De-risk plan

- Keep the crate **adapter-first**: do not re-implement full DNP3; instrument existing stacks.
- Separate concerns: SA transcript/semantics vs transport capture (pcap optional, not required).
- Provide “known-bad” fixtures from synthetic generators (avoid publishing real operational captures).

## Success metrics

- A vendor can attach a single `dnp3bundle.zip` to an issue and another team can reproduce.
- Capability matrix auto-generated for a fleet; drift shows up as a diff.
