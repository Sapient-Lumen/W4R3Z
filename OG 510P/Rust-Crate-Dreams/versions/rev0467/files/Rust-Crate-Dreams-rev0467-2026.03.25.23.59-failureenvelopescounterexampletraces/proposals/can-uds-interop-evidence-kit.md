---
id: P-0288
title: CAN + ISO-TP + UDS Interop & Evidence Kit — canonical traces, timing checks, and reproducible diagnostic bundles
status: idea
domains: [automotive, embedded, protocols, testing, reliability]
last_reviewed: 2026-03-05
evidence:
  - https://www.iso.org/standard/63648.html
  - https://www.iso.org/standard/72439.html
---

## What it should provide others

A Rust-native workflow to make **vehicle/ECU diagnostics** reproducible across tools, adapters, and test benches.

This kit focuses on:

- **Canonical CAN trace IR** (frames + timing + bus parameters) aligned with the CAN data link layer standard. citeturn0search7
- **ISO-TP segmentation/reassembly evidence** and timing checks.
- **UDS session transcripts** (sessions, security access, routines, DIDs) to reproduce failures in CI and across labs, grounded in ISO 14229. citeturn0search2
- Redaction profiles for VIN/serials/keys and any proprietary identifiers.

## Non-goals

- Not a full OEM diagnostic application.
- Not a proprietary DBC/ARXML replacement (but can import/export).

## Core crate/workspace shape

- `can-evidence` — bundle schema + canonicalization + diff
- `isotp` — minimal, spec-faithful reassembly/segmentation helper (or adapter layer to existing)
- `uds-evidence` — UDS transcript IR + validators (session state machine)
- `can-adapters/*` — adapters for SocketCAN, PCAN, Kvaser logs, etc.
- `uds-scenarios` — scenario DSL for tests (e.g., enter session, read DID, run routine)

## Evidence bundle (draft)

`*.canudsbundle.zip`:
- `bundle.toml`
- `bus.json` (bitrate, FD, sample point if known)
- `frames.bin` / `frames.jsonl` (canonical frames)
- `isotp_sessions.jsonl`
- `uds_transcript.jsonl`
- `redaction.toml`
- `diff_report.md` (optional)

## MVP (4–8 weeks)

1. Canonical CAN frame IR + import/export for SocketCAN logs
2. ISO-TP reassembly evidence (capture → sessions)
3. UDS transcript capture + replay harness for a small service subset (session control + read DID)

## De-risk plan

- Start with **classic CAN (no FD)** and a single log format.
- Add DoIP later; keep bundle schema extensible.
