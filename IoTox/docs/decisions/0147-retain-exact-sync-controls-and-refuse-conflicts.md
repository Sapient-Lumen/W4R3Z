# ADR 0147: Retain exact synchronization controls and refuse conflicts

Date: 2026-08-24

Status: accepted

## Context

Tox file offers and IoTox synchronization controls travel through independent event paths. A
delayed or duplicated HEAD/object result can therefore arrive after the related file offer is
already admitted, while a requester retry can repeat an earlier message identifier. Convergence is
safe only if exact duplicates are idempotent, same-identifier conflicts are refused, and reordered
controls cannot allocate another transfer or rewrite retained attempt truth.

The publisher also performs two kinds of effect for an object request: it returns one correlated
control result and, on first admission, creates one Tox file offer. Replaying the retained control
must never replay the file-offer effect.

## Decision

- Canonically encode every accepted synchronization request and retain its exact response under
  friend, authenticated online epoch, and message identifier before any file-offer effect.
- On an exact request replay under unchanged authority, return the byte-identical retained response,
  increment replay telemetry, and suppress any repeated file offer.
- On the same friend/epoch/message identifier with different canonical bytes, increment conflict
  telemetry, return a protocol error, emit no synchronization response, and preserve the original
  replay entry.
- Retain each subscriber HEAD/object result as canonical bytes. Exact duplicates are no-ops after
  their original transition; differing bytes for the same correlated lane fail the pull rather than
  choosing an arrival.
- When an exact duplicate HEAD result arrives after object results, reissue only requests whose lanes
  have no retained result. Once both object results are retained, the duplicate HEAD emits no new
  request.
- Keep file admission and object completion bound to the original FileIds and attempts. Reordered
  duplicate object results neither create a new receive nor change accepted, activated, or visible
  truth.
- Bind exact request/result journal counts, publisher request/offer/replay counters, conflict refusal,
  HEAD-last acceptance, and explicit activation into both guest receipts and the content-free pair
  manifest over observed direct UDP and forced TCP.

## Consequences

Control retry is idempotent without repeating bulk effects, and cross-lane reordering cannot multiply
transfers or make a later duplicate authoritative. A conflicting reuse of a message identifier is
visible and fail-closed while the original valid synchronization remains able to finish.

This does not provide durable replay retention across publisher process restart, automatic request
retransmission, arbitrary packet permutation/fuzz coverage, multi-source reconciliation, or a
content-v2 control protocol. Replay retention remains bounded and scoped to one authenticated online
epoch.
