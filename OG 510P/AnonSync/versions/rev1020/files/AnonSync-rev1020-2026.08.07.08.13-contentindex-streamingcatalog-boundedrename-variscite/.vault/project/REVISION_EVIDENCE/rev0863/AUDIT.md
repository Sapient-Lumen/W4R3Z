# Rev0863 audit

## Question

Does rev0862's transaction-wide SQLite execution budget also bound lock waiting,
and does the retained busy-handler owner enforce one operation-wide allowance?

## Finding: progress authority cannot run while blocked

The progress handler bounds cooperative virtual-machine work and elapsed checks
at callback opportunities. A connection waiting on another connection's lock
has no such opportunity. Checkpoint-sidecar hydration therefore still had an
unowned amplification dimension around transaction begin, statements, commit,
and rollback.

Rev0863 adds a separate purpose-specific busy owner. It freezes the same exact
serialized connection generation and remains older than the transaction guard,
so cleanup retains the callback it may need. The progress owner remains younger
and is revoked before commit or rollback.

## Finding: the generic timeout renewed across locking events

SQLite resets the busy callback's prior-invocation count for each distinct
locking event. The former owner tracked elapsed time from each reset, granting a
fresh timeout to later events. It also made policy depend on scheduler-sensitive
wall time rather than exact callback-granted sleep.

The owner now tracks one monotone cumulative requested-sleep value. It consumes
that authority before calling `sqlite3_sleep()` and refuses every later event
once the owner-lifetime maximum is reached. The value reported by
`sqlite3_sleep()` is retained separately as diagnostic evidence.

## Finding: typed translation must remain evidence-driven

SQLite may skip the busy handler to avoid deadlock. Therefore a generic
`SQLITE_BUSY` is not proof that AnonSync's wait budget was exhausted. The
sidecar adapter translates only when the retained callback set its sticky
exhaustion flag; otherwise the native SQLite error remains the evidence.

## Finding: zero is policy, not invalid input

A zero lock-wait allowance is a useful fail-fast policy and is intentionally
independent of positive VM progress and elapsed limits. The public validator
admits zero, rejects values above the reviewed 60-second ceiling, and maps only
the lock dimension into the new owner.

## Finding: lexical audit brittleness caused a false registry failure

The first uninterrupted run failed one source audit because it searched for the
obsolete literal `Zero lock wait`; the reviewed public contract says `Zero is
valid` and `fail fast on the first lock conflict`. The audit now binds those
actual semantic markers. This was an audit defect, not a suppressed test.

## Finding: sanitizer coverage stopped at the top-level owner

The generated sanitizer command graph showed four uninstrumented compiles: the
expected bundled SQLite C amalgamation and three first-party C++ files in the
mutex/affinity dependency library. That library owns process/thread validation,
SQLite mutex entry/leave, and the narrow busy-timeout mutation fence.

Rev0863 adds `anonsync_sqlite_database_mutex_guard` to the sanitizer compile set
and makes the busy-owner audit require it. The final selected graph contains 89
first-party C++ compile commands, all instrumented, plus three instrumented
executable link commands. The one uninstrumented C compile is the explicitly
nonclaimed bundled SQLite amalgamation.

## Refactor result

The sidecar integration coordinates two narrow capabilities instead of treating
a timeout number as ambient policy. Output cardinality/bytes, cooperative VM
work, elapsed checks, and lock waiting are separate dimensions. Exact-generation
checks, sticky typed evidence, cleanup order, revocation, and publication are
owned by focused types rather than repeated raw callback code.

## Mechanical evidence

- generic busy-owner runtime: 47/47;
- sidecar lock/execution runtime: 45/45;
- integrated domain model: 611/611;
- generic busy-owner structural audit: 41/41;
- sidecar structural audit: 105/105;
- uninterrupted registry: 162/162, including 49/49 audits;
- exact active-source replay: 311/311 files, 13 intended changes, no mismatch;
- ordinary focused repeats: 100/100 each;
- ordinary audit repeats: 100/100 each;
- Clang 17 `-Werror` runtime: 47/47, 45/45, 611/611;
- GCC ASan+UBSan runtime: 47/47, 45/45, 611/611, plus 25 repeats each.

## Residual risk

Requested sleep is not wall-clock time. Scheduler latency, deadlock-bypass
behavior, filesystem and device I/O, and SQLite operations outside these two
sidecar paths remain separate obligations. The busy handler is cooperative and
per connection; it is not a global lock scheduler or a hard deadline.
