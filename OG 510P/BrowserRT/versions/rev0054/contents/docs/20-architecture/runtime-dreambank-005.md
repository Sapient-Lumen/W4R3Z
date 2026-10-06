# Runtime dreambank 005 — one browser kernel with provider I/O

Revision: rev0028

The next dream is BrowserRT as a provider-oriented I/O runtime. Every serious
operation becomes a request to a lane provider, and every result becomes a traced
completion. This is a more powerful mental model than promises plus workers.

## The one-to-rule-them-all version

```txt
app intent
  -> task graph
  -> resource request
  -> provider admission
  -> submit descriptor
  -> data-plane object refs
  -> completion event
  -> trace/replay record
```

A future BrowserRT app should be able to say:

```txt
write these bytes to persistent local storage;
submit this query kernel to CPU or GPU;
render this tile in an OffscreenCanvas worker;
send this media frame through a bounded lane;
coordinate this compaction job across tabs;
record every request and completion so the run can be replayed.
```

The runtime should decide which provider can serve the request under current
capabilities, pressure, and policy.

## Dream primitive: provider registry

```ts
rt.providers.register({
  id: 'opfs-async',
  lane: 'storage',
  capabilities: ['opfs'],
  operations: ['put', 'get', 'delete', 'estimate'],
  submit(request, ctx) { /* bounded operation */ }
})
```

A provider is not merely an implementation detail. It needs:

- capability requirements;
- supported operation names;
- admission limits;
- resource accounting;
- trace event schema;
- non-claim boundary;
- fallback relation to other providers.

## Dream primitive: request/completion record

```ts
request = {
  id,
  lane: 'storage',
  provider: 'opfs-async',
  op: 'put',
  priority,
  deadline,
  payloadRef,
  capabilityGrant,
  traceId
}

completion = {
  requestId,
  status: 'completed' | 'failed' | 'cancelled',
  outputRef,
  durationMs,
  bytes,
  error
}
```

This maps future SAB rings, OPFS block writes, GPU dispatches, worker calls, and
mesh messages into one observable shape.

## Dream primitive: authority ledger

BrowserRT cannot be a perfect security sandbox inside one origin, but it can
make authority auditable:

```txt
process localdb-indexer requested storage:write:segments
provider opfs-async admitted request storage.put
completion wrote opfs block ref opfs:segments/0001
```

This matters for plugins, generated code, and debugging.

## Dream primitive: testable provider ladder

Every provider should enter through a ladder:

1. capability-only probe;
2. tiny request/completion proof;
3. object-ref trace proof;
4. cleanup/teardown proof;
5. quota/pressure proof;
6. worker/off-main-thread proof;
7. crash/recovery proof;
8. performance/stress proof.

Rev0009 lands at steps 1–4 for async OPFS only through manifest task `browser:opfs-async-proof`.

## Ambitious endgame

The endgame is not one monolithic engine. It is a runtime where different heavy
browser features all speak the same small language:

```txt
capability -> provider -> request -> object ref -> completion -> trace -> replay
```

That language can support local-first apps, IDEs, data tools, graphics tools,
media tools, and simulation/debugging surfaces without rewriting scheduling,
tracing, memory, and tests for each one.
