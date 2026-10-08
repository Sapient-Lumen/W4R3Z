# TLS Continuation Affinity Audit — rev0883

## Executive finding

AnonSync's authenticated TLS record continuation is a live shared-state
capability. It is not merely a movable byte-count token. Rev0882 correctly made
one continuation the exclusive owner of an unfinished framed record, but its
no-throw cleanup path did not enforce the same process/thread affinity as
ordinary record I/O. Moving an active continuation to another C++ thread and
letting it destruct there called `poison_noexcept()`, which silently mutated the
shared authenticated-state flags from the foreign thread.

Rev0883 closes that hole. Completion, poisoning, abandonment, active-target
move-assignment, and final `SSL_free()` now pass through one fail-stop owner
fence before mutating or freeing state. A child-process runtime test transfers
an active continuation to a foreign `std::thread`; its destructor must terminate
the child with the exact capability-violation exit code before the stream can
be touched.

This is an execution-affinity correction, not a claim that TLS delivery is
complete. The receiver loop remains missing, OpenSSL WANT states are not owned
by a resumable event loop, and ThreadSanitizer is not claimed.

## Mission fit

The heart of AnonSync is exact authority accounting:

> Exact authorized history owns identity, causality, projection, dispatch,
> retry, receipt, and visible effect. Derived frames, sockets, TLS progress,
> object addresses, thread identifiers, and summaries remain subordinate
> observations.

That principle applies inside one process as well as across replicas. An
unfinished record reservation belongs to the exact authenticated state and the
process/thread incarnation that created it. C++ move syntax may transfer the
wrapper value, but it does not mint new authority to mutate the underlying
OpenSSL object. Cleanup is not exempt: poisoning the stream, clearing its active
reservation, decrementing the shared-state reference count, and eventually
freeing `SSL*` all alter live authority-bearing state.

## The defect inherited from rev0882

The rev0882 state owner already recorded:

- the creating process incarnation;
- the creating thread incarnation;
- the owned `SSL*`;
- whether the stream was poisoned; and
- whether one record write was active.

Ordinary calls reached `validate_or_throw()`, then
`require_current_or_throw()`, before reading or writing through OpenSSL. The
state destructor also checked process and thread affinity before `SSL_free()`.
However, these two no-throw methods did not check affinity:

```cpp
void complete_record_write_noexcept() const noexcept;
void poison_noexcept() const noexcept;
```

`SyncReplicaTlsRecordWriteContinuation::~SyncReplicaTlsRecordWriteContinuation`
called `poison_and_release_noexcept()`, which called `state_->poison_noexcept()`.
Therefore this sequence was possible:

1. thread A authenticated the channel and accepted a complete record prefix;
2. thread A moved the continuation into a `std::thread` closure;
3. thread B destroyed the active continuation without finishing it; and
4. thread B wrote `poisoned_ = true` and `record_write_active_ = false` on the
   shared state without first rejecting foreign-thread ownership.

The code was normally used without a concurrent peer access, so this was not
necessarily a data race in every execution. It was still an authority defect:
the wrong thread was allowed to mutate the owner, and a future caller could
mistake a silently foreign cleanup for an authorized state transition. If that
foreign release became the final `shared_ptr` release, the state destructor
would later fail stopped before `SSL_free()`, but the earlier mutation had
already happened. The fence belonged before the first mutation, not only before
the final free.

## Why cleanup is state mutation

The no-throw path performs security- and framing-relevant work:

- `poisoned_ = true` permanently rejects future channel use;
- `record_write_active_ = false` releases the one-record reservation;
- `state_.reset()` can decrement the last shared owner; and
- destruction of the state can call `SSL_free()`.

OpenSSL's thread-safety documentation says that most OpenSSL objects are not
safe for simultaneous use and that thread safety does not generally permit two
threads to mutate one object concurrently. The relevant object here is not just
the public `SSL*`; the AnonSync wrapper's reservation and poison flags are part
of the same logical stream owner.

`SSL_free()` is also not a trivial pointer release. OpenSSL documents that it
decrements the SSL reference count and, when the count reaches zero, frees the
SSL object and associated buffering BIO, read/write BIOs, cipher lists, and
possibly the session. That operation must remain under the same owner proof as
record progress.

Primary sources:

- OpenSSL 3.5, **OpenSSL thread safety**:
  <https://docs.openssl.org/3.5/man7/openssl-threads/>
- OpenSSL 3.5, **SSL_free**:
  <https://docs.openssl.org/3.5/man3/SSL_free/>
- OpenSSL 3.5, **SSL_write / SSL_write_ex** nonblocking retry semantics:
  <https://docs.openssl.org/3.5/man3/SSL_write/>
- C++ working draft, **`std::thread` constructors**:
  <https://eel.is/c++draft/thread.thread.constr>

These sources support the conservative ownership rule. They do not prove
AnonSync's implementation correct; the compiled process-isolated test remains
the behavioral evidence for the corrected destructor frontier.

