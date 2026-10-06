# ADR-0098: Packet capture summary review-surface boundary

- Status: Accepted
- Date: 2026-03-08

## Context

`adrs/ADR-0097-packet-capture-session-and-summary-first-export-boundary.md` fixed the authority side of packet capture:
DeriveBSD now has a bounded `packet.capture.session` object and a summary-first export posture.

That still left one practical gap:
**what is the canonical summary object for packet capture itself?**

If the answer is "reuse `net-flow-summary`" or "whatever the capture tool printed," two boundaries blur again:

- the bounded network-learning lane (`net-flow-summary` → `policy-suggestion` → `net-egress-policy`) gets overloaded with general incident-capture review,
- packet-capture support/export posture drifts back toward tool-specific output,
- and raw packet blobs regain power because there is no single compact review object to hand around instead.

DeriveBSD needs one narrower answer:
**summary-first packet capture should have its own typed evidence object.**

## Decision

1. Introduce `packet.capture.summary` as the canonical evidence-only review/export surface for bounded packet capture.
   It summarizes:
   - which `packet.capture.session` it came from,
   - the bounded observation window,
   - compact protocol/conversation totals,
   - local raw-artifact references by digest,
   - and whether raw packet payload export stayed forbidden / summary-only / exception-approved.

2. Keep `packet.capture.summary` distinct from `net-flow-summary`:
   - `net-flow-summary` remains the learn/audit convergence artifact for reviewing candidate `net-egress-policy` changes,
   - `packet.capture.summary` remains the incident/support/export review artifact for bounded packet capture,
   - and neither object silently replaces the other.

3. Keep `packet.capture.summary` evidence-only:
   - it does not grant authority,
   - it does not authorize packet export,
   - it does not replace the authoritative `packet.capture.session`,
   - and it does not become a hidden policy patch object.

4. Make `packet.capture.summary` the default `summary_kind` named by `packet.capture.session`.
   If packet capture also informs learn/audit review, that remains an explicit secondary relationship rather than the default meaning of packet-capture summary.

## Consequences

- Packet capture gets one stable summary artifact that support workflows, incident bundles, and export policy can point at.
- The learn/audit lane keeps `net-flow-summary` for policy convergence instead of absorbing general packet-capture review by accident.
- Summary-first export now has a concrete typed object, which makes the packet-capture lane more implementable and more testable.
- A small guardrail can keep session docs, summary docs, export docs, and the new schema/example aligned.

## Why this is narrow enough

This ADR does **not** standardize:

- the full packet-analysis pipeline,
- the exact packet-file encoding,
- every possible aggregation heuristic,
- protocol-specific decoders,
- or the CLI / daemon UX for producing summaries.

It only fixes the default packet-capture review surface so the already-accepted session/export boundary has a concrete target.
