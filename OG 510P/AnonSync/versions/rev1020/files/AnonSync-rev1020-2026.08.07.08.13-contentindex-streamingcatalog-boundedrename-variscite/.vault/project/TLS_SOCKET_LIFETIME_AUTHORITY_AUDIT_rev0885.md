# TLS Socket Lifetime Authority Audit — rev0885

## Executive finding

Rev0884 correctly preserved one pending `SSL_read_ex()` operation across
`SSL_ERROR_WANT_READ` and `SSL_ERROR_WANT_WRITE`, but its strict readiness
policy re-proved only that the current descriptor number still denoted a socket
and still had `O_NONBLOCK`. That was not an identity proof.

A descriptor number is a recyclable table slot. Another owner can close it and
use `dup2()` to place a different nonblocking stream socket at the same integer.
The old checks would still pass. The pending OpenSSL operation would then be
resumed while its BIO addressed a different kernel socket object. The same gap
existed between the strict writer's accepted length prefix and its body
frontier. This is **Descriptor-number ABA**: the observed integer goes from
socket A, through absence, to socket B while appearing unchanged to code that
checks only the final number and properties.

Rev0885 introduces one transport-independent Linux socket-lifetime observer and
makes the authenticated TLS owner retain its opaque result for the entire
record reservation. The proof combines direct socket-BIO shape, descriptor
number, socket type, `fstat` device/inode identity, a mandatory nonzero Linux
`SO_COOKIE`, and `O_NONBLOCK`. Observation samples file identity and the cookie
both before and after the other checks. Reproof reconstructs the complete tuple
and requires exact equality.

The design separates three subordinate signals:

- an event-loop readiness notification, which is only a scheduling hint;
- a descriptor integer, which is only an advisory poll handle; and
- a captured socket-lifetime proof, which remains private to the authenticated
  channel owner and must be re-established at every authority frontier.

The refactor also removes raw `fstat`, `getsockopt`, and `fcntl` identity logic
from the TLS implementation. One generic C++ leaf now owns those semantics and
its diagnostics. The public identity type exposes only the descriptor needed by
polling code; socket type, stat fields, and cookie are deliberately opaque so a
consumer cannot compare a convenient subset or serialize process-local kernel
evidence as protocol authority.

Rev0885 additionally exposes a typed **Advisory event-loop target** after a
WANT result and caps each public body read request at **64 KiB**. Lookup itself
re-proves the socket before returning an integer, and `advance_or_throw()`
re-proves again immediately before the OpenSSL exact retry. A stale target
therefore cannot silently retarget the TLS operation.

This revision does not claim an event-loop service, a production receiver,
write-side WANT continuation, durable partial-frame recovery, peer admission,
terminal effect receipt, exactly-once execution, or anonymity.

## Mission fit

AnonSync's heart remains exact authority accounting:

> Exact authorized history owns identity, causality, projection, dispatch,
> retry, receipt, and visible effect. Kernel handles, TLS return codes,
> readiness notifications, summaries, and source audits are evidence under an
> owner; none may manufacture authority by convenience.

At a pending TLS record frontier, the relevant identity is not merely “an SSL
object has fd 17.” It includes:

- the exact authenticated channel state and exporter binding;
- the exact process and thread incarnation permitted to touch that state;
- the exclusive duplex record reservation;
- the exact heap-stable buffer pointer and requested length of a pending
  `SSL_read_ex()` call;
- the exact kernel socket object addressed by each direct BIO;
- the nonblocking policy required by the bounded caller;
- accepted prefix/body progress; and
- whether failure is still pre-I/O, pending/ambiguous, complete, cleanly closed,
  or poisoned.

Rev0884 owned the first four items and framed progress. Rev0885 closes the
kernel-object gap. A recycled number can no longer satisfy the record owner's
socket proof merely because the replacement is also a nonblocking socket.

## Primary-source constraints

The implementation and audit were reviewed against these primary or
maintainer-authored sources:

- OpenSSL 3.5 `SSL_read` / `SSL_read_ex`:
  <https://docs.openssl.org/3.5/man3/SSL_read/>
- OpenSSL 3.5 `SSL_get_error`:
  <https://docs.openssl.org/3.5/man3/SSL_get_error/>
- OpenSSL 3.5 nonblocking client guide:
  <https://docs.openssl.org/3.5/man7/ossl-guide-tls-client-non-block/>