## Corrected implementation

### One fail-stop fence

`detail::SyncReplicaTlsAuthenticatedState` now has one private helper:

```cpp
void require_owner_or_fail_stop_noexcept() const noexcept;
```

It performs the checks in this order:

1. exact process incarnation is current, otherwise immediate process-capability
   fail-stop;
2. exact thread incarnation is current, otherwise immediate thread-capability
   fail-stop.

The project intentionally uses the same externally observable fail-stop exit
code for these inherited/live-capability violations. There is no C++ unwinding,
no atexit processing, and no attempt to continue through a potentially corrupt
or foreign owner.

### Fence before first mutation

The helper is called at the beginning of:

- `complete_record_write_noexcept()`;
- `poison_noexcept()`; and
- `release_ssl_noexcept()` when an SSL object is present.

This centralization is both a correction and a refactor. The previous
`release_ssl_noexcept()` duplicated the process/thread checks. A single helper
reduces the risk that future no-throw cleanup paths enforce only part of the
affinity contract.

### Public contract

The continuation header now states that finishing, abandoning, destroying, or
move-assigning an active continuation from another process or thread fails
stopped before it may mutate shared TLS state. Same-owner abandonment continues
to poison the stream because a complete prefix without its exact body is an
unrecoverable framing cutpoint.

The wrapper remains move-only. This revision does not prohibit moving the C++
value. It makes the semantic rule precise: a move does not transfer the
underlying live process/thread authority. A consumer that needs asynchronous
progress must introduce an event-loop owner that creates and advances the
continuation on one stable execution owner, rather than moving the current
synchronous owner between arbitrary threads.

## Runtime proof

The TLS runtime matrix creates a real TLS 1.3 connection, authenticates the
sender side, and begins a nine-byte record continuation in an isolated child
process. It then moves that active continuation into a `std::thread` closure and
allows the closure to return without finishing the body.

The continuation's foreign-thread destructor reaches `poison_noexcept()`. The
child must exit with `kSyncProcessCapabilityViolationExitCode`; returning the
sentinel value or surviving the join fails the test. Running in a child process
is load-bearing because the intended behavior is immediate fail-stop and cannot
be safely asserted inside the test runner itself.

The case supplements, rather than replaces, the existing matrix for successful
finish, overlap rejection, size mismatch, same-owner abandonment, body failure,
blocking socket rejection, non-socket BIO rejection, stale claim, exact release,
retry, and post-prefix ambiguity.

## Validation result

The final rev0883 gates record:

- 192/192 registered tests and 61/61 audit-named tests;
- 5,199/5,199 focused checks under GCC 14 Debug, Clang 17 Release C++
  `-Werror`, and GCC 14 ASan/UBSan with leak detection and bundled SQLite
  instrumented;
- 5,940/5,940 mixed authority stress checks;
- 100/100 TLS stress runs and 7,500/7,500 checks; and
- 509/509 selected lexical checks across 17 audits.

The new runtime case changed the exact inherited-process inventory. Fail-closed
source audits rejected the first full gate until the TLS test's spawn count and
the cross-audit aggregate were updated. The resulting inventory remains one raw
`fork()` owner, 15 inherited-state consumer translation units, 27 inherited
spawn sites, eight fresh-image campaigns, and 35 classified process sites in
all. This discovery failure is retained as audit evidence rather than hidden.

## Failure matrix

| Frontier | Owner observation | Allowed action | Durable / stream result |
|---|---|---|---|
| ordinary read/write validation | current process and current thread | continue to live TLS/session proof | no ownership change |
| ordinary read/write validation | foreign process | fail stopped | no wrapper or OpenSSL state may be inspected/mutated |
| ordinary read/write validation | foreign thread | throw before record I/O | caller retains responsibility; no cleanup mutation yet |
| active continuation finish | current owner | validate exact length, re-prove session/readiness, write body, clear reservation | stream remains usable only after complete body |
| active continuation finish | foreign thread | ordinary proof rejects; catch enters fenced no-throw poison and fails stopped | no foreign mutation |
| active continuation destructor | current owner | poison stream and clear reservation | stream permanently unusable |
| foreign-thread destructor | foreign thread | fail stopped at first no-throw owner fence | no poison/reservation mutation and no `SSL_free()` |
| move-assignment over active target | current owner | poison prior target, then take source | prior target stream unusable; source authority retained by wrapper |
| foreign-thread move-assignment over active target | foreign thread | fail stopped while cleaning target | no foreign mutation and assignment does not proceed |
| authenticated-state final release | current owner | `SSL_free()` | OpenSSL/BIO/session references released |
| authenticated-state final release | foreign process or thread | fail stopped before `SSL_free()` | no foreign OpenSSL teardown |
| empty/moved-from wrapper destruction | any thread | no state access | no effect |

## Audit/refactor of the surrounding cube

### Corrected duplication

