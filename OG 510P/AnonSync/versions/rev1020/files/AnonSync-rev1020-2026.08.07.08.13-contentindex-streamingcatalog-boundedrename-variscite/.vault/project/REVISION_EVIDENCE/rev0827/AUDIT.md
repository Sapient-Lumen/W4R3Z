# Rev0827 audit — neutral process proof, anti-fabrication correction, mandatory audits

## Heart of the correction

AnonSync repeatedly treats an observation as authority only after the owner of an
invariant verifies it. The process-incarnation value is one such proof: it binds a
live process and ordinary-fork lineage to capabilities that must not survive into a
child. It was therefore architecturally wrong for generic filesystem publication to
depend on a SQLite-branded type and target.

Rev0827 extracts that owner into `anonsync_process_incarnation`, which depends only
on `Threads`. Atomic filesystem publication now consumes the neutral owner directly;
SQLite users consume the same proof without owning its namespace. Retired
`sync_sqlite_process_incarnation*` files and `SyncSqliteProcessId` have zero active
production call sites.

## The severe first-pass flaw found and removed

The first strong-type draft used a private integer constructor but remained trivially
copyable and exactly `uint64_t`-sized. That blocked ordinary conversion but still
allowed a standards-conforming `std::bit_cast<uint64_t -> proof>`. In other words, the
new spelling looked typed while arbitrary bits could still become a value through a
well-defined public operation.

The sealed implementation makes the public proof non-trivially-copyable, asserts that
property, and retains only internal lock-free raw `uint64_t` atomics where fork hooks
and SQLite lifecycle locks need representation-level storage. The public type remains
standard-layout, copyable in ordinary C++ use, eight bytes, equality-comparable, and
not constructible or convertible from `uint64_t`. Compile reproducers bind both the
raw-conversion rejection and the `std::bit_cast` rejection.

This is accidental domain separation, not cryptographic unforgeability. Code already
executing inside the process can include internal headers, corrupt memory, invoke UB,
or otherwise defeat a C++ type boundary. No stronger claim is made.

## Audit-gate repair

Rev0826 advertised 110 CTests but left valuable source audits outside the gate. Its
SQLite mutex capability audit was unregistered and stale: running the exact parent
script returned 60/64. The owner-generation audit passed 27/27 in the parent but was
also unregistered, so future drift could not fail CTest.

Rev0827 repairs the mutex audit for the tri-state authority path and registers three
obligations: the new process-incarnation audit, mutex-capability audit, and
owner-generation audit. The package verifier now requires the owner-generation script
as well. The inventory is 113 tests, a net increase of three after accounting for the
renamed process test.

Final focused structural results:

- process incarnation: **24/24**;
- SQLite process authority: **87/87**;
- SQLite mutex capability: **64/64**;
- atomic file publication: **39/39**;
- SQLite owner generation: **27/27**;
- aggregate: **241/241**.

## Runtime and compiler proof surface

- GCC 14 Debug affected graph rebuilt and final dependency closure reported no work.
- One uninterrupted final CTest invocation passed **113/113**.
- The final focused CTest lane passed **10/10**.
- Four fork/publication executables passed **20 consecutive iterations each**
  (**80 executions**).
- Direct checks: process incarnation **23/23**, prepared publication **27/27**, and
  SQLite connection authority **133/133**.
- Clang 17 with `-Werror` passed the final focused graph **9/9**.
- GCC 14 ASan/UBSan passed the final focused runtime graph **5/5**, with
  `detect_leaks=1`; bundled SQLite remained deliberately uninstrumented.
- The source patch replays exactly to **190/190** active files.

## Remaining boundary

`pthread_atfork` establishes the ordinary `fork()` lineage used here. `_Fork()`,
`vfork()`, raw clone-style creation, or other routes that bypass the registered child
hook are outside the proof. A child created that way must exec before re-entering
AnonSync. The project also does not claim that arbitrary post-fork C++ execution in a
multithreaded child is generally async-signal-safe.
