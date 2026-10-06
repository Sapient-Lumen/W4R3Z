# Mile-high dream — rev0044

Current revision: rev0054

Rev0040 intentionally steps away from the next low-level provider proof and asks what BrowserRT could become if it were allowed to grow into the one browser runtime substrate that many local-first, heavy browser applications would want underneath them.

## The project in one sentence

BrowserRT could become **a browser userspace kernel**: one runtime, many providers, no accidental claims.

It should coordinate worker agents, memory/object refs, bounded mailboxes, OPFS and other storage providers, scheduler lanes, overload governors, local browser fixtures, trace artifacts, replay/model histories, plugin capabilities, and eventually same-origin mesh behavior.

## The thing that would make it different

The competition is not one product. The competition is a fractured stack:

- WebContainers prove that browser-hosted development runtimes are possible, but they are optimized around a Node-like development environment.
- workerd and edge runtimes prove that web-compatible JavaScript runtimes can be serious infrastructure, but they live outside the browser.
- Tauri/Electron-like app shells prove that web UI can front serious apps, but they leave the browser sandbox and depend on native packaging.
- Ray/Temporal/Durable Objects prove that tasks, actors, object refs, durable histories, and coordination owners are powerful, but they are server/distributed-system substrates.
- WASI and the WebAssembly Component Model prove that capability-oriented components and resource handles are a useful long-term vocabulary.

BrowserRT's possible niche: **bring the runtime vocabulary into the browser itself, while staying honest about what the browser and this cloudtainer can actually prove.**

## Dream layers

1. **Kernel layer:** task lifecycle, resource lanes, admission, cancellation, trace, object refs.
2. **Data-plane layer:** transferables, SharedArrayBuffer rings, frame streams, OPFS blocks, stream refs, GPU-buffer refs.
3. **Storage layer:** fake providers, OPFS providers, manifests, journals, retained refs, compaction, eventually recovery stories.
4. **Scheduler layer:** cross-lane dispatch, fallback routing, priority/fairness, retry policy, retry budgets, circuit breakers, bulkheads.
5. **Mesh layer:** BroadcastChannel, Web Locks, SharedWorker, ServiceWorker, same-origin tab/workers as a tiny local cluster.
6. **Accelerator layer:** WebGPU, WebNN, WASM/SIMD, CPU fallback, provider calibration, cost-aware dispatch.
7. **Transport layer:** postMessage, MessageChannel, BroadcastChannel, WebRTC, WebTransport, local/server relays.
8. **Plugin layer:** capability-scoped JavaScript/Wasm plugins with explicit resource handles.
9. **Devtools layer:** flight recorder, model histories, replay, queue maps, trace timelines, claim checkers.
10. **Application layer:** local-first IDEs, data tools, media tools, simulation tools, multiplayer/collaboration tools, private offline apps.

## The most important boundary

The cube must keep two truths visible at once:

```txt
Dream freely.
Claim narrowly.
Promote only with evidence.
```

A future session may add moonshot docs. It may not convert a dream into an earned claim unless the cube gains a primitive, provider, trace event, manifest task, artifact, validation-index entry, and non-claim update.

## New rev0044 stance

Rev0040 introduces the **cloudtainer testability shelf**. Items are not abandoned merely because they are hard to test in the cloudtainer. They are separated into:

- cloudtainer-buildable;
- smoke-testable;
- needs external evidence;
- shelf until repeated container evidence.

Nothing is permanently shelved until the cube has strong, repeated evidence across sessions that the cloudtainer cannot exercise it safely or meaningfully.

Audit surface: `facility:mile-high-boundary-audit` keeps this cloudtainer shelf boundary legible.
