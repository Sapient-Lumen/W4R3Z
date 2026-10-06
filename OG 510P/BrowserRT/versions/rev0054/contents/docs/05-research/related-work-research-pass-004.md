# Related work research pass 004 — durable actors, ring buffers, simulation, and browser Worker proof

Revision: rev0028

This pass looks past browser helper libraries and studies systems that behave like runtimes: durable workflows, virtual actors, supervision trees, reconciler loops, low-latency ring buffers, trace systems, deterministic simulation, chaos/history checking, and metamorphic testing.

No external code is imported. Source titles and families are recorded in `artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json`; raw external URLs stay out of the cube.

## Steal: durable execution without pretending the browser is a server

Temporal's interesting lesson is not that BrowserRT should become a hosted workflow service. The steal is the vocabulary: a job can be durable, signalable, queryable, retryable, and resumable only if the runtime separates event history from execution side effects.

BrowserRT implication:

- future long jobs should emit resumable trace/history records;
- timers, retries, signals, and cancellation should be named task features;
- idempotency must be documented at the kernel contract layer;
- replay is not a devtools afterthought, it is a runtime design axis.

Non-claim: rev0025 does not implement durable execution.

## Steal: virtual actors as logical handles, not worker instances

Orleans grains suggest a future BrowserRT agent model where the application talks to a logical agent identity while the runtime activates, deactivates, restarts, migrates, or rehydrates the underlying worker.

BrowserRT implication:

```txt
agent identity != worker process/thread instance
object ref      != JS object
actor state     != hot memory only
```

This matters for mesh, OPFS-backed state, and cross-tab coordination. We should keep `WorkerAgent` small now, but the docs should preserve room for a future logical `AgentRef` abstraction.

## Steal: supervision must decorate work, not pollute work

Akka/Erlang-style supervision reinforces a separation already present in the cube: business operations run in agents; restart/stop/escalate policy lives in supervisors. BrowserRT should avoid adding retry policy directly to every kernel body.

Future supervisor policy vocabulary:

- `restart`;
- `stop`;
- `escalate`;
- `replace-provider`;
- `degrade-capability-tier`;
- `open-circuit`;
- `reconcile-desired-state`.

## Steal: reconcilers beat ad hoc repair

Kubernetes controllers are control loops that move actual state toward desired state. BrowserRT will need this once it grows beyond one worker:

```txt
Desired: storage compactor active in exactly one same-origin agent
Actual:  no tab currently owns compaction
Action:  acquire Web Lock and start maintenance lane
```

This is a much better mental model than scattered repair callbacks.

## Steal: the Disruptor's sequenced ring pressure

LMAX Disruptor pushes a strong hot-path lesson: a ring is not just a queue. It is a sequenced data structure with explicit producer and consumer cursors. The future SAB mailbox should have cursors, wraparound rules, backpressure, overwrite policy, and traceable sequence gaps.

BrowserRT implication:

- no vague `sendFast` API;
- name the sequence counters;
- name producer/consumer ownership;
- trace queue depth and cursor lag;
- test wraparound before performance claims.

## Steal: OpenTelemetry's span tree without the dependency

BrowserRT already has a tiny trace log. OpenTelemetry reinforces a future structure:

```txt
trace
  span: task
    span: worker call
      event: transfer buffer
      event: result
```

The cube should eventually define semantic attributes for `rt.lane`, `rt.agent.id`, `rt.object_ref.kind`, `rt.bytes`, `rt.priority`, `rt.deadline_ms`, and `rt.provider`.

## Steal: FoundationDB-style deterministic simulation

FoundationDB's simulation story is the strongest warning against browser-runtime integration soup. BrowserRT will eventually have workers, time, storage, channels, mesh, failure, quotas, and providers. Testing that only in real browsers will be too slow and too nondeterministic.

Future BrowserRT simulator idea:

```txt
fake clock
fake agents
fake object store
fake storage provider
fake GPU provider
seeded scheduler
fault injector
history checker
```

The browser probes remain necessary, but a simulator should catch most logic bugs before launching Chromium.

## Steal: Jepsen history checking for BrowserRT chaos

A BrowserRT chaos test should not merely say "it passed." It should write a history:

```txt
operation: enqueue task
fault: kill worker
operation: cancel task
observation: result rejected
checker: no cancelled task completed after cancel acknowledgement
```

This makes chaos tests reproducible and reviewable inside the datacube.

## Steal: metamorphic testing for scheduler and queue invariants

CockroachDB's metamorphic testing pressure maps nicely onto BrowserRT. Generate legal variations and assert invariant preservation:

- capacity 1/2/8 bounded channels;
- overflow `drop-oldest`, `drop-newest`, `fail`, `wait`;
- priorities reordered where dependencies permit;
- transferable vs clone fallback;
- worker count 1 vs N;
- fake CPU provider vs browser Worker provider.

The invariant is not identical timing. The invariant is semantic safety.

## How rev0025 uses this research immediately

The executable slice for this revision is intentionally humble: a browser module Worker agent proof. It validates that the same agent runtime can run in a real browser Worker, receive a BRT1-style call, process a transferred `ArrayBuffer`, detach sender ownership, return a result, and emit trace evidence.

This is a small piece of the large runtime dream, but it is in the right direction: every ambitious runtime noun must become a named primitive, provider, trace event, manifest task, and proof artifact.
