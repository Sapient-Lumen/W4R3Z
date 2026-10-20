# ADR 0146: Verify synchronization destinations and reuse valid progress

Date: 2026-08-24

Status: accepted

## Context

A Tox file completion is transport truth, not immutable-object truth. Bytes can change between
receipt and object installation because of storage faults, local interference, or a compromised
lower layer. A subscriber must therefore authenticate the complete staged bytes before their
digest-named pathname, signed HEAD acceptance, or visible tree can become authoritative.

Two candidate objects can also finish independently. If one valid object commits before its sibling
fails verification, discarding or retransmitting that good object wastes durable progress. Reuse is
safe only when the subscriber proves the complete existing object's size and SHA-256 against the new
signed candidate before counting it as committed.

## Decision

- Treat completed Tox receive state only as permission to begin staged-object verification. Check
  exact size and complete SHA-256 under the namespace transaction before immutable-store commit.
- On mismatch, fail the pull, fence and clear its signed attempt and private staging, and preserve
  accepted HEAD, activation, object inventory outside the failed candidate, and visible tree truth.
  Never accept or activate a HEAD with one unverified object.
- Retain a sibling candidate object that already committed and still verifies. A fresh explicit pull
  verifies candidate objects already in the immutable store, marks valid objects committed without a
  transport lane, and requests only missing objects.
- Refuse malformed existing objects rather than overwriting them during pull. Quarantine remains the
  explicit `sync-repair` operation.
- Count `committed` as all verified candidate objects, including local reuse; count `requested` and
  `admitted` as transport work only. Thus the qualified partial retry ends with `requested=1`,
  `admitted=1`, and `committed=2`.
- Keep HEAD acceptance last and activation separate. Bind the corruption point, predecessor
  preservation, partial commit, selective retry, candidate identities, and explicit activation into
  both guest receipts and the content-free pair manifest over observed direct UDP and forced TCP.

## Consequences

Destination corruption cannot turn a completed Tox transfer into a trusted object or visible tree.
An independently verified sibling survives failure and reduces retry traffic without weakening the
signed revision boundary. A retry can also converge without requesting any object when both exact
candidate objects already exist and verify locally.

This does not prove media reliability, malicious-kernel resistance, periodic scrubbing, automatic
retry, multi-source failover, or content-v2 behavior. It deliberately does not preserve corrupt
prefix bytes or silently repair an existing digest-named object.