- OpenSSL 3.5 `SSL_write` / `SSL_write_ex`:
  <https://docs.openssl.org/3.5/man3/SSL_write/>
- Linux commit introducing `SO_COOKIE`:
  <https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=5daab9db7b65df87da26fd8cfa695fb9546a1ddb>
- Linux eBPF socket-cookie documentation, which describes the cookie as stable
  for the socket lifetime and usable as an assumed-unique global identifier:
  <https://docs.ebpf.io/linux/helper-function/bpf_get_socket_cookie/>
- Linux `socket(7)`:
  <https://man7.org/linux/man-pages/man7/socket.7.html>
- systemd documentation confirming that the Linux socket cookie is exposed by
  `getsockopt`:
  <https://www.freedesktop.org/software/systemd/man/latest/systemd.socket.html>

The load-bearing observations are:

1. A nonblocking SSL read can return either WANT_READ or WANT_WRITE.
2. A retryable OpenSSL I/O call remains one incomplete operation. The same
   function and operation arguments must be used when it is retried.
3. `SSL_get_error()` must classify the exact preceding call without an
   intervening OpenSSL operation that disturbs the applicable error state.
4. Poll/select readiness is a hint about when to retry; it is not proof of
   application progress, peer receipt, or object identity.
5. Linux supplies a kernel-generated socket cookie that remains stable over the
   socket object's lifetime. `SO_COOKIE` exposes that value to user space.
6. File-descriptor integers are reusable and `dup2()` can deliberately replace
   the object named by an existing number.

These sources constrain the design. They do not prove AnonSync's implementation,
race freedom, compiler output, or end-to-end behavior.

## Defect in rev0884

The strict TLS policy previously used a helper equivalent to:

1. obtain the read and write descriptors from direct OpenSSL socket BIOs;
2. call `getsockopt(SO_TYPE)`;
3. call `fcntl(F_GETFL)`; and
4. require `O_NONBLOCK`.

That establishes a descriptor class and a current property. It does not bind an
object lifetime.

A concrete counterexample is:

1. strict read captures fd 17 and enters WANT_READ;
2. another actor closes fd 17;
3. a fresh nonblocking `SOCK_STREAM` socket B is created;
4. `dup2(B, 17)` restores the original integer;
5. the old readiness check sees a socket with `O_NONBLOCK`; and
6. OpenSSL retries the pending operation through its BIO's fd 17, now socket B.

No ordinary equality check on the integer, type, or flag detects that sequence.
The result can be cross-connection data exposure, protocol corruption, a stuck
state machine, or apparently valid bytes from an unauthenticated transport
lifetime. The TLS session object still contains cryptographic state for socket
A, but its underlying stream has been substituted. Continuing is never
truthful; the channel must be poisoned.

The write side had a related cutpoint. The first-prefix dispatcher intentionally
holds a SQLite writer only across a fixed eight-byte encrypted prefix, then
releases it before the potentially large body. A descriptor substitution in
that interval could send the body to a different socket while preserving the
same integer and nonblocking properties. Prefix authority therefore needs to
bind the exact socket object that must carry the body.

## Generic socket-lifetime leaf

### Opaque value

`SyncSocketReadinessIdentity` is a small process-local value created only by
`observe_sync_nonblocking_socket_identity_or_throw()`. It has no public default
or raw-field constructor. The retained fields are private:

- descriptor number;
- `SO_TYPE`;
- `st_dev`;
- `st_ino`; and
- nonzero Linux `SO_COOKIE`.

Default equality compares the full tuple. The only public accessor is
`descriptor()`, because an event loop must eventually receive an integer to
poll. The remaining components are intentionally opaque.

This is an audit/refactor correction, not cosmetic encapsulation. Public getters
for cookie, inode, or type would invite callers to:

- compare only the convenient field;
- log or persist the value as if it were durable identity;
- transmit process-local evidence over the protocol;
- build a second, subtly different reproof implementation; or
- mistake a kernel cookie for a cryptographic credential.

The class instead supports exactly two meaningful operations: carry the opaque
expected tuple, and exact-compare it with a fresh observation.

### Observation order

On Linux, observation performs:

