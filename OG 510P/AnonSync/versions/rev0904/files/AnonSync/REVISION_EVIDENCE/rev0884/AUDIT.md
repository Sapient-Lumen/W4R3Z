# rev0884 audit record

## Heart of the mission

AnonSync is an exact-authority accounting system. Canonical evidence and live
capabilities own identity, causality, dispatch, retry, receipt, and visible
effect. Readiness signals, buffer addresses, TLS sessions, C++ wrappers,
filesystem spellings, summaries, and test reports may carry or verify authority;
they must not silently manufacture it.

Rev0884 applies that rule to nonblocking TLS receive. A retryable
`SSL_read_ex()` is not “no state”: the authenticated stream owner, exact output
pointer and byte count, prefix/body offsets, process/thread incarnation, and
cleanup frontier remain authority-bearing until that operation terminates.

## Severe gap corrected

The parent had a synchronous framed reader that discarded the stream on
`SSL_ERROR_WANT_READ` or `SSL_ERROR_WANT_WRITE`. There was no application owner
that could survive a readiness boundary. A direct movable implementation with
inline prefix storage would also have been unsound: moving the wrapper can move
the buffer while OpenSSL requires the retry arguments to remain exact.

Rev0884 introduces one heap-stable private read state and a move-only public
continuation. Every `advance_or_throw()` performs at most one `SSL_read_ex`,
classifies its exact result immediately, and preserves unchanged offsets on
WANT_READ/WANT_WRITE. Prefix bounds are proven before body allocation. Clean
close before a frame is distinguished from truncation after framing progress.
Any attempted-but-abandoned operation poisons; pre-I/O destruction releases
cleanly; foreign-owner cleanup fails stopped.

## Refactor and audit finding

The authenticated channel previously represented only an unfinished write with
a boolean. Adding an independent read boolean would admit impossible dual-active
states and duplicate every guard. The owner now has one
`SyncReplicaTlsRecordReservation { Idle, Read, Write }`. Record reads, record
writes, and delivery-authority live validation all pass through that one state,
preventing exporter/certificate re-entry while a WANT retry is pending.

The lexical audit surface was correspondingly refactored. The new receive audit
has 20 checks and explicitly disclaims semantic proof. Existing file-TLS and
delivery-channel audits now inspect the central duplex owner. Process-topology
inventories were updated only for the added isolated foreign-thread fail-stop
case: 15 inherited consumer translation units, 28 inherited spawn sites, eight
fresh-image campaigns, and 36 classified process campaigns.

## Load-bearing evidence

- exact rev0883 parent ZIP independently reverified **26/26**;
- final GCC 14 Debug all-target dependency graph and no-work closure;
- complete registered gate **193/193** and audit-named gate **62/62**;
- focused authority suite **5,236/5,236** in GCC Debug, Clang 17 Release C++
  `-Werror`, and GCC ASan/UBSan with leak detection and bundled SQLite
  instrumented;
- final mixed repeated campaign **6,680/6,680** checks;
- 100 final TLS runs, **11,200/11,200** checks and 100 process-isolated
  foreign-thread read-cleanup fail-stop proofs;
- 18 selected source audits, **529/529** checks; and
- active projection `b756c6bf644b81f543b0877d50b97166faee7b32364a04d87d46ded2b26b6c81`, exact patch, compact evidence
  index, full manifest, and independent directory/ZIP package verification.

## Corrected waste and remaining waste

The single reservation enum removes duplicated state and makes illegal overlap
observable at one boundary. The incremental API also removes a hidden blocking
loop: one event-loop call can perform only one SSL read.

The larger architectural waste remains. The causal SQLite owner, file-effect
owner, authenticated delivery service, first-prefix sender, and new receiver are
still mostly a tested correctness island; the shipped executable follows an
older path. A narrow production-shaped receiver service should now be composed
instead of adding more isolated transport primitives. The final clean graph
also confirms build coupling: a small TLS-header edit still rebuilt multiple
transport/file-dispatch targets, while the earlier clean graph traversed
hundreds of unrelated actions.

## Next mission-critical slice

One bounded process/thread-affine event-loop owner should drive the incremental
reader, cap complete-frame queues, validate a canonical request under the exact
authenticated channel, invoke the existing receiver SQLite/effect owner, reach
atomic publication, produce a terminal effect receipt, and send that receipt
through the existing exact write frontier. Crash injection belongs at every
prefix/body, transaction, publication, receipt, and sender-settlement cutpoint.
Partial TLS byte offsets should remain ephemeral; durable resume authority
belongs to canonical messages and payload chunks above the lost TLS session.

## Nonclaims

This revision does not claim a production poll/epoll loop, concurrent full-duplex
use of one `SSL*`, durable partial-record resume, receiver-effect composition in
the shipped executable, peer receipt from TLS completion, exactly-once remote
execution, ThreadSanitizer, formal proof, anonymity, unlinkability, endpoint
hiding, traffic-analysis resistance, or externally trusted signed provenance.
