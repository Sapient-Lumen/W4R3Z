# Runtime dreambank 015 — admission-control kernel

Revision: rev0028

## Dream

BrowserRT should eventually let apps express overload policy as runtime infrastructure:

```ts
const admission = rt.admission.watermark({
  lowWatermarkBytes: 2 * MiB,
  highWatermarkBytes: 8 * MiB,
  hardLimitBytes: 12 * MiB,
  shed: ['maintenance', 'background'],
  protect: ['critical', 'user-blocking'],
  providerHealth: 'storage-lane'
})

const accepted = admission.tryAdmit({
  bytes: frame.byteLength,
  priority: 'background',
  lane: 'ipc'
})
```

This should feel like a browser-local equivalent of a tiny overload governor.

## New runtime noun

```txt
WatermarkAdmissionController
```

It is a cheap, deterministic admission layer in front of future queues, task lanes, storage providers, and mesh providers.

## Why it belongs in BrowserRT

Admission control crosses BrowserRT’s core responsibilities:

- bounded queues;
- spill mailboxes;
- storage provider health;
- priority and fairness;
- trace evidence;
- scheduler pressure;
- graceful degradation;
- non-claims around performance.

If every app invents this separately, BrowserRT will never become a coherent runtime.

## Provider ladder

```txt
static-watermark-admission
priority-watermark-admission
credit-based-admission
latency-adaptive-admission
fair-queue-admission
mesh-wide-admission
```

rev0025 only implements the first rung.

## Admission states

```txt
open        = below low/high and provider healthy
congested   = high watermark crossed; low priority work rejected
recovering  = releases drain bytes until low watermark is reached
unhealthy   = provider pressure causes low-priority rejection
hard-limit  = projected in-flight bytes exceed hard cap
```

## Trace shape

A rejected admission should be as inspectable as an accepted one. Future devtools should show:

```txt
who was rejected
why they were rejected
what bytes were in flight
which provider/lane was unhealthy
when low-watermark recovery occurred
whether critical work bypassed congestion
```

## Ambition

The far version is a browser-local overload-control plane:

```txt
mailbox watermarks
storage quotas
worker-lane saturation
GPU readback pressure
main-thread jank signals
cross-tab fairness
plugin budgets
```

All of those pressures feed into one visible, traceable admission surface.

## Non-goal for this revision

No adaptive latency controller enters here. rev0025 proves deterministic watermark semantics first.

## Current event anchor

The baby proof requires `admission:high-watermark` and `admission:low-watermark` trace events so overload state is visible instead of hidden inside a boolean.
