# Linux process-resource snapshot and multi-share aggregate audit — rev1016

## Product question

AnonSync's first supported workflow is Linux/headless synchronization of large
media trees measured in terabytes. Delta transfer and selective synchronization
are mandatory, but they are not sufficient if several continuously running
shares consume unpredictable memory. Rev1015 proved one bounded source-manifest
record frontier in isolation. It did not measure the whole process and could
not answer the operator's actual question: **what do the current share daemons
consume together?**

Rev1016 adds an explicit diagnostic observation surface for the existing
one-process-per-share architecture. It does not change synchronization
semantics or create resource authority. Its purpose is to make the next
cloudtainer measurements honest enough to decide whether multi-share process
composition is acceptable or whether a future device-level supervisor is
necessary.

## Retained C++ boundary

The local owner socket accepts the exact read-only request:

```text
resources\n
```

Only that request enters the Linux resource observer. Ordinary `status\n`
continues to return the service owner's already-rendered status bytes and does
not traverse procfs, scan descriptors, query `getrusage`, or advance any
scheduler.

The response schema is:

```text
anonsync.local-process-resources.response.v1
```

It contains one current-process observation:

- process ID and `/proc/self/stat` field-22 start time;
- kernel clock-tick rate and page size;
- one monotonic millisecond sample time;
- `Rss`, `Pss`, `Pss_Anon`, `Pss_File`, `Pss_Shmem`, private/shared resident,
  swap, referenced, anonymous, huge-page, and locked memory fields;
- `getrusage(RUSAGE_SELF)` peak RSS, page faults, filesystem input/output
  operations, and voluntary/involuntary context switches;
- current numeric entries in `/proc/self/fd` and `/proc/self/task`.

The socket client retains the existing local-control protections: absolute
private socket path, private parent, mode `0600`, Unix `SO_PEERCRED`, exact
socket-inode reproof, one bounded response, strict JSON shape, and response PID
matching the connected peer. A PID alone is not used as the aggregate identity;
rev1016 combines the peer-bound PID with the process start time to reject two
socket names served by the same live process.

## Linux observation rules

The observer opens `/proc/self/smaps_rollup` with
`O_RDONLY | O_CLOEXEC | O_NOFOLLOW` and consumes it through one bounded read.
The Linux procfs documentation warns that maps and smaps consistency is only
available when the output is obtained in one read call. `smaps_rollup` provides
one pre-summed mapping and adds the proportional anonymous, file, and shared-
memory fields at substantially lower cost than parsing every VMA.

The parser requires exactly one occurrence of every field it uses, the `kB`
unit, canonical unsigned decimal text, and checked arithmetic. Unknown future
fields remain ignorable. The snapshot frontier is 64 KiB, and a read that fills
that frontier is rejected instead of being treated as complete.

`getrusage` is supplementary rather than a substitute for the current memory
snapshot. On Linux, `ru_maxrss` is peak resident memory in KiB; the fault,
block-I/O, and context-switch fields are cumulative counters. Those counters
are useful for before/after workload comparisons, but they are not byte-precise
disk accounting.

Primary references reviewed for this boundary:

- Linux kernel procfs documentation:
  `https://docs.kernel.org/filesystems/proc.html`
- Linux `smaps_rollup` ABI description:
  `https://docs.kernel.org/admin-guide/abi-testing.html`
- Linux man-pages `getrusage(2)`:
  `https://man7.org/linux/man-pages/man2/getrusage.2.html`

## Aggregate command

The shipping command accepts one through 256 distinct socket pathnames:

```text
anonsync_sync resources \
  --socket /run/user/1000/anonsync/share-a.status.sock \
  --socket /run/user/1000/anonsync/share-b.status.sock \
  --timeout-milliseconds 5000
```

The result schema is:

```text
anonsync.local-process-resources.aggregate.v1
```

It retains every exact per-process response and checked sums for RSS, PSS,
anonymous/file/shared-memory PSS, private resident memory, swap PSS, peak RSS,
open descriptors, and threads. The command applies **one total deadline** to
the complete aggregate. It does not multiply the requested timeout by the
number of sockets.

The output makes three interpretation boundaries explicit:

1. RSS sums double-count shared pages.
2. PSS values use the kernel's proportional share adjustment and are usually
   the more useful cross-process footprint estimate, but they remain sampled
   observations rather than ownership authority.
3. Processes are sampled sequentially; the aggregate is not an atomic global
   cutpoint. `sample_span_milliseconds` reports the observed span.

The measurement is diagnostic-only. It does not change readiness, retention,
transfer budgets, scheduling, admission, eviction, or garbage collection.

## Runtime proof

The focused C++ regression proves strict synthetic `smaps_rollup` parsing,
missing/duplicate/wrong-unit/noncanonical/overflow rejection, live PID and
start-time observation, descriptor and thread accounting, and exact JSON
round-trip validation. The local-socket regression proves the resource request
through the real private socket and proves that mode or parent-permission drift
is rejected.

The real-process regression starts two independent fixture processes. One
process owns two socket aliases; the other touches 48 MiB of private anonymous
memory. It proves:

- the two-process aggregate preserves exact socket and peer identities;
- the touched process reports at least 40 MiB more anonymous PSS and private
  resident memory than the baseline fixture;
- every aggregate sum exactly equals its retained samples;
- two aliases for one process are rejected rather than double-counted;
- one requested timeout governs the aggregate;
- ordinary status remains unchanged after explicit measurement; and
- both private sockets drain and disappear cleanly.

The fixture is deliberately not a fake multi-terabyte result. It isolates the
observer and aggregate semantics before actual share-service measurement.

## Adjacent audit and refactor

The first aggregate implementation applied the timeout independently to every
socket, allowing a 256-socket request to consume up to 256 times the stated
budget. Rev1016 replaces that with one steady-clock deadline and passes only the
remaining budget to each request.

The audit also found an obsolete rev1016 validator compiling a discarded
`/mnt/data` worktree in parallel with the protected source. It was stopped and
excluded from authority. Final validation is rooted only in the frozen
`/home/oai/share` source and its dedicated builds.

The resource renderer is locale-independent, and decimal procfs parsing rejects
multi-digit leading-zero forms. These small constraints prevent ambient locale
or permissive text parsing from turning a diagnostic surface into ambiguous
JSON or identity evidence.

## Nonclaims and next measurements

Rev1016 does **not** prove acceptable memory use for a multi-terabyte share. It
also does not attribute kernel page cache to a particular share, expose malloc
arena fragmentation, measure cgroup pressure or PSI, measure disk amplification,
add an Android adapter, or consolidate shares into one process.

The next workload measurement should run multiple real `anonsync_sync run`
services over sparse large-file trees and record this resource snapshot around:

- cold startup and index recovery;
- source-manifest construction and restart replay;
- content-defined local reuse and network range transfer;
- complete repair scans;
- selective metadata-only convergence and later hydration;
- high-latency direct/Tor/I2P turns; and
- controlled low-disk and ENOSPC events.

If the observed per-share process boundary is acceptable, product priority
should return to identity-preserving rename/move, complete directory semantics,
human conflict handling, and selective-sync user surfaces. A global chunk index
or multi-share daemon should be justified by measured evidence rather than by
another synthetic representation argument.
