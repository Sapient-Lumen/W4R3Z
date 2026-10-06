# Endgame scenarios

Revision: rev0028

This document is allowed to dream. It is not a claim that the current cube does
these things.

## Endgame A: browser userspace kernel

BrowserRT becomes the default substrate for heavyweight local browser apps. It
coordinates workers, memory, storage, GPU, render, media, mesh, cancellation,
telemetry, and replay through one tiny vocabulary.

What a user sees: web apps that feel like native local tools without requiring a
backend for every heavy operation.

What a developer sees: one runtime contract instead of scattered ad hoc Worker,
OPFS, WebGPU, and testing code.

## Endgame B: local compute node

A same-origin browser session becomes a small local cluster. Visible tabs get
interactive priority. Hidden tabs can donate background compute. A shared worker
or elected tab coordinates storage maintenance. BrowserRT reconciles desired
state against observed agents.

What this enables: browser IDEs, local analytics, offline data apps, and agentic
artifact workbenches that keep working across tabs and reloads.

## Endgame C: trace-native development

Every BrowserRT job emits enough evidence to debug it later. Failures become
portable trace artifacts. Cloudtainer development stops depending on vague
reproduction instructions.

What this enables: fast iteration over complex browser behavior despite short
execution windows.

## Endgame D: capability-scoped plugin runtime

Apps can load local JS or Wasm-like plugins through BrowserRT process contracts:
allowed lanes, storage scopes, memory budgets, cancellation behavior, and trace
requirements.

What this enables: user-extensible local browser software without letting every
plugin invent its own runtime failure modes.

## Endgame E: provider marketplace without dependency sprawl

The kernel stays small, but providers can exist for lanes:

- CPU worker provider,
- SAB mailbox provider,
- OPFS block provider,
- WebGPU dispatch provider,
- OffscreenCanvas render provider,
- CDP browser-fixture provider,
- future cross-browser fixture providers,
- simulated providers for tests.

What this enables: the runtime can be ambitious without requiring every app or
every test to load every capability.

## Endgame F: anti-framework infrastructure

BrowserRT does not compete with React, Vue, Svelte, vanilla, or future UI
frameworks. It becomes what those apps call when they need serious work done
without breaking responsiveness.

What this enables: adoption by many app styles because BrowserRT is runtime
infrastructure, not app architecture.

## Tempering rule

Every endgame scenario must eventually collapse into:

```txt
a primitive + a provider + a trace event + a manifest test + a non-claim boundary
```

If an ambition cannot be reduced that way, it is probably decorative and should
not drive implementation.