1. reject a negative descriptor;
2. `fstat` into `before`;
3. require socket mode with `S_ISSOCK`;
4. read exact `SO_TYPE`;
5. read a nonzero `SO_COOKIE`;
6. read file-status flags and require `O_NONBLOCK`;
7. `fstat` into `after` and require identical device/inode/mode;
8. read `SO_COOKIE` again and require equality; and
9. checked-convert stat components into the private tuple.

The second stat and cookie observations catch a substitution that remains
visible across the observation window. They do not make unsynchronized
concurrent mutation safe. An adversary could theoretically swap A→B→A between
individual system calls. **Raw descriptor mutation must be serialized** by the
same higher-level owner that serializes use of the `SSL*`.

The double observation is still valuable. Without it, a routine could
accidentally return a mixed tuple assembled from two sequential occupants even
when the race overlaps a system call boundary in an ordinary way. With it,
observable inconsistency fails closed.

### Linux-only exactness

The strongest evidence implemented here depends on Linux `SO_COOKIE`. The
source uses a compile-time error if a Linux build lacks the socket-option
constant and rejects a zero or changing cookie at runtime.

**Unsupported platforms fail closed.** Rev0885 does not label `st_dev` and
`st_ino` alone as exact cross-ABA authority on another Unix. A future platform
adapter may be added when it can provide an equivalently strong, documented,
process-local socket-lifetime identifier. Until then, strict mode reports that
it cannot prove an exact nonblocking socket lifetime.

This is intentionally narrower than the initial draft, which retained an
optional cookie bit and accepted a weaker non-Linux tuple. Optional evidence is
appropriate for diagnostics; it is not appropriate when the API name and
consumer rely on exact object-lifetime reproof.

### Reproof

`reprove_sync_nonblocking_socket_identity_or_throw()` observes the original
descriptor number again and exact-compares the opaque tuple. It fails when:

- the descriptor is closed;
- the number now names a non-socket;
- the number names a different socket;
- `SO_TYPE` differs;
- `O_NONBLOCK` is gone;
- stat identity differs;
- the cookie is absent, zero, changed, or unobservable; or
- any required system call fails.

Restoring `O_NONBLOCK` on the same socket permits reproof again. That behavior
is deliberate: the identity is the same, while strict readiness authority is a
current property checked at every frontier.

## TLS ownership refactor

### One proof beside one reservation

`SyncReplicaTlsAuthenticatedState` already owns the exact process/thread
incarnation, `SSL*`, peer pin, exporter binding, poison/closed state, and the
exclusive `Idle/Read/Write` record reservation. Rev0885 adds exactly one
optional read/write socket proof to that same owner.

The proof lifecycle is:

- capture before changing `Idle` to `Read` or `Write`;
- retain while the reservation is active;
- reprove at each pending retry;
- recapture and exact-compare at each fresh operation boundary;
- clear on successful completion;
- clear on pre-I/O abandonment;
- clear and poison on post-I/O abandonment or identity failure;
- clear on clean peer-close; and
- clear on general poison.

Keeping proof and reservation together rules out split ownership states such as
an active continuation with a copied proof detached from the current channel,
an idle channel retaining stale socket evidence, or a moved wrapper becoming a
new authority source.

### Direct BIO capture

Strict capture first requires both OpenSSL BIOs to exist and to be direct
`BIO_TYPE_SOCKET` instances. It then obtains `SSL_get_rfd()` and
`SSL_get_wfd()` and passes each distinct descriptor to the generic observer.
When both directions use the same descriptor, the exact opaque value is copied
rather than independently inferred.

The TLS source no longer contains raw `fstat`, `getsockopt`, `fcntl`, or
`SO_COOKIE` logic. This removes a wasteful and dangerous duplication seam:
future transport adapters can consume one reviewed observer, while changes to
Linux evidence semantics have one implementation and one dedicated runtime
matrix.

## OpenSSL exact retry and fresh-operation separation

A WANT result and a successful partial read are different authority frontiers.
Rev0885 makes that distinction explicit.

### Pending WANT retry

After `SSL_read_ex()` returns WANT_READ or WANT_WRITE:

- prefix/body offsets remain unchanged;
- the heap-stable pointer remains unchanged;
- the requested length remains unchanged;
- the continuation records the exact requested readiness direction; and
- `retry_pending` remains true.

