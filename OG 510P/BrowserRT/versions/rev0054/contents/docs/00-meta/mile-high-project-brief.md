# Mile-high project brief

Revision: rev0028

## One sentence

BrowserRT is a cloudtainer-built browser userspace kernel: a small runtime layer
that teaches browser software to coordinate work, memory, storage, browser
fixtures, traces, and future accelerators as one coherent local system.

## Less compressed

Browsers already expose many powerful primitives, but application code usually
meets them as scattered APIs: Worker, postMessage, transferable buffers,
SharedArrayBuffer, OPFS, WebGPU, OffscreenCanvas, BroadcastChannel, Web Locks,
PerformanceObserver, and browser automation fixtures. BrowserRT tries to become
the layer that gives those primitives runtime discipline:

- named tasks instead of anonymous work,
- explicit object references instead of accidental giant clones,
- bounded channels instead of unbounded message floods,
- supervisors instead of mystery worker death,
- provider lanes instead of feature-specific rewrites,
- traces instead of vibes,
- manifest-addressable tests instead of giant expensive integration blobs.

## What it is today

Today it is still a baby cube. It has:

- an archive/reentry discipline learned from previous datacubes,
- runtime contracts for lanes, capabilities, memory ownership, envelopes, and
  control/data-plane separation,
- a tiny executable Node/cloudtainer proof for boot, bounded channel,
  transferable object reference, worker agent, and supervisor restart,
- a manifest-driven test facility with timing, impact planning, sharding, and
  artifact output,
- a one-shot browser/CDP boot probe that owns local server setup, managed policy
  restoration, Chromium launch, page import, capability capture, and teardown.

It is not yet a complete browser runtime.

## What it could become

The ambitious version is a local browser operating substrate for serious apps:

```txt
workers + memory + streams + OPFS + GPU + render + media + audio + mesh + telemetry + replay + plugins
```

A future application would ask BrowserRT for a resource or job, not manually
stitch every browser primitive together:

```txt
run this CPU task, with this deadline, using this memory ref;
spill this queue to OPFS if storage pressure allows;
dispatch this GPU kernel only if upload/readback wins;
keep this render job off the main thread;
coordinate this maintenance task across tabs;
record a trace I can replay after a crash.
```

## What it must not become

BrowserRT must not become a generic wrapper over every browser API. It must not
become a database, a video editor, a design tool, a benchmark trophy, or a
framework-specific scheduler. Those can be built on top. BrowserRT is the
coordination layer under them.

## The weird ambition

If the project gets very far, BrowserRT could make a browser tab feel less like
a page and more like a local compute node:

- worker agents supervised like tiny processes,
- OPFS blocks treated like local durable-ish storage,
- GPU/CPU/render lanes selected by measured provider cost,
- multiple same-origin tabs participating in a small mesh,
- every expensive run producing a trace, not just a pass/fail,
- plugins running under declared capability budgets,
- failed jobs replayable from compact artifacts.

The dream is intentionally too large. The cube exists to keep that dream from
turning into incoherence.
