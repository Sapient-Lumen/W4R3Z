# Resource lanes and scheduler

BrowserRT schedules by resource lanes, not just by worker count.

## Lanes

- `main`: tiny UI coordination only.
- `interactive`: user-linked small tasks.
- `cpu`: CPU-heavy worker tasks.
- `storage`: OPFS, manifests, journaling, compaction.
- `gpu`: WebGPU dispatch and readback.
- `render`: OffscreenCanvas and frame production.
- `media`: future WebCodecs paths.
- `audio`: future AudioWorklet coordination; not scheduled like generic CPU work.
- `network`: future local/offline network paths.
- `cross-tab`: BroadcastChannel, SharedWorker, Web Locks.
- `maintenance`: cleanup, warming, compaction.

## Scheduler questions

The scheduler must ask:

- what resource is needed;
- what priority applies;
- whether a deadline exists;
- how much memory is required;
- whether storage is backpressured;
- whether GPU upload/readback is worth it;
- whether the task can be cancelled;
- whether a fallback exists;
- which provider can execute the kernel;
- which supervisor owns the agent or task family.

## Priorities

- `critical`
- `user-blocking`
- `user-visible`
- `background`
- `maintenance`

## Admission control

A task may be refused before it starts if capacity, memory, storage, or policy
would make it unsafe. Refusal is better than browser meltdown.

## Scheduler doctrine imported from research

- Use RPC convenience only for cold paths.
- Keep bounded channels as the primitive for pipes and streams.
- Return object refs instead of giant values.
- Keep scheduler statistics as trace events, not private counters.
- Prefer provider selection over feature-specific branches.
- Treat hidden tabs, quota pressure, worker death, and GPU device loss as normal
  scheduler inputs.

## First scheduler proof

The first scheduler proof is not WebGPU or OPFS. It is:

1. a bounded channel;
2. a worker agent;
3. one transferable object ref;
4. wait/run trace events;
5. cancellation;
6. supervisor restart after intentional worker crash.


## Rev0002 refinement

The scheduler now uses the primitive vocabulary in `runtime-primitives.md`:
tasks, actors, objects, channels, lanes, agents, trace, and policy. This keeps
worker-pool thinking from swallowing storage, GPU, mesh, and lifecycle concerns.
