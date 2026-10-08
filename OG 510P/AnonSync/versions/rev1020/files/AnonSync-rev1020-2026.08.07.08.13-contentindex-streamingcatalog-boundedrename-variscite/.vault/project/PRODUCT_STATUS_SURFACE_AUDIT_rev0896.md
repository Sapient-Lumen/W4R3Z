# Product status surface audit, rev0896

## Heart of the mission

AnonSync is not a file copier with metadata bolted on. It is an
authority-preserving convergence engine: exact authorized observations become
identity-bearing operations, durable cutpoints decide what can be attempted,
and visible filesystem effects must be explainable from those operations and
live capabilities. Summaries, metrics, and status output are only useful when
they remain subordinate to those exact sources of authority.

## What was missing

Rev0895 made the causal replica stack invokable as a product spine, but it left
a severe operational gap: the executable could act once, yet it could not say
what durable condition it was in. That meant an operator, test harness, or future
daemon loop had to infer health from side effects or private database knowledge.
That is backwards for this project. The product spine needs an owned condition
surface before it can safely grow a scheduler or recovery loop.

## What changed

`anonsync_replica status` now restores the causal SQLite owner and optional
payload/effect/membership owners, then reports:

- causal evidence, active, pending, quarantined, visible path, causal head, and
  missing predecessor counts;
- local counter, local compromise bit, retained canonical bytes, and the four
  main replica digests;
- outbox intent, unclaimed, claimable, live, expired, retry-waiting, dispatch
  attempt, high-water epoch, clock health, anomaly, observation generation, and
  recovery generation counts;
- optional retained payload entry/byte/transient counts and payload snapshot
  digest;
- optional receiver effect generation, staged/published counts, retained payload
  bytes, and effect cutpoint digest; and
- optional membership generation, policy epoch, entry count, chain digest,
  anchor generation, anchor transition sequence, and anchor/current agreement.

## Audit/refactor judgment

The good part is that status uses existing reviewed owners and model restore
logic. It does not mint a second schema contract by issuing raw SQL queries
against private tables. The paired-option helper also prevents half-authorized
reports such as an effect database without its file root or a membership
database without its independent anchor database.

The remaining concern is that this is still a command-line report, not a stable
machine API specification. The field names are intentionally flat for now so the
process proof can pin them, but the next loop should either version the status
schema or make the durable loop consume in-process owner snapshots directly and
use CLI status only as an operator view.

## Waste corrected, and waste still present

Corrected: the product spine now has a read/observe verb. This reduces the
previous tendency to accumulate proof islands without an operator-facing
integration seam.

Still present: the build graph is too broad for narrow product changes. The
final full build succeeded only after resumed invocations because long legacy
compilation units exceed the cloudtainer command window. Over time this should
be corrected by shrinking monolithic units, consolidating micro-libraries that
exist only to satisfy past audit seams, keeping product-spine tests close to the
runtime, and preserving the full scan/oracle tests as release checks rather than
making every edit pay the whole historical cost.

## Severe nonclaims

Status is not recovery, not a daemon, not discovery, not privacy, not GC, and not
an index. It is a necessary cutpoint: future loops can now ask the product what
it durably knows before deciding whether to claim, retry, recover, rotate trust,
or shut down.