Before the next retry, the authenticated owner checks its process/thread and
read reservation, then performs only system-level socket-lifetime reproof. It
does not call certificate, exporter, BIO-inspection, or other OpenSSL APIs.
This preserves the narrow **OpenSSL exact retry** frontier while preventing a
changed descriptor lifetime from reaching OpenSSL.

If the proof fails, the channel is poisoned and the continuation abandons the
reservation. The operation may already have consumed or emitted TLS control
bytes, so it cannot be replaced by a fresh operation on a reused stream.

### Fresh operation after success

A successful `SSL_read_ex()` call completes that OpenSSL operation even when it
returns only part of the AnonSync frame. Before the next read call, the owner:

1. revalidates the authenticated live TLS session and exporter binding;
2. re-inspects the direct read/write BIOs and their descriptor numbers;
3. captures fresh opaque socket identities; and
4. exact-compares them to the proof retained at reservation.

This catches descriptor or BIO substitution between successful prefix/body
steps. It also avoids treating every later call as continuation of an old WANT,
which would incorrectly suppress live-session re-attestation for an entire
large frame.

### Strict write frontier

The strict writer captures the same proof before accepting its encrypted length
prefix. Before body progress it revalidates the TLS session, re-inspects direct
BIOs, recaptures both socket identities, and requires exact equality. A
substitution between prefix and body poisons the channel. Sender outbox intent
remains ambiguous after prefix progress; transport failure is not misreported as
receiver admission or terminal effect.

Write-side `SSL_ERROR_WANT_READ` and `SSL_ERROR_WANT_WRITE` are still fail-closed
in this revision. The existing writer loops only while `SSL_write_ex()` reports
successful progress; readiness loss poisons the stream because no heap-stable
write-retry continuation yet owns exact pointer/length state for every partial
call. Rev0885 does not weaken that boundary merely to claim symmetry.

## Advisory event-loop target

`SyncReplicaTlsRecordReadContinuation::pending_readiness_or_throw()` is valid
only after a strict read has returned WANT_READ or WANT_WRITE. It returns:

- `{read_fd, Readable}` for WANT_READ; or
- `{write_fd, Writable}` for WANT_WRITE.

The typed direction prevents a common error: a TLS read can need to write
control traffic, so polling only for readability can deadlock.

The target is advisory, not authority. Two proofs protect its use:

1. target lookup performs system-only exact reproof before returning the fd, so
   an already-recycled integer is not handed to the event loop; and
2. `advance_or_throw()` performs exact reproof again immediately before
   re-entering OpenSSL, because the object could change after poll registration
   or while the caller waits.

If lookup discovers stale identity, it poisons the authenticated state and
immediately abandons the pending continuation. Returning a stale integer and
waiting for a later advance would expose the event loop to an unrelated kernel
object and unnecessarily retain a reservation that can never be resumed.

A readiness event can still become stale without identity loss. That is normal:
the exact retry may simply return WANT again. No readiness event proves bytes,
peer admission, receipt, or effect.

## Bounded public body step

The frame prefix remains exactly eight bytes. Once the peer-advertised body
length has passed the configured maximum and representability checks, the body
buffer is allocated exactly once in heap-stable state.

Each public body call supplies at most
`kSyncReplicaTlsRecordReadStepBytes == 64 KiB` to `SSL_read_ex()`. Prefix calls
request only the remaining prefix bytes. A WANT retry reconstructs the same
pointer and the same bounded length because no offset changes on WANT.

This ceiling is an application request bound, not a claim about OpenSSL's
internal number of kernel reads, CPU time, TLS-record processing, or scheduler
latency. It prevents one `advance_or_throw()` from submitting an arbitrary
peer-sized remainder and gives a future event-loop owner a finite application
work unit.

## Failure matrix

