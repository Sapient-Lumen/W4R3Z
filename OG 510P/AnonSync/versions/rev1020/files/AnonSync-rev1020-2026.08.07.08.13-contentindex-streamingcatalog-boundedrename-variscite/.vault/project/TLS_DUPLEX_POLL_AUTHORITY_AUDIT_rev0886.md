# AnonSync rev0886 — duplex TLS poll and release-path authority audit

## Executive finding

Rev0886's incremental TLS continuations made nonblocking `SSL_read_ex()` and
`SSL_write_ex()` resumable, but the cube still left the wait between those
operations to ad hoc callers. That was a material composition gap. A typed WANT
state exposed an advisory descriptor, yet no production leaf owned all of the
following as one bounded decision:

1. the exact pending continuation;
2. the exact readiness direction selected by OpenSSL;
3. a monotonic absolute deadline;
4. target reproof before each kernel wait;
5. interruption and transient poll-resource handling;
6. the post-wakeup authority cutpoint; and
7. the rule that one readiness event may issue at most one OpenSSL operation.

Without that owner, every future event loop would have to reproduce subtle
logic around descriptor reuse, `EINTR`, timeout rounding, stale readiness,
`POLLHUP`, and retry argument identity. Duplication at this boundary would be
especially dangerous because poll readiness is not TLS truth and because a
pending OpenSSL retry may already have consumed internal protocol state.

This revision adds one shared duplex poll owner. It composes the existing exact
read and write continuations without absorbing their authority. The owner waits;
the continuation still owns TLS validation, socket/BIO reproof, retry identity,
framing, close classification, poisoning, and terminal state.

The same release audit found a separate verifier inversion. The old generated-
artifact rule rejected a legitimate evidence basename such as
`build-shape-observation.json` because one path component began with `build-`,
while it did not reject an actual directory named exactly `build/`. The policy
now classifies directory components separately from the final basename and is
covered by an executable positive/negative path matrix.

## Mission relationship

AnonSync's heart is exact authority accounting across crash, retry, transport,
and visible effect. A readiness bit, descriptor integer, relative timeout, or
release verifier heuristic is only an observation. None may manufacture a
stronger conclusion.

For this boundary, the governing statement is:

> One exact pending TLS operation may be retried only by its current owner, on
> its re-proved transport capability, before the caller's absolute scheduling
> cutpoint. Kernel readiness is permission to ask the continuation for one next
> result; it is not evidence of protocol progress, clean closure, peer receipt,
> durable acceptance, or receiver effect.

This keeps three kinds of time and progress separate:

- **kernel readiness** says a system call may not block in the same way now;
- **TLS progress** says what one immediate OpenSSL operation returned; and
- **application authority** advances only when the exact higher-level state
  machine accepts that TLS result at its own cutpoint.

## Defect analysis

### 1. Relative waits can renew authority accidentally

A loop that calls `poll(fd, ..., 50)` again after every `EINTR` or early wakeup
can wait indefinitely under repeated signals or spurious activity. Each retry
silently grants a fresh 50 ms budget. That contradicts a caller that intended a
single bounded scheduling decision.

The new API accepts `std::chrono::steady_clock::time_point`, not a duration.
Every retry recomputes the remaining interval against the original absolute
cutpoint. `steady_clock::is_steady` is compile-time asserted.

### 2. Millisecond conversion can expire too early

Linux `poll()` accepts an integer millisecond timeout. Truncating a positive
sub-millisecond remainder to zero changes a bounded wait into an immediate poll.
That can create a CPU spin and can report deadline expiry before the caller's
actual cutpoint.

The conversion therefore:

- returns zero only when the deadline is already reached;
- rounds a positive fractional millisecond upward;
- clamps intervals above `INT_MAX` milliseconds; and
- treats a zero return from `poll()` as an observation that must be checked
  again against the absolute steady-clock deadline.

The kernel may schedule the thread after the requested timeout. The absolute
clock comparison, not one syscall return, owns expiry.

### 3. An interrupted wait invalidates a cached target

A descriptor number is not authority. A signal handler or concurrent
unsynchronized actor could close, duplicate, replace, or change policy on the
underlying descriptor while `poll()` is interrupted. Reusing the prior
`pollfd` after `EINTR` would skip the continuation's exact socket-lifetime and
nonblocking-policy reproof.

The shared loop discards the target after `EINTR` and the portable `EAGAIN`
resource failure. Its next iteration asks
`pending_readiness_or_throw()` again. That method checks continuation ownership,
WANT state, process/thread affinity, retained BIO identity, descriptor identity,
Linux socket lifetime, and current strict nonblocking policy through the
existing transport state machine.

### 4. Readiness error bits are not protocol outcomes

`POLLERR`, `POLLHUP`, and `POLLNVAL` are wakeup conditions. They do not say that
TLS received a valid `close_notify`, that a record is complete, or that the
connection can be reused. Mapping `POLLHUP` directly to “peer closed” would
accept truncation outside OpenSSL's protocol state. Mapping `POLLNVAL` directly
to a benign retry would conceal descriptor invalidation.

