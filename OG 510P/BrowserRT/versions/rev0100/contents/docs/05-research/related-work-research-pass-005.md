# Related work research pass 005 — async runtimes, capability I/O, and OPFS storage pressure

Revision: rev0028

This pass steals ideas from systems that are not browser-worker libraries: Deno,
Bun, libuv, io_uring, WASI, the WebAssembly Component Model, OPFS, and SQLite
Wasm OPFS VFS work. The point is not to import any code. The point is to sharpen
BrowserRT's future shape as a browser userspace kernel with explicit resources,
providers, permissions, submit/complete queues, and storage traces.

## What to steal

### Deno: make authority visible

Deno's permission model is useful design pressure even though BrowserRT cannot be
an origin-level security boundary. BrowserRT should still make internal authority
visible: a process or provider should declare the resource families it needs, and
trace events should show when storage, worker, GPU, network, or plugin authority
is exercised.

Steal:

- explicit permission vocabulary;
- deny-by-default for future plugin/process APIs;
- resource-scoped capabilities instead of ambient access;
- test surfaces that can run with deliberately restricted permissions.

Reject:

- pretending BrowserRT can enforce OS-level security inside a single browser
  origin;
- adding prompts or policy UI before the primitive contracts exist.

### Bun: a runtime can win by collapsing tool surfaces

Bun is a reminder that runtime products can gain power by owning the boring
surfaces: run, test, package, transpile, install, serve. BrowserRT should not
clone Bun, but the cube should learn from the all-in-one posture: the test
facility, browser fixture, packaging, trace records, and proof artifacts are not
side quests. They are part of the runtime product.

Steal:

- low startup-friction ergonomics;
- one-command proof loops;
- integrated test/package surfaces;
- small obvious commands for common paths.

Reject:

- broad toolchain sprawl before the runtime kernel is stable;
- external package-manager dependence inside the cube.

### libuv: handles, requests, and lanes

libuv's split between an event loop, long-lived handles, short-lived requests,
and an internal thread pool maps cleanly onto BrowserRT language. BrowserRT
should distinguish:

- `handle`: long-lived agent/provider/resource identity;
- `request`: bounded operation submitted to a lane;
- `completion`: explicit result event;
- `lane`: resource-specific scheduler domain.

The storage lane, browser fixture, worker pool, GPU lane, and mesh coordinator
should not all be modeled as generic promises. They are requests against specific
providers with different completion and failure rules.

### io_uring: submit/completion rings beat ad-hoc mailboxes

The future SAB transport should not be only a queue of messages. It should be a
submission/completion design: producers submit small descriptors, providers
publish completions, and the data plane stays in object refs, slabs, OPFS blocks,
or GPU buffers. This matters for cancellation, backpressure, priority inversion,
and tracing.

Steal:

- separate submission queue and completion queue;
- fixed-size descriptors that refer to external data;
- completion records as first-class events;
- bounded queue capacity from the start.

Reject:

- Linux-specific details;
- busy polling by default;
- pretending browser scheduling has kernel-grade guarantees.

### WASI and Component Model: resources are handles, not blobs

WASI capability design and Component Model resource types reinforce a BrowserRT
rule: big things should be passed as handles/resources, not copied values.
OPFS files, SharedArrayBuffer slabs, GPU buffers, workers, channels, streams, and
future plugin components should all be resource handles with ownership rules.

Steal:

- typed resource handles;
- explicit import/export worlds for future plugin/process boundaries;
- capability-scoped APIs;
- ownership and borrowing vocabulary.

Reject:

- trying to implement WASI in BrowserRT now;
- designing a plugin ABI before task/memory/storage traces are stable.

### OPFS and SQLite Wasm: browser storage is serious but subtle

OPFS is the first credible storage backing for BrowserRT's persistent lane, but
SQLite Wasm OPFS/VFS discussion pressure makes the danger clear: concurrency,
locking, quota, crash recovery, and sync-access-handle semantics are hard. A
single async write/read proof is not a storage engine.

Steal:

- OPFS as an origin-private provider;
- worker-only sync-access-handle as future fast path;
- provider variants chosen by capability and concurrency needs;
- quota and cleanup evidence in tests.

Reject:

- treating OPFS as normal user-visible files;
- assuming persistence equals durability;
- hiding browser quota/eviction limits;
- merging async, sync-handle, multi-tab, and crash recovery proofs.

## New pressure on BrowserRT

The runtime vocabulary now wants these nouns:

```txt
resource handle   = long-lived object authority or identity
request           = bounded operation submitted to a provider/lane
completion        = explicit result/failure/cancellation record
provider          = capability-backed implementation of a lane
capability grant  = declared access to a resource family
object ref        = data-plane handle to bytes/streams/files/GPU/shared memory
```

This pass pushes BrowserRT toward a future where storage, GPU, render, worker,
media, and mesh operations all share a common request/completion discipline.
That is the ambitious dream. The rev0025 proof only adds the smallest storage
step: an async OPFS write/read slice with object-ref and trace evidence.

## Non-claims

- No external code or dependency was imported.
- This pass does not make BrowserRT a Deno/Bun/libuv/io_uring/WASI clone.
- OPFS async write/read is not a block store, database, sync-access-handle proof,
  durability proof, or multi-tab concurrency proof.
- Capability vocabulary inside one browser origin is not a security guarantee.