| Frontier | Observation | Result | Stream authority |
|---|---|---|---|
| Strict begin, BIO absent/non-socket | Direct BIO proof fails before reservation | Throw | Idle and reusable if otherwise valid |
| Strict begin, unsupported platform | Exact lifetime unavailable | Throw | Idle; no weak authority minted |
| Strict begin, blocking descriptor | `O_NONBLOCK` absent | Throw | Idle; no stream I/O attempted |
| Strict begin, cookie/stat capture inconsistent | Observation raced or failed | Throw | Idle; no reservation accepted |
| Read WANT, unchanged socket | Exact system reproof passes | Retry same function/pointer/length | Read reservation remains exclusive |
| Read WANT, lost `O_NONBLOCK` | Reproof fails | Throw and abandon | Poisoned |
| Read WANT, close/`dup2` ABA | Cookie/stat tuple differs | Throw and abandon | Poisoned |
| Poll-target lookup after ABA | Lookup reproof fails | Throw and abandon immediately | Poisoned |
| Successful partial read, unchanged socket/session | Full session/BIO recapture passes | Start next fresh read operation | Read reservation remains exclusive |
| Successful partial read, changed BIO/socket | Full recapture differs | Throw and abandon | Poisoned |
| Write prefix accepted, unchanged socket/session | Full recapture passes | Body may proceed | Write reservation remains exclusive |
| Write prefix accepted, descriptor ABA | Full recapture differs | Throw | Poisoned; sender attempt remains ambiguous |
| Read completes exact body | Frame size matches | Release reservation, expose complete frame | Channel reusable |
| Clean `close_notify` before frame bytes | Zero-return with zero progress | `PeerClosed` | Channel permanently closed, not poisoned |
| Close/error after any frame progress | Incomplete framed operation | Throw and abandon | Poisoned |
| Continuation destroyed before first read call | No SSL I/O attempted | Clean release | Channel reusable |
| Continuation destroyed after read attempt/WANT | Pending or ambiguous SSL operation | No-throw abandon | Poisoned |
| Foreign process/thread cleanup | Owner incarnation mismatch | Fail-stop before mutation | No unauthorized cleanup mutation |

## Runtime evidence added

### Generic identity test

The dedicated generic executable covers:

- successful observation of a nonblocking stream socket;
- exposure of only the advisory descriptor;
- exact unchanged reproof;
- inequality of independent socket lifetimes;
- rejection after loss of `O_NONBLOCK`;
- successful reproof after restoring `O_NONBLOCK` on the same socket;
- rejection after close/`dup2` descriptor ABA;
- rejection of a nonblocking pipe; and
- rejection after descriptor close.

The pipe fixture uses `pipe()` plus explicit flag configuration instead of
`pipe2()`. That small test refactor avoids coupling an identity test to a
convenience construction API and makes each required property visible.

### Real TLS 1.3 matrix

The existing authenticated in-process TLS fixture now additionally covers:

- no readiness target before WANT;
- exact readable/writable target after WANT;
- target preservation across move of the heap-stable continuation;
- target-lookup rejection after descriptor ABA;
- exact retry rejection after descriptor ABA without a second lookup;
- fresh-step rejection after successful partial progress and ABA;
- strict write rejection between accepted prefix and body;
- strict file-dispatch rejection at the same frontier;
- loss of `O_NONBLOCK` after WANT;
- 64 KiB maximum body progress per public step; and
- existing cleanup, affinity, duplex reservation, close, truncation, bounds,
  and canonical file-dispatch frontiers.

The ABA fixtures intentionally replace the descriptor with another nonblocking
stream socket at the same number. Passing therefore depends on exact lifetime
evidence, not on the old socket-class policy.

## Audit/refactor findings

### Corrected duplication

Before this change, socket readiness checks lived inside the OpenSSL adapter.
That made them difficult to reuse, test independently, or compare with future
poll/epoll owners. It also encouraged every transport seam to repeat a slightly
different set of `getsockopt` and `fcntl` checks.

Rev0885 moves the capability into one small library with no OpenSSL dependency.
The TLS adapter now owns composition only: direct BIO inspection, two-direction
proof capture, reservation lifecycle, and OpenSSL retry boundaries.

### Corrected public overexposure

The first rev0885 draft exposed getters for socket type, device, inode, and
cookie and allowed non-Linux Unix systems to accept an identity without a
cookie. Review found both choices too permissive.

The final value is opaque except for its advisory descriptor, and unsupported
platforms fail closed. This prevents accidental partial authority and keeps the
contract aligned with what the implementation can actually prove.

### Corrected stale-target disclosure

The first draft returned the stored descriptor from
`pending_readiness_or_throw()` without a fresh system reproof, relying only on
the later `advance_or_throw()`. Although later retry remained protected, the
event loop could temporarily be pointed at an unrelated object after ABA.

The final implementation re-proves on target lookup and again on advance.
Failure during lookup abandons the impossible pending operation immediately.

### Lexical audit scope

