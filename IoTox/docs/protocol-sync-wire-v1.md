# IoTox synchronization wire v1

**Implemented:** canonical codecs, publisher/subscriber admission, explicit-FileId file join, bounded
Agent dispatch, durable receive attempts, exact retry, and the negotiated bounded-range extension

**Wire allocation:** IoTox message types 20–23 and feature bit 18 (`state-sync-v1`); message types
24–25 and feature bit 26 (`state-sync-ranges-v1`), which requires bit 18

**Activation:** default-off; advertised and handled only when `iotox run --enable-sync` constructs the
strict namespace, attempt, publisher, subscriber, worker, and file-transfer seams

All integer fields use unsigned big-endian representation. Version is exactly 1, every reserved byte
and unused fixed slot byte is zero, and no trailing bytes are accepted.

## Common frame envelope

All six records travel in the ordinary IoTox lossless custom-packet frame. Major/minor are exactly
1.0 and flags, sequence, and expiry are zero. Requests have a nonzero message ID and zero correlation.
Results have their own nonzero message ID and correlate the exact request with a nonzero correlation
ID. The enclosing confirmed session supplies the peer Tox key and online epoch; current stable-
principal proof and namespace authorization are mandatory dispatcher context and are not nominated by
the payload.

## HEAD request — message type 20, 72 bytes

| Offset | Size | Meaning |
|---:|---:|---|
| 0 | 1 | wire version, exactly 1 |
| 1 | 1 | namespace length, 1..64 |
| 2 | 6 | zero |
| 8 | 64 | canonical namespace bytes followed by zero padding |

The publisher returns its current local signed HEAD only after `sync.subscribe` admission for the
exact proven principal and namespace. Absence and denial are intentionally distinct; an unknown
namespace is deliberately indistinguishable from a denied namespace.

## HEAD result — message type 21, 304 bytes

| Offset | Size | Meaning |
|---:|---:|---|
| 0 | 1 | wire version, exactly 1 |
| 1 | 1 | status |
| 2 | 6 | zero |
| 8 | 296 | complete `IOTXSHD1` signed HEAD, or all zero |

Statuses are `1 available`, `2 absent`, `3 denied`, and `4 unavailable`. Only `available` carries a
HEAD. Structural decoding does not accept zero identities, sizes, signatures, invalid engines, or
invalid genesis/parent shape. The subscriber must still verify the signature, namespace policy,
writer membership, quotas, parent/fork/rollback transition, and its own `sync.subscribe` admission
before persistence.

## Object request — message type 22, 136 bytes

| Offset | Size | Meaning |
|---:|---:|---|
| 0 | 1 | wire version, exactly 1 |
| 1 | 1 | object kind: `1 artifact`, `2 manifest` |
| 2 | 1 | namespace length, 1..64 |
| 3 | 5 | zero |
| 8 | 32 | digest of the exact complete signed HEAD record |
| 40 | 32 | nonzero requested Tox FileId / transfer token |
| 72 | 64 | canonical namespace bytes followed by zero padding |

The publisher resolves the named current signed HEAD, derives the selected object's digest, size, and
final private path locally, and offers precisely that file with the requested FileId. The request does
not carry a path, filename, byte count, object digest, range, or executable intent. A stale HEAD,
missing final object, authorization failure, unavailable worker, or duplicate live token fails before
a new offer is accepted.

## Object result — message type 23, 72 bytes

| Offset | Size | Meaning |
|---:|---:|---|
| 0 | 1 | wire version, exactly 1 |
| 1 | 1 | status |
| 2 | 1 | object kind |
| 3 | 5 | zero |
| 8 | 32 | exact signed-HEAD record digest from the request |
| 40 | 32 | exact transfer token from the request |

Statuses are `1 offered`, `2 denied`, `3 stale-head`, `4 object-absent`, and `5 unavailable`. The
identity tuple is echoed in every result so a denial cannot be retargeted. `offered` means only that
the publisher accepted an exact Tox file offer; it is not delivery, verification, object commit, HEAD
acceptance, or activation evidence.

## Range request — message type 24, `136 + 16 * count` bytes

This optional record is valid only after both peers negotiated `state-sync-ranges-v1`.

| Offset | Size | Meaning |
|---:|---:|---|
| 0 | 1 | wire version, exactly 1 |
| 1 | 1 | namespace length, 1..64 |
| 2 | 2 | range count, 1..64 |
| 4 | 4 | zero |
| 8 | 32 | digest of the exact complete signed HEAD record |
| 40 | 32 | nonzero requested Tox FileId / transfer token |
| 72 | 64 | canonical namespace bytes followed by zero padding |
| 136 | `16 * count` | range records: 8-byte offset then 8-byte length |

