# ADR 0126: admit publisher effects behind bounded epoch replay

Status: accepted, 2026-08-21.

## Decision

The first synchronization network service is a default-off publisher dispatcher. It accepts only
canonical HEAD and object requests from one confirmed online epoch after the exact current authority
ledger v3 head, `sync.subscribe` capability, and namespace subscriber membership agree.

Replay state is bounded and non-evicting. The tuple `(friend number, online epoch, message ID)` names
one canonical request. An exact duplicate returns the retained result without loading state again or
repeating a file offer; different bytes conflict. Retained responses are also fenced by the authority
format, epoch, sequence, tail digest, remote principal, and capabilities used for admission. A changed
authority head never receives an old cached response.

For an object request, the service loads the current signed HEAD, compares its complete record digest,
derives the object identity, size, and path locally, verifies the final object, and preconstructs both
the offered and unavailable results. It retains the replay record before calling the exact-FileId file
offer seam. Allocation or replay-capacity failure therefore precedes the effect. Unknown namespaces
return the same denial class as unauthorized namespaces.

## Consequences

- A peer needs subscribe authority to fetch from this publisher. A remote publisher will separately
  need publish authority and writer membership before its HEAD can be accepted locally.
- Reconnect creates a new epoch and must reprove authority. Old Tox file numbers are never replay
  identity.
- The replay cache is process-local. Repeating an immutable offer after a daemon restart can waste
  bandwidth but cannot change a synchronization root; receiver-side exact FileId and digest checks
  remain mandatory.
- Feature advertisement stays absent until Agent construction, receiver orchestration, durable
  attempt recovery, and E2E qualification are all wired.
