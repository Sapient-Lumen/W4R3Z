# SQLite connection-authority test synchronization audit — rev0888

## Mission connection

AnonSync treats validation output as evidence, not authority. That distinction
requires the validation machinery itself to be bounded and truthful: a test
harness race must not masquerade as a production deadlock, and an occasional
rerun must not erase the first contradictory observation.

During the rev0888 complete registered-test invocation,
`anonsync_sqlite_connection_authority_test` exceeded its 15-second CTest limit.
The same binary immediately passed alone in about two tenths of a second. This
was not accepted as harmless load noise. The timed-out path was audited before
release.

## Root cause

`PolicyRetirementMutexProbe` owns a worker that checks whether a retired
SQLite authorizer context is destroyed outside the exact connection mutex. A
context deleter publishes a monotonically increasing request ticket, notifies
the worker, then waits until the worker publishes the corresponding completed
ticket.

The old worker began with:

```cpp
std::uint64_t observed = request_.load(...);
request_.wait(observed, ...);
```

If the deleter published ticket one before the new thread performed its first
load, the worker copied `1` into `observed` and waited for the atomic to change
away from the already-published request. The notify associated with ticket one
had already happened. No second request was required to occur, so the deleter
and test could block indefinitely.

This is a test synchronization defect, not evidence that the SQLite owner held
the mutex forever. It nevertheless invalidated the affected validation run and
consumed the full external timeout.

The C++ atomic waiting rules make the predicate error explicit: waiting is
value-based, and a wait may block while the atomic still equals the supplied old
value. Notification is not a durable queued event that compensates for choosing
the wrong baseline. Primary current draft reference:

- <https://eel.is/c++draft/thread#atomics.wait>

## Correction

The worker now starts from the last **completed** ticket, initially zero. On
each loop it:

1. loads the current requested ticket;
2. exits if teardown is requested;
3. waits only when requested equals completed;
4. otherwise performs the exact SQLite mutex probe;
5. publishes the requested ticket as completed; and
6. advances its private completed frontier.

A request published before worker startup is therefore work to process, not a
value to copy into the wait predicate. The ordinary race between the predicate
check and `atomic::wait` is also safe: if the request changes before the call,
`wait(old)` observes that the value no longer equals `old` and returns without
blocking.

## Deterministic regression

The probe constructor now has a test-only initial-ticket parameter. The new
regression constructs it with request ticket one already present before
`std::thread` can enter the worker function. The worker must complete ticket one
and observe `SQLITE_OK` within a bounded local cutpoint.

This schedule deterministically deadlocks the retired implementation; it does
not depend on winning a startup race by chance. The existing 15-second external
CTest timeout remains as a final containment boundary, not as the primary test
oracle.

`audit_sqlite_mutex_capability.py` now inventories both the completed-ticket
state machine and the deterministic pre-start request case. The audit remains
lexical hygiene and does not prove C++ memory ordering or SQLite mutex behavior.

## Runtime evidence

The corrected binary passed its direct run with 155 checks. It then passed 200
consecutive process executions with 31,000 checks. The complete registered suite
is rerun from the corrected source; the original timed-out invocation remains in
the revision evidence as the observation that triggered this correction rather
than being silently replaced.

## Refactor and waste correction

The fix removes a startup handshake assumption that the class never actually
owned. It does not add sleeps, retry loops, or a larger global timeout. The
worker state is now expressed in the same ticket domain as the waiting deleter:
requested work versus completed work.

This is both less wasteful and more exact:

- no full 15-second delay is required to discover the former race;
- no scheduler-dependent notification is treated as persistent state;
- the regression forces the old failure schedule directly; and
- the external timeout remains available for genuinely unknown deadlocks.

## Nonclaims

This correction does not prove that every AnonSync concurrency test is
race-free, that `std::atomic::wait` is implemented without operating-system
bugs, that SQLite mutex ownership is formally verified, or that a passing test
can replace production crash and concurrency evidence. It corrects one concrete
validation race and makes its former schedule executable.
