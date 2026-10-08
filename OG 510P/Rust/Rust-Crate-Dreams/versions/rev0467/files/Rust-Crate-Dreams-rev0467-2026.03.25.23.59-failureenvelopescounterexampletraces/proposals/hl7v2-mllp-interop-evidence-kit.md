---
id: P-0285
title: HL7 v2 + MLLP Interop & Evidence Kit — canonical framing, ACK semantics, and PHI-safe replay bundles
status: idea
domains: [healthcare, interoperability, networking, compliance, testing, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://docs.oracle.com/cd/E19509-01/820-5508/ghadt/index.html
  - https://docs.cloud.google.com/healthcare-api/docs/concepts/hl7v2
  - https://docs.aws.amazon.com/wellarchitected/latest/healthcare-industry-lens/interoperability-architectures.html
  - https://crates.io/crates/hl7
---
## What it should provide others

A **PHI-safe evidence + replay** toolkit for HL7 v2 over MLLP that standardizes:
- message framing and segmentation canonicalization
- ACK behavior analysis (“what did we actually acknowledge?”)
- safe, shareable `*.hl7bundle.zip` artifacts for debugging and CI

The gap: teams spend weeks debugging “MLLP works, but…” issues where framing, ACK timing, retries, and partial reads differ across engines.

## Core crate shape (workspace)

- `mllp-ir` — canonical framing/events (start/end blocks, separators, timing)
- `hl7v2-normalize` — canonical segment ordering/whitespace normalization rules (configurable)
- `hl7bundle` — bundle IO + redaction/transforms (remove/replace PHI deterministically)
- `hl7-lab` — scenario runner: client/server harness with scripted message/ACK flows (including MLLP-over-TLS notes)

## Bundle format: `*.hl7bundle.zip`

- `manifest.json` — scenario id, transport (MLLP, optional TLS), redaction policy
- `frames.jsonl` — canonical framing events + timestamps
- `messages/` — normalized HL7 v2 messages (redacted) + hashes of original bytes
- `acks/` — ACK classification + semantic checks (AA/AE/AR, expected vs received)
- `replay/` — runnable scenario spec + fixture inputs

## MVP (4–8 weeks)

1. MLLP framing recorder + canonicalizer (byte-accurate framing timeline).
2. Deterministic redaction pipeline (PHI-safe) with pluggable rules.
3. Scenario runner with 6–10 common cases:
   - delayed ACK
   - duplicate send / at-least-once behavior
   - partial frame reads
   - malformed segment terminators
4. `hl7bundle diff` CLI (first divergence + framing vs payload mismatch report).

## De-risk plan

- Do **transport + evidence** first; avoid “HL7 v2 validator” scope creep.
- Treat security as an integration concern (e.g., “MLLP over TLS”) and record it in the manifest.
- Provide drop-in adapters for popular interface engines via socket capture.
