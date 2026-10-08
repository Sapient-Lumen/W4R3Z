---
id: P-0266
title: RDP Interop & Evidence Kit — canonical RDP traces + capability matrices + replay bundles
status: idea
domains: [networking, remote-desktop, windows, interoperability, testing, security]
last_reviewed: 2026-03-05
evidence:
  - https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-rdpbcgr/5073f4ed-1e93-45e1-b039-6e30c385867c
  - https://winprotocoldoc.z19.web.core.windows.net/MS-RDPBCGR/%5BMS-RDPBCGR%5D-220903.pdf
  - https://github.com/Devolutions/IronRDP
  - https://crates.io/crates/rdp-rs
  - https://crates.io/crates/freerdp2
---

## What it should provide others

A **diagnostic and conformance toolkit** for RDP implementations (clients, servers, gateways) that turns RDP failures into **portable, privacy-safe evidence bundles** (`*.rdpbundle.zip`) and produces **capability matrices**.

The crate should give users:

- **Canonical trace IR** of the RDP connection lifecycle (negotiation, security, capabilities, graphics orders at a coarse level).
- **Redaction-first** capture (strip bitmaps, clipboard, credentials, file contents).
- **Feature/capability negotiation diffs**: make it obvious *where* two implementations diverge.
- **Replay harness** for narrow slices (e.g., handshake/capabilities) to regression-test parsers and state machines.

## Why it is missing / worth building

Rust has active RDP work (e.g., IronRDP) and older pure-Rust efforts, plus bindings to mature C stacks. What’s missing is the “lab layer”: a standardized way to capture and compare sessions across implementations without shipping sensitive data.

This would also de-risk long-term maintenance by keeping protocol understanding encoded as fixtures and canonicalization rules.

## Non-goals

- Not a full RDP client/server.
- Not a full pixel-perfect graphics replay engine.

## Proposed design

### Workspace layout

- `rdp-evidence-core`: canonical IR + schemas + bundle I/O
- `rdp-capture`: adapters
  - IronRDP adapter
  - rdp-rs adapter
  - optional FreeRDP binding adapter (if feasible)
- `rdp-compare`: capability diff + “explain divergence” reports
- `rdp-fixtures`: curated handshake/capability fixtures

### Bundle format (`rdpbundle.zip`)

- `manifest.json`
- `trace.ir.jsonl` (canonicalized events)
- `capabilities.json` (normalized)
- `redaction.toml`
- `attachments/` (optional: log excerpts, error stacks)

## MVP (4–8 weeks)

1. Canonicalize and diff: negotiation + security selection + capability exchange
2. Bundle writer/reader + redaction defaults
3. Adapter for one Rust stack (IronRDP first)
4. Generate a “capability matrix” report across targets

## Maintenance plan

- Keep a small set of evergreen fixtures for negotiation/security/capabilities.
- Add graphics-order coverage only when needed for a specific bug class.
