# North-star demos after related-work research

The demos should force BrowserRT to prove boundaries between slices, not just
show isolated APIs.

## D1: Jank Guillotine remains first

Naive mode freezes the UI. BrowserRT mode runs through workers, bounded channels,
transferable buffers, trace events, and cooperative yielding. The demo reports
long tasks, queue depth, throughput, and responsiveness.

## D2: Pipeline MRI becomes the scheduler demo

A visual DAG exercises task graph scheduling, backpressure, resource lanes, and
fallback traces. Toggle SAB, OPFS, GPU, or worker count and observe plan changes.

## D3: Tab Swarm becomes the mesh demo

Multiple same-origin tabs coordinate through locks, broadcasts, and a shared
coordinator. One tab becomes storage leader; visible tabs get priority; hidden
tabs do background maintenance only when allowed.

## D4: Chaos Lab becomes the recovery demo

Kill workers, fill queues, cancel tasks, fake quota pressure, lose GPU device,
reload mid-job, and corrupt a test block. BrowserRT should recover or fail with a
compact trace.

## D5: Runtime Replay becomes the debugging demo

Run a workload, save trace plus buffer hashes plus block refs, reload, and replay
the control plane. Exact deterministic replay is not promised in the baby era;
replay should still shrink failures.

## D6: Local Browser Supercomputer is the audacity demo

A single generated workload uses CPU workers, optional GPU compute, OPFS block
storage, service-worker asset cache, mesh coordination, and devtools telemetry.
It is intentionally too much for early implementation, but it gives the runtime a
north-star integration target.
