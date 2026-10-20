# ADR 0141: Keep synchronization pressure off the transport pump

Date: 2026-08-24

Status: accepted

## Context

IoTox already moves synchronization filesystem verification and file-offer construction to a bounded
worker outside the toxcore owner callback. A live two-guest worker-pressure gate nevertheless exposed
three indirect waits on that work. `sync-status` took the publisher replay mutex for an exact
statistics snapshot. Periodic best-effort Ratox servicing waited on the shared authority-effect
mutex. The synchronization file-event hook took that authority mutex even for transport events that
could not have a synchronization file effect.

Each wait looked locally reasonable, but toxcore has one event owner. Holding that owner behind a
long object verification prevented it from observing the next lossless synchronization request, so
the configured queue bound could neither admit nor refuse work promptly. This is also a latency risk
for terminal traffic sharing the process.

## Decision

The transport event pump must not wait for synchronization publisher work unless the current event
itself has a required synchronization effect.

- Publisher status uses a nonblocking snapshot. When the replay mutex is held, `sync-status` reports
  `publisher-busy=1`, zeroes only unavailable publisher fields, and still reports independent worker
  and subscriber counters.
- Periodic Ratox servicing attempts the authority-effect mutex without waiting. A missed iteration
  performs no Ratox effect and therefore preserves the existing total order; the next event-loop
  iteration retries it.
- The synchronization file-event hook rejects unrelated events before authority serialization. A
  file offer or an event already associated with a synchronization receive retains the full session,
  authority, epoch, and transfer checks.
- The worker queue stays bounded and non-evicting. Saturated admission returns
  `resource_exhausted`; no existing job, terminal result, or higher-priority terminal lane is displaced.
  Because a response can be unavailable at the instant of overload, recovery is an exact retained
  request retry after capacity returns, not an implicit widening of the queue.

## Consequences

The direct-UDP and forced-TCP `sync-tree-pressure` cells hold one real cross-process namespace
transaction, fill a queue of one behind the active job, require one additional namespace request to
be refused, then release the transaction and converge both retained namespaces by exact retry. The
event pump remains live enough to expose saturation and recovery on both carriers.

Status is deliberately observational rather than perfectly simultaneous while the publisher is busy.
The explicit busy bit is more truthful than blocking every status field behind the effect being
measured. Terminal work retains its separately bounded priority queue and is not reclassified as bulk
synchronization work.

This does not prove a peak resident-memory bound, namespace byte/object quota behavior, arbitrary
kernel scheduling, fleet contention, multiple publishers, or multi-source convergence. It does not
grant lossy retry semantics to signed control records and does not make synchronization a priority
transport lane.
