# Storage worker and sync access frontier

Revision: rev0028

## Why this frontier exists

OPFS asynchronous writes prove that a browser page can persist and read bytes.
That is useful, but it does not exercise the worker-only low-level file path that
serious storage engines care about. OPFS sync access handles are only available
in workers so they do not block the main thread. BrowserRT therefore needs a
storage-worker frontier early.

## Current rev0025 proof shape

`browser:opfs-sync-worker-proof` performs this sequence:

```txt
managed local server
  -> temporary Chromium policy relaxation
  -> CDP attach
  -> page imports BrowserRT
  -> page boots runtime and emits trace
  -> page creates transferable payload object ref
  -> page spawns dedicated module Worker
  -> worker opens OPFS file handle
  -> worker calls createSyncAccessHandle
  -> worker truncate/write/flush/getSize/read/close
  -> worker returns digest and byte equality
  -> page creates OPFS sync object ref
  -> page terminates worker and closes runtime
  -> harness restores policy and writes artifact
```

## Provider assumptions now captured

- Sync access belongs in a Worker, not on the main thread.
- The page can own the control plane while the Worker owns the file handle.
- Payload bytes can enter the Worker through a transferable object ref.
- The result is an OPFS object ref with backend `opfs-sync-access-handle`.
- Trace events must name spawn, ready, call, result, object ref, terminate, and
  runtime close.

## Problems this anticipates

### Exclusive handle collisions

A sync access handle can imply exclusive file access. Future tests must avoid
running sync-handle probes concurrently against the same path. Manifest
`parallelGroup: browser-process` is a coarse early fence.

### Cleanup lies

A proof that writes a file and never removes it can poison later runs. The probe
uses a temporary browser profile and cleanup, but this is still not a production
cleanup policy.

### Durability overclaiming

`flush()` evidence is not the same as crash-recovery evidence. Future journal
proofs must simulate interruption and recovery as separate tasks.

### Performance temptation

The cloudtainer can show that the method exists and behaves correctly; it cannot
produce trustworthy consumer-device storage throughput. Timing is regression
metadata, not a public benchmark.

## Future slices that belong here

1. `browser:opfs-block-write-read-proof` — one block ref, checksum, manifest.
2. `browser:opfs-journal-recovery-proof` — incomplete write, reload, recover.
3. `browser:opfs-quota-pressure-proof` — bounded synthetic quota behavior or
   fake-provider pressure first.
4. `browser:web-locks-storage-leader-proof` — one same-origin storage leader.
5. `sim:storage-provider-faults` — deterministic fake provider for reorder,
   deny, truncate, and cleanup failures.

## Required trace event

The current proof must emit `storage:opfs-sync-worker-result` so later storage-lane work can distinguish worker spawn, call, completion, and object-ref events.

## Multi-tab boundary

The rev0025 sync-worker proof is deliberately single-tab. Multi-tab OPFS safety
must arrive later as a separate Web Locks / storage-leader slice, because a
single successful `createSyncAccessHandle` write/read does not prove same-origin
multi-tab coordination, lock fairness, handle-pool safety, or recovery from a
tab disappearing while it owns storage work.
