# Ambition contract: one runtime to rule the browser work graph

This document captures the deliberately over-ambitious shape so that later
revisions can reduce it without losing the organizing idea.

## North star

BrowserRT is a userspace kernel for local browser software. It should eventually
make heavyweight browser applications feel like they have:

- processes;
- actors;
- object references;
- memory leases;
- bounded channels;
- resource scheduling;
- OPFS-backed storage;
- optional GPU/media/render acceleration;
- cross-tab coordination;
- observability;
- replay;
- install/update/cache lifecycle;
- plugin boundaries.

The browser remains the security boundary. BrowserRT is an application-level
kernel inside that boundary.

## Primary runtime objects

### Task

A task is a bounded unit of work with inputs, outputs, trace IDs, cancellation,
deadline, priority, lane requirements, and resource hints.

### Actor

An actor is a stateful runtime process. It owns state, receives ordered methods,
can hold resources across calls, and can be restarted or retired by policy.

### Object

An object is a data-plane reference. It may point to a transferable buffer, a
shared slab region, an OPFS block, a stream, a GPU buffer, a media frame, or a
small inline value.

### Channel

A channel is a bounded edge between producers and consumers. It has capacity,
backpressure, overflow policy, tracing, and optional persistence.

### Lane

A lane is a resource family with admission rules: main, interactive, CPU,
storage, GPU, render, media, network, cross-tab, or maintenance.

### Agent

An agent is a participant in the runtime mesh: main page, dedicated worker,
shared worker, service worker bridge, worklet, visible tab, hidden tab, or Node
cloudtainer test worker.

## The one-runtime rule

There is one BrowserRT API surface. Applications do not import separate runtimes
for SAB, no-SAB, GPU, no-GPU, OPFS, no-OPFS, browser, or Node test execution.
They express requirements and preferences; the runtime selects a plan and traces
its fallbacks.

## The no-lie rule

Every advanced capability must expose its deployment constraints:

- shared memory needs isolation;
- storage has quotas and eviction risk;
- GPU may be absent or lose device state;
- workers have lifecycle and throttling constraints;
- service-worker upgrades can race;
- cross-tab agents may appear and disappear;
- cloudtainer tests are not real-device performance proof.

## The explicit demotion rule

When ambition is too high, demote features into future lanes rather than erasing
them. Example: full plugin isolation may demote to `process contract only`, not
vanish from the north star.

## The baby implementation boundary

The first real implementation should still be narrow:

1. boot;
2. capability detection;
3. trace log;
4. bounded channel;
5. one worker task;
6. transferable buffer path;
7. no-SAB fallback;
8. browser smoke harness;
9. packaged trace receipt.

Everything else is pressure, not immediate scope.
