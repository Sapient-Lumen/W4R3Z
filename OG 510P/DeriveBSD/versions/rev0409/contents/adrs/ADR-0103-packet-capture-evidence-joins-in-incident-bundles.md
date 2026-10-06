# ADR-0103: Incident bundles must carry packet-capture evidence by typed digest joins, not raw blob creep

Date: 2026-03-09  
Status: Accepted

## Context

`adrs/ADR-0097-packet-capture-session-and-summary-first-export-boundary.md` already fixed packet capture as a bounded session with summary-first export posture.
`adrs/ADR-0101-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md` and `adrs/ADR-0102-packet-capture-normalization-redaction-receipt-boundary.md` then fixed the stronger import and normalization lanes.

That still leaves one practical wiring gap:
**the official support/incident bundle schema does not yet say how packet-capture evidence joins the bundle contract.**

If the answer is only “mention packet capture in prose”, the archive drifts again:

- bundle builders either omit packet-capture evidence entirely or stash it in `extra`,
- stronger imported captures silently push original or normalized `.pcapng` bytes into the default payload,
- support workflows lose the typed joins back to the session/import/redaction evidence that explain those bytes,
- and the packet-capture lane becomes a special-case blob workflow instead of a first-class part of the existing bundle contract.

DeriveBSD already has a bundle contract:
`incident.bundle` + `bundle.plan` + `bundle.payload.manifest` + `bundle.build.receipt`.
The packet-capture lane should join that contract through typed digest references rather than by teaching bundles to smuggle raw packet files by default.

## Decision

**Incident/support bundles carry packet-capture evidence through typed digest joins, while raw packet bytes remain non-default payload members.**

Specifically:

1. Extend the canonical bundle include-knob surface with packet-capture joins.
   - `spec/incident.bundle.schema.json#/$defs/include_knobs` must carry:
     - `packet_capture_sessions`
     - `packet_capture_summaries`
     - `packet_capture_import_receipts`
     - `packet_capture_redaction_receipts`
   - `spec/bundle.plan.schema.json` already reuses that include-knob shape, so the bundle-selection lane inherits the same contract automatically.

2. Make the included packet-capture evidence explicit in `incident.bundle.includes`.
   - The canonical bundle metadata surface must carry:
     - `packet_capture_session_digests`
     - `packet_capture_summary_digests`
     - `packet_capture_import_receipt_digests`
     - `packet_capture_redaction_receipt_digests`

3. Keep packet capture summary-first inside bundles.
   - The ordinary packet-capture members of a support bundle are the session digest, summary digest, and when relevant the safe-open import + normalization proof digests.
   - Raw packet bytes do **not** become ordinary bundle members merely because a normalized derivative exists.

4. Keep stronger artifacts joined by proof, not by payload default.
   - If a stronger imported packet artifact participates in support handoff, the official bundle path carries the `content.import.packet-capture.receipt` digest and the matching packet-capture `redaction.receipt` digest.
   - The original strong artifact remains quarantined evidence.
   - Any raw-byte derivative that actually leaves the system still needs its own export-policy / export-receipt path as a stronger action.

5. Do not invent a packet-capture-specific bundle subsystem.
   - This is a narrow extension of the existing bundle-plan / incident-bundle contract, not a second bundle format or a packet-only collector.

## Consequences

- Packet-capture evidence is now mechanically selectable in `bundle.plan` instead of living in prose or `extra`.
- Support bundles can explain packet-capture participation without defaulting to packet blobs.
- Stronger imported captures now have one official join into support bundles: session/summary/import/redaction evidence digests.
- A/B/C/D keep one coherent support-bundle story without forking around packet troubleshooting.

## What this does not decide

This ADR does **not** decide:

- the transport used if a raw packet derivative is separately exported,
- the exact packet-analysis tooling behind the session/summary/import/redaction evidence,
- or whether every incident bundle should include packet-capture evidence by default.

It only fixes the missing typed join between the already-decided packet-capture lane and the already-decided incident/support bundle contract.