The state previously had one explicit affinity implementation for throwing
operations and another inline implementation for final SSL release, while
completion and poisoning had none. Rev0883 does not attempt to merge throwing
and no-throw policy because their error contracts differ. It does centralize all
no-throw fail-stop enforcement in one helper and structurally checks that the
helper precedes mutation/free in each path.

### Rejected receive prototype

During this review, an unrelated **578-line** incremental nonblocking receive
prototype appeared in the mutable workspace. It changed public APIs, introduced
a unified read/write reservation concept, and attempted a larger event-loop
step. Its first clean compile failed, and the branch supplied no matching
runtime cases for its new public behavior or failure frontiers.

The prototype was rejected rather than repaired opportunistically. The final
rev0883 tree was rebuilt from the independently verified rev0882 archive and
contains only the narrow affinity correction, contract, test, audit, and
revision evidence. This is a material waste-control decision: large speculative
state-machine changes must not acquire authority merely because they are present
in a working directory or use plausible vocabulary.

The receive direction is still important. It should return as a separately
owned revision with explicit partial-prefix/body state, exact WANT_READ/WANT_WRITE
semantics, cancellation, peer-close behavior, bounded allocation, stream poison
rules, runtime backpressure, and crash/restart nonclaims.

### Lexical audit boundary

`tools/audit_sync_file_tls_dispatch.py` now inventories:

- the centralized process-then-thread fail-stop helper;
- ordering of the helper before completion, poison, and `SSL_free()` mutation;
- the public foreign-owner cleanup contract;
- the child-process foreign-thread destructor case;
- the rev0883 package/design surface; and
- the online-source, failure-matrix, rejected-scope, and nonclaim record.

These are deterministic source checks, not semantic proof. A matching substring
cannot prove object lifetime, absence of races, OpenSSL behavior, or fail-stop
execution. Compiled runtime, sanitizer lanes, stress, and future race-oriented
validation remain load-bearing.

## What remains severely missing

### Receiver loop remains missing

No production-shaped service owns authenticated input records, reconstructs the
exact receiver request, performs idempotent evidence admission, stages bounded
payload bytes, publishes the visible file effect, and returns a terminal effect
receipt. Sender dispatch hardening cannot substitute for this missing half.

### No resumable nonblocking owner

The current writer requires a complete fixed prefix write while the SQLite guard
is held and then attempts the immutable body synchronously after releasing the
writer. It fails closed on OpenSSL WANT states rather than retaining a durable or
event-loop-owned continuation. There is no body offset, cancellation state,
transfer deadline, heartbeat, or restart recovery.

### No durable post-prefix marker

After the prefix frontier, failure is correctly treated as ambiguous and the
claim remains live. The database still does not record a durable
`dispatch_started` cutpoint or body progress. Process crash therefore leaves
retry policy dependent on lease expiry and receiver idempotency, not resumable
transport state.

### Newer stack is still not the shipped product path

The causal SQLite owner, file-effect owner, authenticated channel, and TLS
composition continue to be strongest in tests and audit targets. The shipped
`anonsync_core` executable has not yet been migrated to one end-to-end replica
service using these owners as its sole durable authority.

### ThreadSanitizer is not claimed

The correction is deterministic affinity enforcement. It is not evidence that
all OpenSSL/wrapper object races are absent. ThreadSanitizer, a model checker, or
a formally specified single-owner event loop has not been run or implemented.
ASan/UBSan cannot establish race freedom.

## Recommended next sequence

1. Define one receive-side framed-record continuation with explicit prefix and
   body offsets, bounded allocation, and a single event-loop execution owner.
2. Prove WANT_READ/WANT_WRITE transitions with socket backpressure and peer
   close at every byte frontier; do not hold SQLite ownership across those
   transitions.
3. Compose exact receiver evidence admission, immutable payload staging,
   atomic publication, directory durability, terminal effect receipt, and
   duplicate replay.
4. Record a durable sender post-prefix state only after defining recovery and
   retry semantics that cannot confuse a partial old stream with a fresh one.
5. Migrate one shipped executable path to the composed sender/receiver service
   before adding more isolated assurance libraries.
6. Add ThreadSanitizer where the OpenSSL/toolchain combination is supportable,
   while retaining process-isolated fail-stop tests as deterministic contract
   evidence.

## Deliberate nonclaims

Rev0883 does not claim:

- that moving an active continuation transfers live thread authority;
- race freedom for arbitrary concurrent access;
- ThreadSanitizer coverage or formal proof;
- resumable OpenSSL WANT_READ/WANT_WRITE progress;
- a receive continuation or receiver loop;
- durable body offset, dispatch-started state, cancellation, or transfer age;
- atomic SQLite-plus-TLS delivery;
- peer receipt or admission from local SSL write completion;
- exactly-once network delivery or remote file effect;
- integration into the shipped executable;
- portable strict socket readiness outside the currently implemented Unix path;
- complete retry/dead-letter, membership, revocation, compaction, rejoin, or
  privacy/anonymity semantics; or
- externally trusted signed build provenance.
