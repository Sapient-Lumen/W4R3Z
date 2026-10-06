# ADR-0102: Packet-capture normalization must produce generic redaction evidence

Date: 2026-03-09  
Status: Accepted

## Context

`adrs/ADR-0101-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md` already fixed the intake posture for stronger packet-capture artifacts:
foreign or richer `.pcap` / `.pcapng` files stay on the typed safe-open `content.import.*` lane,
and ordinary promotion/export may target only `packet.capture.summary` or normalized `packet-records-only` derivatives.

That still leaves one practical ambiguity:
**what evidence makes a normalized packet-capture derivative trustworthy enough for ordinary promotion/export?**

If the answer is only “the import receipt says `strip-metadata` happened”, the archive drifts again:

- packet-capture normalization becomes tool folklore instead of a reusable evidence pattern,
- export/support workflows cannot prove *which* deterministic sanitization policy produced the derived artifact,
- and packet-capture capture-file cleanup quietly bypasses the existing redaction/privacy machinery already used elsewhere in the archive.

DeriveBSD already has a generic privacy/evidence lane:
`redaction-transform` and `redaction-receipt`.
The packet-capture lane should reuse that instead of inventing a parallel packet-specific proof story.

## Decision

**Packet-capture normalization is authoritative only when it is bound to the generic deterministic redaction lane.**

Specifically:

1. Keep `content.import.plan` / `content.import.receipt` as the authoritative safe-open intake lane for stronger packet-capture artifacts.
   - We are not creating a new packet-capture import subsystem.

2. Require the normalization step to bind to generic redaction evidence.
   - The canonical packet-capture normalization policy is a constrained `redaction-transform` profile for `applies_to = ["pcap"]`.
   - The canonical proof that normalization happened is a constrained `redaction-receipt` profile.

3. Make the packet-capture import receipt point at that redaction evidence.
   - `spec/content.import.packet-capture.receipt.schema.json` must attach typed proof on the normalized output it emits.
   - The normalized-output labels must record:
     - `redaction_transform_digest`
     - `redaction_receipt_digest`
     - `promotion_verdict`
   - The normalized output digest itself remains the join key back to the generic `redaction-receipt`.

4. Keep packet-capture normalization allowlist-first.
   - The canonical packet-capture redaction profile keeps packet records and required structural framing,
   - while stripping stronger sideband metadata such as comments, name-resolution material, decryption-secret blocks, and other non-authoritative sideband metadata.

5. Keep the original artifact quarantined.
   - The redaction receipt proves the derivative,
   - not that the original risky artifact becomes ordinary evidence.

## Consequences

- Packet-capture normalization now plugs into an existing archive-wide pattern instead of becoming a packet-only exception.
- Export/support workflows can prove which deterministic sanitization policy produced the normalized derivative.
- A/B/C/D keep one official stricter path for richer packet captures without losing compatibility tooling.
- Future implementation can swap concrete packet tools as long as they still emit the same typed redaction evidence.

## What this does not decide

This ADR does **not** decide:

- the exact implementation toolchain,
- the full block-by-block pcapng parser surface,
- or whether every stronger artifact can always yield an ordinary-export-eligible normalized derivative.

It only fixes the evidence boundary for the normalization step that ADR-0101 already made necessary.
