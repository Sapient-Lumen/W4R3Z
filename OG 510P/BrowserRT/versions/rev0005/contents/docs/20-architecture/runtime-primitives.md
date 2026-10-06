# Runtime primitives: tasks, actors, objects, channels, lanes, agents

The related-work pass clarified that BrowserRT needs a small primitive set that
can survive the ambitious roadmap.

## Primitive set

```txt
Task      = bounded work unit
Actor     = stateful runtime process
Object    = data-plane reference
Channel   = bounded producer-consumer edge
Lane      = resource family
Agent     = runtime participant
Trace     = evidence stream
Policy    = admission, fallback, limits, recovery
```

These names should remain stable unless a later revision proves they are wrong.

## Why not just functions?

A function-call model is too weak because it cannot naturally represent stateful
workers, persistent resources, GPU-resident data, cross-tab leadership, or
storage compaction. It also tempts the runtime into RPC-first design.

## Why not just actors?

An actor-only model is too coarse for streaming pipelines and stateless parallel
kernels. BrowserRT needs stateless tasks and stateful actors.

## Why not just streams?

Streams are excellent for flow and backpressure, but they do not fully describe
resource admission, worker lifecycle, GPU buffers, OPFS block refs, or replay.
Streams should integrate with BrowserRT channels rather than replace them.

## Object references

Object refs are the key data-plane abstraction. A ref can describe:

- inline small payload;
- transferable buffer;
- shared slab slice;
- OPFS block range;
- stream endpoint;
- GPU buffer;
- media frame;
- future Wasm memory region.

The scheduler should be able to place tasks near object owners or choose transfer
versus shared memory based on object state.

## Actor references

Actor refs are control-plane handles to stateful agents. An actor may be pinned
to a worker, a shared worker, a visible tab, a storage coordinator, or a future
plugin process. Actor methods are tasks with ordered access to actor state.

## Policy references

Policies are named and traceable. A task should not say only `run this`. It
should say:

```txt
priority: user-visible
lanes: CPU preferred, GPU optional
memory: 64 MiB max transient
overflow: spill-to-storage
cancel: cooperative checkpoints every 8 ms
fallback: CPU kernel if GPU unavailable
```

## Trace as a primitive

Trace is not logging. Trace is the runtime's evidence stream. Every queue push,
lease, fallback, actor restart, storage write, and worker crash should be
recordable in a compact form.