Ranges name the target artifact address space. Every length is nonzero. Records are strictly sorted,
nonoverlapping, and nonadjacent; adjacent records would have a second encoding and are rejected.
Addition may not overflow. The publisher resolves the exact current HEAD and artifact size locally,
requires every range to fit, and enforces both the 64-range limit and namespace staging-byte bound on
the sum. It then offers one file whose bytes are the ranges' canonical concatenation. The complete
source remains descriptor-pinned and mutation-checked; no remote path and no temporary bundle file
exists at the publisher.

## Range result — message type 25, 72 bytes

| Offset | Size | Meaning |
|---:|---:|---|
| 0 | 1 | wire version, exactly 1 |
| 1 | 1 | status |
| 2 | 6 | zero |
| 8 | 32 | exact signed-HEAD record digest from the request |
| 40 | 32 | exact transfer token from the request |

Statuses are `1 offered`, `2 denied`, `3 stale-head`, `4 artifact-absent`, and `5 unavailable`.
The complete identity tuple is always echoed. `offered` is only publisher-side Tox offer admission;
it grants no truth about received bytes or the reconstructed artifact.

## File-offer join and terminal truth

The receiver ignores the offered filename and looks up the paused incoming offer by exact nonzero
FileId. It admits a destination only after the signed HEAD has supplied the canonical object identity,
the scheduler has reserved an exact attempt and staging bytes, and the durable attempt journal has
recorded that identity. The sender reads the explicit FileId back from c-toxcore and cancels any
mismatch. Range bundles use the target artifact's durable attempt and exact staging path; after
terminal shape and size checks the subscriber unlinks the bundle pathname while retaining its open
descriptor, reconstructs the target, and verifies its complete SHA-256 before object commit.
Auxiliary send and receive terminals use the same bounded non-evicting parent queue.

Provider file numbers remain live opaque handles. They are not request IDs, object identities, or
durable restart state. Restart never resumes one: complete staging is independently verified and
committed, while incomplete state is fenced before reassignment.

## Replay, retry, and retained nonclaims

The publisher service retains exact request/result replay within one confirmed online
epoch, rejects same-ID conflicts, and fences retained responses when the exact authority head,
principal, or capability set changes. It preallocates the offered and failure results and records
replay before making a file offer. The subscriber retains the exact HEAD request and every unanswered
object request so an operator retry resends the same message IDs and FileIds instead of creating
parallel work. A terminal outcome is applied only to the attempt already durably bound to that
FileId. Reconnect creates a new epoch, fences the old job, and must reprove authority.

One range-specific exception is frozen by ADR 0138. After an incomplete range terminal or failed
reconstruction, the subscriber may retry the unchanged canonical plan once only if it has removed
the old staging path, finished its signed attempt record, and fenced its scheduler attempt. The retry
allocates a new attempt, request message ID, and FileId. No received range-bundle prefix or old
handle is retained.
Cleanup uncertainty or a second failure is terminal. Explicit whole-job cancellation and epoch loss
retire the job and do not enter this exception.

ADR 0224 freezes a separate local whole-object transport optimization that changes no wire bytes.
When an authenticated auxiliary carrier is lost, an `available` job may fence its old attempt and
move an exact positive private whole-object prefix no-clobber into a fresh attempt owned by another
eligible authenticated carrier. The replacement has a fresh request message ID and FileId and seeks
to the inherited length; final commit still requires the complete immutable digest. Fail-closed
jobs, range bundles, cancellation, terminal failure, and zero-byte attempts never reuse that
live-loss prefix. Stale terminals from the lost incarnation cannot commit it.

ADR 0234 adds another wire-neutral whole-object case. After process restart, startup may retain only
a strict positive canonical prefix whose exact object kind, digest, and size remain bound by the
stable-device-signed attempt journal. It restores no old job, epoch, route, worker, Tox file number,
FileId, or request. A fresh authorized pull must verify a signed HEAD naming that identical object,
allocate fresh identities, inherit the inode no-clobber, and seek the new offer. Full digest
verification and HEAD-last acceptance remain mandatory. An unmatched newly verified HEAD prunes the
old prefix.

The Agent owner callback performs only bounded decode, bookkeeping, and queue insertion. Blocking
HEAD/object verification and terminal commit run on a bounded worker that reacquires current session
and authority context immediately before an effect. Range-v1 is the only integrated engine: the
manifest object must be a bounded canonical toxsync range index describing the exact artifact digest
and size. With bit 26, the subscriber commits and verifies that complete candidate manifest first,
plans only against the exact artifact named by its current accepted HEAD, and requests one bounded
missing-range bundle. No basis or plan is accepted from the wire. It falls back to a complete artifact
request when no verified basis/reuse exists or the plan exceeds request bounds. The subscriber
rechecks the semantic pair under the namespace transaction and commits the accepted signed HEAD last,
after both exact SHA-256 objects. Completion never activates it. Manual activation independently
rechecks both object identities and the same semantic pair.

No codec, friendship, filename, or FileId grants namespace access. Multi-source planning,
multi-route byte stripes, range-bundle continuation across process restart or by prefix reuse,
automatic job resurrection, remote cancellation, automatic activation, and OTA execution are
outside v1.
