# Linux process-resource series and peak-envelope audit — rev1017

## Product question

AnonSync's first supported workflow is Linux/headless synchronization of large
media trees measured in terabytes. Delta transfer and selective synchronization
are mandatory, but the product also needs a defensible memory boundary when
several one-process-per-share services run continuously. Rev1016 exposed one
strict Linux process-resource snapshot and one bounded multi-share aggregate.
That single instant could not answer the practical question: **what was the
largest observed footprint while a real workload was running?**

Rev1017 adds a bounded diagnostic time series over the existing owner-only
`resources\n` request. It does not create another daemon protocol, another
resource observer, or any synchronization authority. The command repeatedly
uses the already released per-process snapshot, keeps a compact aggregate point
per sample and one envelope per process, and rejects process replacement rather
than silently joining observations from different lifetimes.

## Shipping command and frontiers

The shipping command is:

```text
anonsync_sync resources-watch \
  --socket /run/user/1000/anonsync/share-a.status.sock \
  --socket /run/user/1000/anonsync/share-b.status.sock \
  --samples 120 \
  --interval-milliseconds 1000 \
  --timeout-milliseconds 180000
```

The response schema is:

```text
anonsync.local-process-resources.series.v1
```

The command accepts:

- one through 256 distinct private socket pathnames;
- two through 1,024 sample rounds;
- a 1 millisecond through 1 hour interval; and
- one total deadline of at most 24 hours.

The final scheduled sample must fit strictly before the requested deadline.
The schedule is anchored to command start rather than chained to the previous
round's completion. Each point records its scheduled offset, actual start and
completion offsets, schedule lag, round sample span, and checked aggregate
resource totals.

## Retained-memory shape

The implementation retains:

- one exact first and last snapshot for each process;
- one fixed-width observed-peak envelope and cumulative-usage baseline for each
  process; and
- one compact aggregate point for each requested round.

It deliberately does not retain every process response for every round. The
retained shape is therefore O(processes + samples), not O(processes × samples).
With the released frontiers, a 256-process, 1,024-sample request keeps 256
process envelopes and 1,024 aggregate points rather than 262,144 full JSON
responses.

The command reports first totals, last totals, element-wise observed aggregate
peaks, cumulative `getrusage` deltas, maximum schedule lag, maximum round sample
span, and per-process envelopes. The word “peak” means **largest sampled
value**. A transient that begins and ends between sample points can be missed.
`ru_maxrss` remains the kernel's lifetime process peak, while the other
observed peaks are point samples.

## Identity, arithmetic, and one deadline

Socket selection, checked aggregation, deadline handling, and round sampling are
shared with the released one-shot `resources` command. The refactor removes a
second copy of path deduplication and resource arithmetic rather than allowing
the one-shot and series semantics to drift.

The first round records each process identity as the peer-bound PID combined
with `/proc/self/stat` start-time clock ticks. Every later round must return the
same ordered identity for the same socket. A process restart, socket alias
change, or replacement fails the complete series. The command never splices a
new process lifetime into an old envelope.

One steady-clock deadline governs all waits and all socket observations. The
timeout does not multiply by process count or sample count. The fixed schedule
also receives a preflight check so an impossible final sample is rejected before
any resource request is sent.

## Runtime proof

The real-process regression starts two independent resource fixtures. One begins
with a touched 48 MiB anonymous reservation. During a 16-point, 75 millisecond
series, a trigger causes the second fixture to touch another 48 MiB. The runtime
proof requires:

- the aggregate and process envelopes to observe at least a 40 MiB rise in
  `Pss_Anon` and private resident memory;
- exact fixed schedule offsets and monotonic point completion;
- exact first, last, peak, and cumulative-delta relationships;
- no full per-process response matrix inside compact points;
- same-live-process alias rejection in both one-shot and series commands;
- fail-closed rejection when one synthetic socket changes its process start
  identity between rounds;
- one total deadline across multiple delayed sockets;
- impossible-schedule rejection before sampling; and
- ordinary status remaining unchanged and procfs-cold.

The focused Linux observer regression remains 45 checks. The expanded
real-process regression passes 246 checks.

## Adjacent audit and refactor

The first fixture revision queried `_SC_PAGESIZE` after a successful `mmap`.
Although page-size failure is unlikely on Linux, that order left a constructor
exception window in which the newly mapped region had not yet entered an RAII
object and could leak. Rev1017 queries and validates the page size first, then
maps and touches the reservation.

The command implementation also centralizes socket selection, checked totals,
identity proof, round sampling, and deadline arithmetic. The released one-shot
response keeps its exact v1 schema and semantics while using the same boundary
as the new series.

During validation, transient cloudtainer remounts removed unsealed source and
build trees. Those interrupted trees and their results are excluded. The exact
reviewed source is reconstructed from the sealed rev1016 parent, committed in a
hidden authority, and persisted as a Git bundle outside the working tree before
release sealing.

## Nonclaims and next measurement

Rev1017 is diagnostic-only. It does not change readiness, scheduling,
admission, transfer budgets, retention, selective synchronization, garbage
collection, or filesystem authority. It does not attribute page cache to a
share, expose allocator arena fragmentation, measure cgroup memory pressure or
PSI, pause targets for an atomic global cutpoint, sample Android, or guarantee
that a transient between points is visible.

Most importantly, rev1017 does **not** prove that a multi-terabyte workload fits
a particular budget. It supplies a bounded peak-series seam so the next
cloudtainer experiment can run multiple real `anonsync_sync run` services over
sparse multi-terabyte fixtures and measure cold startup, manifest recovery,
content-defined reuse, network transfer, repair scans, selective hydration,
restart replay, and controlled ENOSPC. The results should decide whether the
one-process-per-share model is acceptable before AnonSync spends another
revision on a global index or multi-share supervisor.

After that measurement, product priority should return to identity-preserving
rename/move, complete directory and empty-directory semantics, human conflict
handling, selective-sync operator surfaces, and best-effort retention
collection. Linux remains the supported platform direction; Android remains a
worthy but unproved adapter target. Direct TCP, Tor, and I2P remain first-class
routes whose live qualification still requires the eventual CLI environment.
