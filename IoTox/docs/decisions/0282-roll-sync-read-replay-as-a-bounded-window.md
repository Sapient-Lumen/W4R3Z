# ADR 0282: roll synchronization reads through a bounded exact-replay window

Status: accepted, 2026-09-01.

## Context

The two-hour IoTox/Resilio shadow first failed after eight healthy mutations. The publisher had
retained exactly 256 request results: 240 periodic HEAD reads and 16 immutable-object reads. The
next HEAD request was locally queued and repeatedly retried, but the non-evicting publisher table
could never admit it while the authenticated peer remained online. At the ordinary 30-second poll
interval, the same default becomes a roughly two-hour connection-lifetime failure.

Adding a retirement acknowledgement would change framing after the sync protocols were frozen.
Increasing the table merely postpones exhaustion. Unlike commands, Ratox input, authority changes,
or update effects, all publisher operations on the sync v1, content-v2, and tree-v2 surfaces are
authorized reads of signed state or offers of immutable digest-bound bytes.

## Decision

Each synchronization publisher keeps its configured maximum as a FIFO exact-replay **window**:

- a request whose friend/epoch/carrier/message ID remains in the window must have identical
  canonical bytes and unchanged authority, and returns the exact retained result without another
  file offer;
- same-ID/different-payload reuse while retained remains a protocol error;
- only after a fresh request has validated and produced a result, a full window retires its oldest
  entry in constant time, increments a content-free eviction counter, and retains the new result
  before any file-offer effect;
- an identifier outside the window is fresh read-only work. It is fully re-authorized against the
  current session, namespace membership, signed HEAD, object identity, quotas, and local bytes. It
  may repeat an immutable file offer, but it cannot recover old authority or select a path; and
- malformed, unsupported, or otherwise unhandled work does not evict a valid entry.

This applies consistently to HEAD/object/range v1, content object/availability v2, and tree-v2
inventory/object service. `sync-status` exposes the three eviction counters. No peer frame, feature
bit, subscriber durable attempt, worker queue, transfer terminal ledger, command replay, authority
record, update effect, or Ratox side-effect rule changes.

## Consequences

- Long-lived healthy sessions no longer have a finite request lifetime.
- Exact at-most-one file-offer behavior is guaranteed inside the configured recent window. Outside
  it, a duplicate can waste bounded transfer work just as it can after daemon restart, but digest,
  FileId, current-HEAD, authority, and receiver verification still prevent content substitution or
  state advancement.
- A malicious stream can turn over replay history, but every replacement pays the complete current
  authorization and immutable-object checks and remains subject to existing request, lane, byte,
  store, and worker bounds.
- Side-effecting protocols retain their non-evicting or cumulative-fence rules. This decision is
  specific to synchronization publisher reads and must not be generalized to commands or terminal
  input.

The deterministic service tests force all three publisher families through one- and two-entry
windows. The accepted long shadow must additionally report a positive publisher eviction count so
it proves operation beyond the original exhaustion boundary.
