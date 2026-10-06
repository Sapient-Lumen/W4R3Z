# Runtime dreambank 004 — one browser userspace kernel, if it gets to be enormous

Revision: rev0028

This is an ambition document, not an implementation claim.

BrowserRT could eventually become a local userspace kernel with these provider families:

```txt
compute provider:      main thread fallback, dedicated Worker, worker pool, fake simulator
memory provider:       clone, transfer, SharedArrayBuffer slab, OPFS spill, GPU buffer
storage provider:      memory, OPFS block store, journaled OPFS store, fake simulator store
scheduler provider:    FIFO, lane-aware, deadline-aware, work-stealing, deterministic simulator
render provider:       DOM/main fallback, OffscreenCanvas worker, WebGPU render lane
media provider:        Canvas frames, WebCodecs, fake frame source
mesh provider:         none, BroadcastChannel, SharedWorker, Web Locks coordinator
trace provider:        in-memory, JSON artifact, timeline viewer, replay recorder
plugin provider:       JS module, Worker module, Wasm component, capability-scoped process
```

The one-to-rule-them-all version is not "everything is implemented." It is that every subsystem speaks the same nouns:

```txt
task, agent, actor, object ref, lane, provider, capability, lease, trace, history, supervisor, reconciler
```

## The audacious endpoint

A future app could say:

```txt
Run this workflow as a logical agent.
Give it a bounded object-ref channel.
Persist checkpoints to OPFS.
Use browser Workers now, SAB later if isolated, GPU only if calibration says so.
Expose a trace I can replay.
If the page closes, preserve enough history to resume.
If another tab is visible, transfer foreground priority there.
If this worker dies, reconcile to desired state.
```

That is the dream.

## The safety rail

Every dream feature must reduce to all five surfaces:

1. primitive contract;
2. provider contract;
3. trace event schema;
4. manifest test;
5. non-claim boundary.

If a feature cannot be decomposed that way, it is not ready to enter the cube.

## What rev0025 actually adds

Rev0008 adds only the browser Worker agent proof. This matters because it converts "we can boot a page" into "we can run a BrowserRT agent in a real browser Worker and move bytes through it." It does not make the project a scheduler, persistent workflow engine, durable actor runtime, or GPU/media platform.

## Future dream slices

Ordered from smallest useful proof to larger architecture pressure:

1. OPFS async write/read proof.
2. OPFS worker sync-access proof.
3. SharedArrayBuffer cursor/ring proof.
4. Deterministic fake scheduler proof.
5. Trace span tree and JSON replay fixture.
6. Browser supervisor restart/degrade proof.
7. Web Locks leader-election proof.
8. BroadcastChannel two-page mesh proof.
9. WebGPU compute provider proof.
10. Provider-calibration decision proof: CPU vs Worker vs GPU.
