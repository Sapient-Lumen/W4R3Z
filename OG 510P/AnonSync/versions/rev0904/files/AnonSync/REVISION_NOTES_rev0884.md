# AnonSync rev0884 revision notes

## Mission-level correction

AnonSync treats live transport progress as authority-bearing state rather than
an incidental loop variable. Rev0883 fenced write-continuation cleanup but still
had no owner for a nonblocking TLS read after OpenSSL returned WANT_READ or
WANT_WRITE. A movable continuation with inline prefix/body buffers would also
risk changing the exact pointer that OpenSSL requires on retry.

Rev0884 makes one heap allocation the identity of an incremental record read.
The public wrapper is move-only and `noexcept` movable; moving it transfers a
`unique_ptr` without relocating the prefix or body storage supplied to
`SSL_read_ex`.

## C++ implementation

`SyncReplicaTlsRecordReadContinuation` now owns one bounded framed read and
returns typed progress: `Progress`, `WantRead`, `WantWrite`, `Complete`, or
`PeerClosed`. Each advance performs at most one SSL read. It clears the OpenSSL
error queue immediately before that call and classifies a failure immediately
with `SSL_get_error`.

The exact prefix pointer/length or body pointer/length is reconstructed from
heap-stable storage and unchanged offsets. WANT results do not advance offsets.
The first attempted read re-attests the authenticated TLS session; a pending
retry avoids certificate/exporter re-entry while strict mode still re-proves
direct socket BIOs and `O_NONBLOCK`.

A clean close-notify before any frame byte is a distinct `PeerClosed` terminal
state. Close after prefix/body progress, an unclean EOF, over-limit prefix,
readiness contradiction after I/O, or abandonment after any attempted read
poisons the stream. Destruction before the first attempted read releases the
reservation cleanly. Every no-throw path remains process/thread owner-fenced.

## Refactor

The authenticated owner no longer represents active framing with a write-only
boolean. One `SyncReplicaTlsRecordReservation { Idle, Read, Write }` controls
both directions. A second read, write, generic operation, or delivery-authority
verifier is rejected while a read or write continuation is active. This avoids
invalid two-boolean combinations and prevents certificate/exporter operations
from interposing on a pending WANT retry.

The legacy one-shot reader delegates to the incremental state machine. It still
does not spin on nonblocking readiness: encountering WANT fails and the active
continuation poisons the stream.

## Runtime and audit surface

The real TLS 1.3 test matrix now covers moves after prefix and body WANT states,
fragmented records, clean pre-I/O abandonment, pending-I/O poison, duplex
exclusion, strict descriptor reproof, clean peer close, truncation, over-limit
prefixes, non-socket BIO rejection, foreign-thread fail-stop, and legacy helper
delegation.

A new source audit inventories heap ownership, one-read-per-advance ordering,
immediate error classification, unchanged WANT offsets, prefix-before-allocation
bounds, close and cleanup frontiers, duplex reservation, runtime cases, CTest
registration, package requirements, and explicit nonclaims. Existing TLS and
delivery-channel audits were refactored to inspect the central duplex state
rather than a retired write-only flag.

Exact final gate counts and toolchain results are recorded in
`REVISION_EVIDENCE/rev0884/validation/VALIDATION_SUMMARY.json`.

## Research

The design follows OpenSSL 3.5 guidance for `SSL_read_ex`, same-argument retry,
`SSL_get_error` error-queue discipline, and the limits of `SSL_pending` as a
readiness signal. The full source rationale and failure matrix travel in
`TLS_INCREMENTAL_RECEIVE_AUDIT_rev0884.md`.

## Nonclaims and next step

This revision does not claim a production event loop, durable partial-TLS-record
resume, full-duplex concurrent SSL use, receiver effect integration in the
shipped executable, peer receipt, exactly-once execution, ThreadSanitizer,
anonymity, or formal proof.

The next high-value slice is a bounded single-owner receiver service that drives
this continuation from poll/epoll, validates a complete canonical request under
the authenticated delivery authority, reaches the existing receiver effect
state machine and atomic publication, and sends one terminal effect receipt.
