# Async I/O and storage provider frontier

Revision: rev0028

BrowserRT's storage lane should not begin as a database. It should begin as a
provider contract with small request/completion proofs. OPFS is the first real
browser provider because it is origin-private, browser-native, and file-shaped.

## Current executable step

Rev0009 adds:

```txt
provider-ish helper: opfsAsyncWriteReadProbe
object ref kind: opfs
trace events: storage:opfs-async-probe-start/result and object:opfs-ref
test task: browser:opfs-async-proof
artifact: REV0039-BROWSER-OPFS-ASYNC-PROBE.json
```

This is deliberately a probe, not yet a storage engine.

## Future storage provider ladder

```txt
opfs-async-probe
  -> opfs-async-block-store
  -> opfs-sync-worker-block-store
  -> journaled block store
  -> quota/pressure-aware store
  -> crash-recovery proof
  -> multi-tab locking proof
  -> compaction proof
```

Each step needs its own manifest task and non-claim boundary.

## Why not build the block store immediately?

Because the storage contract has too many failure modes:

- quota and eviction behavior;
- partial writes;
- browser profile cleanup;
- worker-only sync access handles;
- multi-tab access;
- lock/lease semantics;
- file naming and namespace cleanup;
- crash recovery;
- trace/replay semantics;
- how storage pressure propagates upstream.

A tiny OPFS write/read proof lets the cube validate the browser fixture and
storage capability without pretending the hard parts are solved.

## Provider rules

A storage provider must eventually declare:

```txt
id
lane
capability requirements
supported operations
admission limits
object-ref formats
cleanup semantics
quota behavior
durability non-claims
trace event schema
test task ids
```

The async OPFS probe now gives BrowserRT a storage foothold and a place to hang
these rules.
