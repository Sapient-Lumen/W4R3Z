# Paged content fabric v2

## Object graph

A paged revision has one signed HEAD, one immutable root manifest, immutable page objects,
and immutable chunk objects:

```text
HEAD -> root digest
          |
          +-- page 0 digest -> chunk records -> SHA-256 chunk objects
          +-- page 1 digest -> chunk records -> SHA-256 chunk objects
          +-- ...
```

The root is fixed metadata plus 80 bytes per page. Each page has a 96-byte header and 40
bytes per chunk record. Root, pages, chunks, and final artifact are independently digested.

## Bounded operation

`read_content_chunk_window()` loads only the caller's output span and intersecting page
objects. A worker can reuse that span as borrowed storage for `MultiSourceScheduler`. Memory
therefore follows configured window and peer counts, not total artifact size.

The flat-v1 content manifest remains accepted. Sequential callers pass the previous
`next_artifact_offset` as a hint so later windows do not rescan all earlier lengths.

## Availability

Two mechanisms coexist:

- exact inventory pages: one bit per requested manifest chunk, bounded by request limits;
- conservative sketches: fixed-size filters where a negative is authoritative and a positive
  means only “possibly present.”

Exact pages drive rarest-first scheduling. Sketches cheaply avoid peers that definitely lack
an object. Neither grants trust: every received object is SHA-256 verified.

## Publication

Completed private staging objects are installed by digest. Same-filesystem ingest can verify,
hard-link into the store, and unlink the staging name without copying payload bytes.
Cross-filesystem ingest verifies while copying through a bounded reusable buffer and then
publishes without replacement.

## Retention

The pin ledger records namespace, generation, root digest, expiry, and flags in a
checksum-protected append-only journal. Replay repairs a torn final record but rejects a
validly encoded conflicting generation. Garbage collection marks pinned roots, pages, and
chunks into a bounded conservative filter and sweeps unmarked objects. False positives retain
objects; they cannot make a live marked object look absent.

## Receiver session

`ContentFabricSession` combines the bounded pieces into a transport-neutral receiver state
machine. It acquires paged metadata first, marks already-present objects, accepts exact peer
inventories, issues rarest-first assignments, verifies and installs completed staging files,
advances through windows, and reconstructs only after complete coverage. Restart recovery
rescans immutable store objects rather than replaying an unbounded per-chunk journal.

IoTox does not yet attach that state machine to its live range-event pump or perform final
namespace activation. The current range and inventory commands expose the transport pieces
for deterministic development and real-network measurement.
