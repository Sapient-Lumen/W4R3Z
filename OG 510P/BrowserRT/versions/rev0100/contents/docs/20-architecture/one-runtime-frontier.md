# One-runtime frontier

Revision: rev0028

## North-star claim

BrowserRT is allowed to dream as if it were the one browser runtime substrate to rule them all:

```txt
workers + memory + streams + OPFS + GPU + render + media + audio + mesh + telemetry + replay + plugins
```

But BrowserRT is not allowed to claim any of that without a small manifest task and an artifact.

## What “one runtime” means

BrowserRT should become the coordination layer that application code can ask for:

- a task,
- an actor,
- an object reference,
- a storage block,
- a GPU dispatch,
- a render job,
- a browser fixture,
- a mesh lease,
- a trace,
- a replayable event stream.

It should not become the application, database, video editor, vector engine, or UI framework.

## Provider model

Every major lane should eventually be provider-backed:

| Lane | Possible providers | Always required fallback |
|---|---|---|
| CPU | Dedicated Worker, Node worker thread, local process surrogate | main/process fallback for tests |
| IPC | structured clone, transferables, SAB ring | structured clone |
| Storage | OPFS, Node fs, memory store | memory store |
| GPU | WebGPU, CPU kernel | CPU kernel |
| Render | OffscreenCanvas, Canvas2D, no-render test provider | no-render test provider |
| Browser fixture | CDP Chromium, simulated browser, future cross-browser adapters | simulated fixture for unit tests |
| Mesh | BroadcastChannel, Web Locks, SharedWorker | single-agent mode |
| Plugin | JS module, Wasm component, provider adapter | disabled plugin path |

## Desired-state reconciliation

The runtime should eventually store a desired state:

```txt
3 CPU agents wanted
1 storage leader wanted
0 leaked browser fixtures wanted
all manifests recovered
all claimed leases released
all background jobs cancellable
```

A supervisor/reconciler compares observed state and takes small actions. This avoids turning runtime maintenance into ad hoc cleanup.

## Browser fixture as first reconciled resource

The rev0025 CDP boot probe is the first resource that needs reconciliation discipline:

```txt
desired: local server running, policy relaxed, Chromium launched, CDP connected
observed: target page loaded, BrowserRT imported, capabilities reported
finally: CDP closed, Chromium killed, server closed, temp profile removed, policy restored
```

This should become the model for OPFS sync handles, GPU devices, service workers, shared workers, and future mesh leaders.

## Forbidden ambition drift

BrowserRT should not drift into:

- “all browser APIs wrapped for convenience,”
- “benchmark claims without external devices,”
- “one monolithic integration test,”
- “daemon processes that are assumed to survive turns,”
- “framework-specific runtime shape,”
- “GPU-only or SAB-only hot paths,”
- “plugin freedom without capability accounting.”

## Keep

The ambition is retained as architecture pressure, not release claim. Each frontier gets a named lane, a provider shape, a fallback, and a future proof task.
