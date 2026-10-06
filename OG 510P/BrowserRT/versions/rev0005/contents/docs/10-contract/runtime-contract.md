# BrowserRT runtime contract

BrowserRT is a browser userspace kernel. Its purpose is to coordinate work across
browser resources without turning the main thread into a dumping ground.

## Runtime responsibilities

BrowserRT eventually owns these responsibilities:

- capability detection;
- worker, agent, and process lifecycle;
- task graph scheduling;
- resource lanes;
- bounded channels and backpressure;
- explicit memory ownership;
- cancellation and deadlines;
- OPFS-backed block storage;
- optional WebGPU dispatch;
- provider selection and fallback tracing;
- trace emission and replay preparation;
- cross-tab coordination where available;
- task/actor/object primitive discipline;
- install/update/cache lifecycle posture.

## Non-responsibilities

BrowserRT does not own application semantics such as SQL, vector databases,
spreadsheet formulas, media timelines, or canvas scene graphs. Those belong to
libraries built on top of BrowserRT.

BrowserRT also does not begin as a Unix clone, Node clone, Python runtime, ML
runtime, database, graphics engine, or PWA cache library. It may host those
personalities later.

## Core vocabulary

### Task

A finite unit of work with priority, lane, deadline, dependencies, cancellation,
resource hints, and trace identity.

### Agent

A long-lived stateful runtime participant such as a worker, storage leader, GPU
device manager, mesh coordinator, plugin process, or service-worker bridge.

### Object ref

A stable reference to data that may live in a transferable buffer, shared slab,
OPFS block, stream, GPU buffer, or future media frame. Object refs are the data
plane handle.

### Supervisor

An agent that owns child-agent lifecycle policy: restart, replace, fail parent,
escalate, quarantine, or terminate.

### Provider

A backend that can execute a kernel for a lane: CPU JS, Wasm, WebGPU, WebCodecs,
OffscreenCanvas, AudioWorklet, or future accelerator. Provider selection is
capability- and cost-aware.

## Invariants

### BR-INV-001: no hidden hot-path object soup

Large payloads must not travel as giant arrays of JavaScript objects. Hot-path
payloads use typed arrays, transferables, shared slabs, OPFS block refs, streams,
or GPU buffer refs.

### BR-INV-002: no unbounded queues

Every runtime queue must declare a capacity policy. Overflow must wait, drop,
spill, degrade, cancel, or fail explicitly.

### BR-INV-003: cancellation reaches every task

Every task accepts a cancellation context. Non-cooperative tasks must be marked
and isolated so cancellation can kill or replace their worker.

### BR-INV-004: fallbacks are traced

A fallback from shared memory to transfer, GPU to CPU, OPFS to memory, native
scheduler to polyfill, or worker to main thread must emit a trace event.

### BR-INV-005: capability tiers are not separate products

There is one BrowserRT. It chooses capability tiers at boot and per task.
Applications may ask for requirements, but they do not import separate runtimes.

### BR-INV-006: persistence has recovery

A persistent write is not complete until its recovery semantics are clear:
journaled, manifest-swapped, temporary, or deliberately best-effort.

### BR-INV-007: RPC is cold path only unless proven otherwise

BrowserRT may expose pleasant remote-call APIs, but bulk data does not move
through hidden structured-clone RPC. Hot paths use object refs and explicit data
movement.

### BR-INV-008: every agent has a supervisor policy

Worker death, GPU device loss, storage contention, plugin failure, and mesh
leader loss are expected events. Every long-lived agent must declare its failure
policy.

### BR-INV-009: borrowed ideas become owned contracts

A researched pattern does not enter BrowserRT as folklore. It must map to a
BrowserRT contract, vocabulary item, validation check, or open question.

### BR-INV-010: tasks, actors, and objects are distinct

Stateless work, stateful processes, and data-plane references must not collapse
into one vague RPC concept. The runtime tracks tasks, actors/agents, and object
refs as separate primitive families.

### BR-INV-011: trace is evidence, not decoration

If a scheduler decision, fallback, memory movement, storage write, actor restart,
or lane demotion matters for correctness or performance, it must be traceable.

## Public boot sketch

```js
import { boot } from './src/browserrt.mjs';

const rt = await boot({
  isolation: 'prefer',
  workers: 'calibrate',
  storage: 'opfs-or-memory',
  gpu: 'auto',
  telemetry: 'always'
});
```

## Task context sketch

```ts
type RtTaskContext = {
  signal: AbortSignal;
  deadline: RtDeadline;
  priority: RtPriority;
  lane: RtLane;
  trace: RtTraceWriter;
  memory: RtMemory;
  yield: () => Promise<void>;
};
```

## First implementation boundary

Rev0003 proves the first narrow implementation boundary inside the cloudtainer:

- boot report and capability detection;
- trace emission;
- bounded channel behavior;
- one Node worker-agent path;
- one transferable-buffer object-ref path;
- one supervisor restart path;
- one machine-readable proof artifact suitable for replay planning.

The comparable browser Worker/CDP smoke page remains the next boundary.
Everything broader than this proof should remain contract until the primitive path
stays stable under validation.
