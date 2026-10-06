# Phase roadmap

## Phase 0: cube and contract

Freeze reentry, packaging, validation, and runtime contracts. This was rev0001.

## Phase 0.5: related-work steal-bank

Import adjacent-runtime lessons without importing scope. This is rev0002. It adds
primitive vocabulary, steal-bank, tradeoff register, mesh/lifecycle posture, and
north-star demos.

## Phase 1: kernel seed

Implement boot, capability detection, trace log, bounded channel, worker spawn,
and transferable-buffer task execution. Rev0003 begins this phase with a Node
worker-thread proof: boot report, trace, channel, transfer ref, supervised worker
call, transferred `ArrayBuffer`, forced crash, and restart.

Exit receipt:

- Node smoke test passes;
- transfer detachment is observed on the sender side;
- worker exit and supervisor restart are traced;
- local browser smoke harness boots;
- trace contains boot, channel, worker, transfer, restart, and close events;
- no external dependency added.

## Phase 2: memory and IPC

Add transfer pool, object refs, leases, SAB ring where available, mailbox
abstraction, and fallback traces.

Exit receipt:

- transfer baseline works without SAB;
- SAB tier works when isolation is present;
- illegal lease behavior is caught or traced;
- large payload path avoids structured-clone object soup.

## Phase 3: scheduler

Add task graph, actors, resource lanes, priorities, deadlines, backpressure
propagation, calibration, cooperative yield helpers, and kill-box worker policy.

Exit receipt:

- tasks, actors, and objects are distinct in traces;
- admission control rejects or delays work under memory/queue pressure;
- scheduler emits why a fallback or lane choice happened.

## Phase 4: storage

Add OPFS block store, Node fs test backend, manifest, journal, checksums, quota
monitoring, compaction, and recovery tests.

Exit receipt:

- crash/reload recovery smoke passes in local browser harness;
- corrupt test block is detected;
- quota estimate is surfaced where available;
- storage write semantics are labeled temporary, journaled, or manifest-swapped.

## Phase 5: browser harness

Add local server, CDP runner, COOP/COEP test page, worker/SAB/OPFS/WebGPU smoke
receipts, screenshots where useful, and trace artifacts.

Exit receipt:

- browser smoke tests are packaged as artifacts;
- isolation on/off paths are tested;
- failure messages are actionable.

## Phase 6: GPU/media/render lanes

Add GPU capability detector, shader registry, buffer pool, compute dispatch,
readback measurements, CPU fallbacks, WebCodecs/OffscreenCanvas posture, and
device-loss handling.

Exit receipt:

- tiny GPU compute works where available;
- CPU fallback works everywhere;
- device absence and device loss are traceable;
- no real-device performance claim is made from cloudtainer-only evidence.

## Phase 7: mesh and lifecycle

Add BroadcastChannel/Web Locks/SharedWorker coordination, service-worker bridge,
leader election, agent lifecycle, visibility-aware priority, and stale-agent
recovery.

Exit receipt:

- two-tab local harness coordinates one exclusive job;
- storage leader election is traced;
- hidden/visible priority change is reflected in scheduling policy.

## Phase 8: devtools and replay

Add trace viewer, queue inspector, memory map, storage map, runtime dashboard,
record/replay format, and chaos lab.

Exit receipt:

- a failed workload can be summarized by a compact trace artifact;
- replay can reconstruct control-plane events;
- devtools reads traces rather than private runtime internals.

## Phase 9: plugin/process model

Add capability-scoped JS/Wasm plugins, process lifecycle, permission declarations,
resource limits, and host interface contracts.

Exit receipt:

- plugin can be denied a capability;
- plugin crash is isolated to its worker/process;
- host does not overclaim browser-level security isolation.
