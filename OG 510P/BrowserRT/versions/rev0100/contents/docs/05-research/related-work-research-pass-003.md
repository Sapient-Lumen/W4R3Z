# Related-work research pass 003 — browser fixture and one-runtime dreambank

Revision: rev0028

## Purpose

This pass expands BrowserRT research in two directions at once:

1. The practical testing slice: how to safely run local browser/CDP proofs in a short cloudtainer window.
2. The ambition frontier: what BrowserRT can steal from runtimes, distributed systems, browser operating systems, and control-plane projects without becoming incoherent.

The cube still stores source titles and domains only. Conversation-level citations belong outside the cube.

## Testing patterns stolen

### Chrome DevTools Protocol

CDP becomes the browser fixture control plane. A browser proof should not be judged by a screenshot or by a page being reachable. It should prove an explicit path:

- local server created,
- policy state handled,
- Chromium launched,
- page target found,
- CDP connected,
- page evaluated,
- BrowserRT imported,
- boot report observed,
- teardown completed,
- artifact written.

### Chromium Telemetry / Catapult

The steal is fixture structure: browser lifecycle, page actions, metrics, and cleanup belong to one owned test unit. BrowserRT should not scatter browser launch logic across demos, scripts, and docs.

### Web Platform Tests

Browser tests need explicit timeout discipline and page-test vocabulary. BrowserRT must keep browser proofs narrow, targetable, and manifest-addressable.

### Bazel-style test contracts

BrowserRT tests should have declared inputs, outputs, capabilities, isolation, size, timeouts, and serial-resource ownership. The browser is a scarce resource lane, not a random side effect.

## Runtime ambition patterns stolen

### WebContainers and browser OS projects

The browser can host serious local runtime products. BrowserRT should not apologize for being ambitious, but it should keep the ambition in substrate form: scheduler, memory, IPC, storage, capabilities, agents, traces, and fixtures.

### workerd and standards-shaped runtimes

BrowserRT should keep its abstractions web-shaped where possible. Do not invent an alien system API when web APIs already provide workers, streams, locks, storage, compression, fetch, and events.

### WASI and the Component Model

Future BrowserRT plugins should be typed and capability-oriented. The useful idea is not “compile everything to Wasm immediately”; it is to define import/export/capability boundaries so kernels can eventually be Wasm, JS, or provider-backed.

### Ray

Tasks, actors, and object references remain the core vocabulary. BrowserRT should avoid smuggling huge data through RPC and instead pass refs to transfer buffers, shared slabs, OPFS blocks, GPU buffers, and streams.

### Erlang/OTP

Supervision is not an afterthought. Agents need child specs, restart policy, escalation, crash traces, and clear non-restartable failure states.

### Kubernetes controllers

Long-lived runtime resources should be reconciled from desired state to observed state. That applies to workers, browser fixtures, storage compaction, mesh leadership, and future plugin processes.

### Tokio

A runtime is not just a queue. It is a bundle of scheduler, timers, I/O/resource drivers, spawn API, blocking pools, and tracing. BrowserRT should grow as a runtime bundle, not as a bag of unrelated helpers.

## Resulting rev0025 decision

The concrete slice is a managed browser/CDP boot probe. It is intentionally small, but it establishes the shape for every future expensive proof:

```txt
manifest task -> owned fixture -> explicit capability probe -> timing artifact -> teardown evidence
```

The dreambank docs can grow, but every dream must eventually pay rent as a tiny executable proof.