The poll owner treats every nonzero `revents` set as advisory. It invokes at
most one continuation operation. The continuation re-proves the target and lets
OpenSSL distinguish WANT, progress, complete frame, clean close, truncation, or
fatal state. This is intentionally conservative even if the requested POLLIN or
POLLOUT bit is absent and only an error/hangup bit woke the call.

### 5. A readiness loop can hide unbounded TLS work

A helper that polls and then repeatedly calls `advance_or_throw()` until the
continuation reaches WANT or terminal state would combine scheduling and TLS
progress into a hidden loop. One event-loop dispatch could copy an entire large
record, monopolize a thread, and cross several framing or cancellation
cutpoints.

The generic implementation contains exactly one call to
`continuation.advance_or_throw()` on a nonzero wakeup. Fresh write operations
remain capped by `kSyncReplicaTlsRecordWriteStepBytes` (64 KiB), and read
operations retain their existing bounded step. Progress returns to the caller
for the next scheduling decision.

### 6. Read and write policy had started to diverge

An abandoned branch implemented a read-only poll helper. Keeping that shape
would force write-side event-loop code to duplicate timeout conversion,
interruption handling, error-bit semantics, and target reproof. The current
implementation extracts one private typed template for both continuations and
uses exhaustive mapping functions for their distinct public terminal states.

The refactor deliberately does **not** merge socket lifetime with mutable
readiness policy. `SO_COOKIE`/stat/BIO evidence answers which socket lifetime is
present. `O_NONBLOCK` answers whether the current operation may use strict
readiness semantics. The continuation performs the lifetime–policy–lifetime
reproof at every required frontier.

## Public state machines

### Read poll result

`SyncReplicaTlsRecordReadPollProgress` has six states:

- `DeadlineExpired`: no OpenSSL operation was started by this call;
- `Progress`: one bounded read operation advanced framing state;
- `WantRead`: the exact retry remains pending for readable readiness;
- `WantWrite`: the exact retry remains pending for writable readiness;
- `Complete`: one exact frame is ready for extraction; and
- `PeerClosed`: OpenSSL classified a clean close before a partial frame.

### Write poll result

`SyncReplicaTlsRecordWritePollProgress` has five states:

- `DeadlineExpired`: the exact pending write request is unchanged;
- `Progress`: one bounded body operation advanced the application cutpoint;
- `WantRead` or `WantWrite`: the same pointer/length retry remains pending; and
- `Complete`: OpenSSL accepted the complete application record locally.

Write completion remains transport-local. It does not prove that the peer read
the record, durably admitted the operation, published a filesystem effect, or
returned an authenticated terminal receipt.

## Exact algorithm

For either continuation, the owner performs:

1. Ask the continuation for its pending readiness target. This rejects inactive,
   pre-WANT, caller-managed, foreign-owner, stale-BIO, stale-socket, and lost-
   policy states before ordinary timeout can disguise them.
2. Read `steady_clock::now()` and return `DeadlineExpired` if the absolute
   cutpoint has already arrived.
3. Map the typed readiness direction to only `POLLIN` or `POLLOUT`.
4. Round up and clamp the remaining interval for `poll()`.
5. On `EINTR` or `EAGAIN`, discard the target and restart at step 1 with the
   same absolute deadline.
6. On syscall timeout, compare the monotonic clock again. If the cutpoint has
   not arrived, recompute rather than inventing expiry.
7. On a nonzero result, require at least one `revents` bit and recheck the
   absolute cutpoint before spending TLS authority.
8. Invoke exactly one continuation `advance_or_throw()` and exhaustively map its
   typed result.

The post-wakeup deadline check means readiness observed before the deadline does
not authorize an operation begun after it. This is scheduling policy, not a
claim that the subsequent OpenSSL call itself has a wall-clock bound.

## Runtime matrix

The real TLS 1.3 socketpair test now exercises:

- rejection before read WANT without consuming the continuation;
- already-expired and idle read deadlines retaining the exact target;
- one prefix wakeup stopping before body I/O;
- one body wakeup returning an exact frame;
- clean `close_notify` classified by OpenSSL after a poll wakeup;
- a real signal delivered during a bounded poll call, followed by expiry at the
  original deadline and exact target retention;
- rejection before write WANT without consuming the continuation;
- already-expired and saturated idle write deadlines retaining both exact
  target and exact body cutpoint;
- a two-megabyte cooperative nonblocking transfer driven by both read and write
  poll overloads;
- exact peer bytes after completion; and
- proof that every successful write-poll operation advances no more than the
  public 64 KiB write-step budget.

These tests complement, rather than replace, the existing matrices for BIO
replacement, in-place descriptor change, `dup2()` ABA, loss of `O_NONBLOCK`,
caller-buffer mutation, wrapper move, thread/process fences, partial framing,
clean close, truncation, and file-dispatch ambiguity.

