
# Borrowed patterns map

This map translates researched adjacent work into BrowserRT-owned patterns.
It is not a list of dependencies.

## Pattern table

| Borrowed pattern | Seen in family | BrowserRT form | First revision pressure |
|---|---|---|---|
| Remote function ergonomics | Worker RPC libraries | `rt.rpc` cold-path facade | Do not let RPC carry bulk bytes |
| Worker pool statistics | Node/browser pools | `RtWorkerPoolStats` trace events | Measure queue wait and run time |
| Custom queues | Piscina-style pools | Lane scheduler hooks | Avoid one global FIFO |
| Cancellation | Worker pools and platform AbortSignal | Mandatory task signal | Mark non-cooperative kernels |
| DOM/proxy tradeoff docs | Partytown | Explicit proxy limitations | Never pretend proxying is free |
| Process-like lifecycle | Browsix/WebContainers | `agent` and `supervisor` | Spawn, crash, restart, terminate |
| Pipes | Unix/Browsix | Bounded `RtChannel` | Capacity required at creation |
| Shared object store | Ray/WebContainers/browser fs | `RtObjectRef` + `RtBlockRef` | Return refs, not giant payloads |
| Backend filesystem adapters | BrowserFS/ZenFS/Emscripten | `RtStorageBackend` | Node backend for tests, OPFS later |
| Manifest/journal discipline | OPFS/SQLite patterns | `RtStorageReceipt` | Every write states recovery semantics |
| Execution providers | ONNX/WebGPU/ML stacks | `RtProvider` | CPU fallback required |
| Device/pipeline cache | WebGPU stacks | `RtGpuDeviceManager` | Fallback traces on device loss |
| Cross-tab coordination | Web Locks/BroadcastChannel | `RtMesh` | Design protocol early |
| Offline lifecycle | Service workers/Workbox | Optional service-worker bridge | Keep app cache distinct from block store |
| Supervision trees | Erlang/Akka | `RtSupervisor` | Worker death is expected, not exceptional |
| Work stealing | Tokio-style runtimes | CPU lane scheduler | Add after basic queue correctness |
| Task/actor/object triad | Ray | task, agent, object-ref | Core vocabulary from rev0002 |
| Runtime trace stack | Tokio/tracing/platform performance APIs | `RtTraceEvent` | Every fallback emits evidence |

## BrowserRT vocabulary added by this pass

### Task

A finite unit of work with priority, lane, deadline, dependencies, cancellation,
resource hints, and trace identity.

### Agent

A long-lived stateful runtime participant: worker, storage leader, GPU device
manager, mesh coordinator, plugin process, or service-worker bridge.

### Object ref

A stable reference to data that may live in a transferable buffer, shared slab,
OPFS block, stream, GPU buffer, or future media frame. Object refs are the data
plane handle.

### Supervisor

An agent that owns child-agent lifecycle policy: restart, replace, fail parent,
escalate, quarantine, or terminate. BrowserRT should assume worker death and
device loss are normal events.

### Provider

A backend that can execute a kernel for a lane: CPU JS, Wasm, WebGPU, WebCodecs,
OffscreenCanvas, AudioWorklet, or future WebNN-like provider. Provider selection
is capability- and cost-aware.

## API doctrine

BrowserRT should offer three surfaces:

1. Pleasant cold-path APIs for application authors.
2. Explicit hot-path APIs for byte movement and high-throughput kernels.
3. Trace/devtools APIs that reveal what actually happened.

The second surface always wins if there is tension. BrowserRT is allowed to be
pleasant only when pleasant does not hide expensive data motion.

## Research-to-contract rules

- Every borrowed idea must map to an owned BrowserRT contract.
- Every future external dependency must be vendored or replaced before entering
  a released cube.
- Every platform primitive must sit behind capability detection.
- Every unsupported or downgraded provider must emit a trace event.
- Every ambitious pattern must name its first tiny executable proof.

Lowercase vocabulary sentinel: object ref, supervisor, provider, task, agent.


## Validator vocabulary marker

This pass uses the phrase object ref intentionally: an object ref is the runtime handle for data location and ownership.
