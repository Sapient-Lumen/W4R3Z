# ADR 0181: Qualify new admission during active route loss

Status: accepted over direct UDP and forced TCP, 2026-08-26.

## Context

ADR 0180 proved that four already-admitted jobs can leave one failed bulk carrier together and
converge through the survivor. It did not prove the degraded scheduler can accept work that did not
exist before the fault. A scheduler could therefore pass population loss while closing admission,
using a stale two-route view, over-debiting the survivor, or reviving work on the stopped
incarnation.

The first new fixture run also exposed a shutdown-order dependency in the auxiliary supervisor. Its
event and carrier-service threads shared one stop flag. Clean Agent shutdown could let the event
consumer exit while a synchronous carrier command was still waiting for toxcore's owner thread to
publish a required event. The carrier then waited for the owner, the owner waited for event queue
space, and no consumer remained. This was the ADR 0180 liveness cycle in reverse.

## Decision

Auxiliary shutdown is two phase. A distinct carrier-stop flag first prevents new synchronous
carrier commands. The carrier thread joins while the ordered event consumer remains live and drains
required toxcore events. Only then does the supervisor stop and join the event consumer, followed by
the transfer managers and transports. An event-thread failure requests both stops; normal carrier
quiescence does not falsely mark the still-draining supervisor stopped.

The Sandwurm fixture also treats startup readiness as a successful correlated local-control status
round trip from a live, non-zombie daemon PID. A stale control-socket pathname can no longer make a
rejected restart look ready. The qualification fault uses the CLI's minimum valid one-millisecond
post-threshold delay; zero is not passed through the public option.

Add `sync-tree-route-loss-admission`. Under fixed selection it starts two independent two-object
pulls on the first four-job bulk route and consumes four signed work units. After at least 65,536
aggregate receive bytes plus one millisecond, that exact worker stops. Both jobs must be remembered,
fenced, and reassigned to the sole ready survivor. Only after the loss and both reassignments are
observed does the fixture start two more signed pulls. Acceptance requires both new jobs to select
the survivor while exactly one bulk route is ready, followed by all four activations, one bounded
recovery, six fixed selections, stale-terminal fencing, and work four-to-zero. Forty protected
Ratox samples remain below 250 ms.

## Consequences

- Degraded admission is now live-qualified rather than inferred from pre-fault migration.
- New and migrated work share the same complete-work capacity check; the stopped incarnation is
  never eligible merely because its signed member record still exists.
- Route recovery remains delayed until every remembered affected job is terminal. Late jobs may
  finish on the survivor without authorizing or delaying stale work revival.
- Clean restart can no longer stop the only required-event consumer ahead of synchronous carrier
  quiescence.
- Sync framing, signed route inventory, route binding, primary authority, HEAD-last acceptance, and
  activation are unchanged.
- This is one deterministic two-before/two-after row. It does not prove daemon cold startup while a
  route is absent, randomized fault timing, larger-object fairness, physical common-link priority,
  independent relay diversity, or long-running production recovery policy.

## Qualification

Binary `db64c1eb64ba0896690f12910b5af6fcee85ec66ef6c3fbb133a275d8fac2fbc`
passes strict raw and compact verification in both two-Sandwurm-guest cells.

- Direct UDP `pair.v3qc2kld`: 29,259 ms, fault at 135,729 bytes, two affected jobs, two
  reassignments, two late admissions on the sole survivor, four stale terminals, one recovery, four
  activations, and protected Ratox p50/p95/max 15.860/19.149/19.980 ms.
- Forced TCP `pair.djhqe3we`: 94,046 ms, fault at 67,179 bytes, the same exact logical counts, and
  protected Ratox p50/p95/max 89.293/95.741/103.416 ms.

Both compact exports allocate 245,760 bytes and exclude guest disks, private identities, bootstrap
secrets, and mutable runtime state. The ordinary 30-entry CTest lane, all 45 Clang ASan+UBSan
entries, and all 45 GCC ThreadSanitizer entries pass; the five private-cgroup capability routes are
explicit skips in each applicable lane. Exact proof hashes and rejected-run interpretation live in
`evidence/2026-08-26-sandwurm-sync-route-loss-admission.md`.