## Release verifier audit and refactor

The package verifier inventories files, so every `path.parts[:-1]` component is
a directory and `path.name` is the final basename. The old predicate applied
`startswith("build-")` to all components. This produced two contrary errors:

- false rejection of
  `REVISION_EVIDENCE/rev0886/validation/build-shape-observation.json`; and
- false acceptance of `build/generated-object` because `build` does not start
  with `build-`.

The refactored predicate now rejects directory components that are:

- exactly `build`;
- prefixed `build-`;
- prefixed `cmake-build-`; or
- members of the established forbidden-directory set such as `.git`,
  `CMakeFiles`, `Testing`, and `__pycache__`.

Suffix and forbidden-basename checks still apply to the final file. Evidence or
documentation basenames containing words such as `build-`, `cmake-build-`, or
`rebuild` remain valid.

`tools/test_verify_release_package_policy.py` is registered with CTest and
contains both acceptance and rejection examples. This is runtime policy
coverage, not a lexical assertion that a desired substring appears in the
verifier.

## Primary-source constraints

The implementation was checked against these primary sources:

- Linux `poll(2)` manual page:
  https://man7.org/linux/man-pages/man2/poll.2.html
- The Open Group `poll()` specification:
  https://pubs.opengroup.org/onlinepubs/9799919799/functions/poll.html
- OpenSSL `SSL_get_error()` documentation:
  https://docs.openssl.org/3.5/man3/SSL_get_error/
- OpenSSL `SSL_write_ex()` documentation:
  https://docs.openssl.org/3.5/man3/SSL_write/
- OpenSSL mode documentation, including moving-buffer and partial-write rules:
  https://docs.openssl.org/3.5/man3/SSL_CTX_set_mode/

Applied conclusions:

- `poll()` readiness and error bits are observations, not TLS protocol facts;
- timeout granularity and scheduling can overshoot the requested duration;
- interrupted waits must preserve the caller's original budget;
- `SSL_get_error()` classification must be immediate and same-thread with a
  clean error queue;
- a nonblocking SSL operation may WANT either read or write readiness; and
- retry argument identity belongs to the continuation, not the poll helper.

Those sources constrain the design but do not prove the implementation.

## Rejected alternatives

### Put polling inside `advance_or_throw()`

Rejected because it would turn a deterministic one-operation state transition
into a blocking scheduler and would make cancellation/deadline policy
inseparable from TLS framing.

### Accept a raw descriptor and event mask

Rejected because the caller could supply a convenient integer unrelated to the
continuation's authenticated BIO/socket capability or request readiness that
OpenSSL did not select.

### Use a relative duration

Rejected because restarts after signal or early timeout can silently renew the
budget unless every caller carefully tracks elapsed monotonic time.

### Treat HUP as clean close

Rejected because only OpenSSL can validate TLS close semantics and distinguish
clean shutdown from record truncation.

### Poll until progress or completion

Rejected because one scheduler dispatch would hide an unbounded number of TLS
operations and defeat the per-step work budget.

### Bind `O_NONBLOCK` into immutable socket identity

Rejected because file-status flags are mutable policy shared by duplicated file
descriptions, not the identity of the kernel socket. Strict mode re-proves the
policy around exact lifetime evidence instead.

### Rename the evidence file to satisfy the verifier

Rejected because that would preserve a wrong classifier, hide acceptance of a
real `build/` tree, and teach future release work to route around assurance code
rather than repair it.

## Residual risks and next correction

The duplex owner is a bounded poll leaf, not a production event loop. Important
remaining work includes:

- one connection owner that serializes raw SSL/BIO/fd mutation and queues exact
  read/write continuations;
- cancellation tokens and durable mapping from connection loss to message-level
  retry state;
- aggregate per-peer frame and continuation memory ceilings;
- fair scheduling between read, write, receipt, heartbeat, and shutdown work;
- epoll/kqueue/IOCP adapters with the same exact-target and absolute-deadline
  contract;
- wakeup ownership for new outbox work and clock quarantine transitions;
- authenticated receiver admission, bounded payload/effect staging, atomic
  visible publication, terminal effect receipt, and sender settlement in one
  executable path; and
- generated crash-frontier tests around every durable and network cutpoint.

A malicious same-process actor that races raw descriptor, BIO, or SSL mutation
remains outside the synchronization contract. `poll()` can still block longer
than requested due scheduling, and one OpenSSL call has no independent wall-
clock preemption. The implementation is process/thread-affine and Unix-only for
this poll leaf. There is no claim of peer receipt, exactly-once remote effect,
formal proof, anonymity, traffic-analysis resistance, or production readiness.

## Audit scope

`tools/audit_sync_tls_poll_owner.py` inventories source shape, CMake ownership,
runtime matrix presence, release-path regression coverage, and nonclaims. It is
lexical hygiene. Compiler lanes, the real TLS runtime, sanitizer execution,
stress runs, package verification, and human review carry distinct evidence and
must not be collapsed into the source audit's pass count.
