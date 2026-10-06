# BrowserRT moonshot frontier

Current revision: rev0055

This document is intentionally more ambitious than the implementation. It exists so future sessions can see where the project might go without confusing that direction with earned claims.

## Moonshot 1: local browser kernel

BrowserRT becomes the thin runtime under heavy local browser apps: data tools, IDEs, media tools, scientific notebooks, offline-first dashboards, local AI memory, collaborative editors, and generated-app workbenches.

## Moonshot 2: object-ref browser runtime

BrowserRT becomes a Ray-like local object-ref system inside the browser. Object refs point to transfer buffers, shared-memory slabs, OPFS blocks, streams, GPU buffers, model histories, and plugin resources.

## Moonshot 3: local durable execution

BrowserRT grows a local workflow/history layer for resumable jobs. This would be inspired by durable-execution systems but constrained by browser storage, quota, eviction, and lifecycle reality.

## Moonshot 4: same-origin coordination mesh

BrowserRT treats tabs, windows, dedicated workers, shared workers, service workers, and OPFS as a same-origin local cluster. Web Locks chooses leaders; BroadcastChannel routes events; OPFS stores shared local state.

## Moonshot 5: accelerator broker

BrowserRT chooses CPU, WebGPU, WebNN, WASM/SIMD, or fake providers based on capabilities, calibration, and cost. The broker records provider decisions so later sessions can audit the choice.

## Moonshot 6: plugin/component host

BrowserRT grows a capability-scoped plugin model inspired by WASI and the Component Model: plugins receive handles, not ambient global powers.

## Moonshot 7: runtime devtools and replay

BrowserRT becomes its own observability product: queue maps, lane views, traces, histories, model oracles, replay artifacts, and claim checkers.

## Moonshot 8: local-first application substrate

BrowserRT becomes what browser apps reach for when they want to feel less like web pages and more like local software without leaving the browser.

## The non-negotiable caveat

Every moonshot above must stay labeled as one of:

```txt
cloudtainer-buildable
smoke-testable
needs external evidence
shelf until repeated container evidence
```

A future session that cannot build a proof should preserve the dream, not overclaim it.

Audit surface: `facility:mile-high-boundary-audit` keeps this cloudtainer shelf boundary legible.
