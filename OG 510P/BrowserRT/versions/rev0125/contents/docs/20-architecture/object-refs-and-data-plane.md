# Object refs and the data plane — rev0002

## Problem

Browser workloads lose performance when they casually send large JS object graphs through `postMessage`. Structured cloning is fine for control messages and terrible as the default data plane.

## Decision pressure

BrowserRT should adopt `RtObjectRef` early.

```ts
type RtObjectRef =
  | { kind: 'inline'; bytes: number; encoding: 'json' | 'binary' }
  | { kind: 'transfer'; id: string; bytes: number; owner: RtAgentId }
  | { kind: 'shared'; slab: string; offset: number; length: number }
  | { kind: 'opfs'; block: string; offset: number; length: number }
  | { kind: 'stream'; id: string; readable: boolean; writable: boolean }
  | { kind: 'gpu'; id: string; bytes: number; residency: 'device' }
```

The task graph passes refs. The memory/storage/GPU subsystems decide movement.

## Consequences

- Scheduler can delay tasks until data is resident.
- Trace can report bytes moved versus bytes referenced.
- Fallbacks become explicit: GPU ref can materialize to CPU buffer, OPFS block can stream into a transfer buffer, shared slab can degrade to transfer mode.
- Plugins get least-privilege data access.

## Non-claim

This is not a finalized binary ABI. It is the first semantic commitment: **data location is a runtime concept**.