`tools/audit_sync_socket_readiness_identity.py` inventories source shape,
including opaque construction, Linux evidence ordering, double capture, exact
comparison, CMake separation, absence of duplicate raw syscalls in TLS, proof
lifecycle, retry/fresh separation, poll-target abandonment, bounded read steps,
runtime case names, CTest registration, package surface, and this design record.

That audit is hygiene only. Substring order does not prove system-call atomicity,
Linux cookie uniqueness, OpenSSL behavior, pointer stability, or generated
machine code.

## Alternatives considered

### Keep `SO_TYPE` and `O_NONBLOCK` only

Rejected. A replacement nonblocking stream socket satisfies both. Those are
properties of the current occupant, not identity of the original object.

### Bind only descriptor number plus `fstat`

Rejected for Linux strict mode. Stat identity is useful and remains part of the
tuple, but Linux provides a documented socket cookie specifically intended to
identify the socket object over its lifetime. Exact mode should use all
available required evidence rather than silently weaken itself.

### Bind only `SO_COOKIE`

Rejected. The cookie identifies the socket object, but strict readiness also
requires a current socket type and `O_NONBLOCK`. Stat double capture supplies an
additional check against mixed observations and better diagnostics.

### Expose raw identity fields publicly

Rejected. They are implementation evidence, not application protocol fields.
Opaque equality prevents partial comparison and serialization overclaim.

### Return the identity object to the event loop

Rejected. Polling APIs need an fd and readiness direction. Giving them the
private proof would invite transfer or independent reproof policy. The channel
owner retains evidence and returns only a typed advisory target.

### Re-run full TLS authentication before a WANT retry

Rejected. WANT leaves one incomplete OpenSSL I/O operation. System-only socket
reproof protects the kernel object without interposing unrelated OpenSSL calls
before the exact retry.

### Never re-attest after the first read call

Rejected. Every successful read completes one OpenSSL operation. The next call
is a fresh frontier and must revalidate session/BIO/socket authority.

### Add a resumable write continuation in the same revision

Deferred. A correct write continuation must retain exact pointer, length,
partial-success semantics, WANT direction, reservation, body cutpoint, and
sender ambiguity policy. Extending scope without that complete state machine
would weaken the already fail-closed writer.

## Deliberate nonclaims and remaining work

Rev0885 deliberately **does not claim**:

- that `SO_COOKIE` is a cryptographic identity or durable protocol identifier;
- safety under unsynchronized raw descriptor mutation;
- support for exact strict socket identity outside Linux;
- a poll, epoll, io_uring, or reactor service;
- a resumable nonblocking write WANT state machine;
- bounded wall-clock duration of one OpenSSL call;
- durable partial-frame storage or restart resume;
- authenticated accept/connect ownership;
- bounded complete-frame queues or receiver backpressure;
- receiver SQLite admission composed with this read continuation;
- atomic filesystem effect and terminal effect receipt over this transport;
- peer receipt from local TLS write completion;
- exactly-once remote execution;
- ThreadSanitizer coverage;
- externally trusted build provenance; or
- anonymity, unlinkability, or traffic-analysis resistance.

Raw descriptor mutation must be serialized with the authenticated channel
owner. The current process/thread capability prevents ordinary AnonSync API
calls from crossing owners, but it cannot stop unrelated code in the process
from calling `close`, `dup2`, `fcntl`, `SSL_set_bio`, or other raw APIs. The
reproofs detect many resulting contradictions and fail closed; they do not turn
an unsynchronized process into a race-free one.

## Recommended next composition step

The next valuable C++ milestone remains a bounded receiver owner rather than
more isolated vocabulary:

1. place authenticated accept/connect and this read continuation under one
   poll/epoll reactor bound to a process/thread incarnation;
2. bound active channels, per-channel frames, aggregate bytes, and ready work;
3. decode exactly one canonical file-delivery request;
4. enter receiver SQLite idempotency/admission authority;
5. stage and atomically publish one bounded file effect;
6. mint a terminal effect receipt only after durable publication evidence;
7. send that receipt through a write continuation with the same exact retry
   discipline; and
8. settle the sender's exact outbox claim only from the validated receipt.

The full-history SQLite owner should remain the correctness oracle while this
narrow executable composition is built. Readiness, socket cookies, and TLS
progress are transport evidence; canonical operation, durable admission,
visible effect, and receipt remain the mission's authoritative history.
