# Killer demos that should shape BrowserRT

The demos are pressure tests for the runtime contract.

## 1. Jank Guillotine

A visible animation, text input, and slider run beside a heavy workload. The bad
mode freezes the page. BrowserRT mode keeps input responsive through workers,
bounded queues, and traceable backpressure.

## 2. Pipeline MRI

A visual task graph shows throughput, queue depth, resource lanes, worker
utilization, memory, storage, and fallback events.

## 3. Tab Swarm

Multiple same-origin tabs coordinate through future mesh primitives. A visible
tab gets interactive priority while hidden tabs can do maintenance if allowed.

## 4. Chaos Lab

The demo kills workers, cancels jobs, fills queues, simulates storage pressure,
disables GPU, and reloads mid-job. BrowserRT should recover, roll back, or emit
a clear failure trace.

## 5. Runtime Replay

A workload generates a trace that can be saved and replayed enough to debug task
ordering, fallbacks, and failures.
