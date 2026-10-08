# AnonSync rev0877 evidence audit

## Mission

AnonSync is an authority-accounting system under partial failure. Exact
canonical evidence must own identity, causality, projection, dispatch, retry,
receiver admission, receipts, and visible effects. Context objects, caches,
leases, clocks, transport sessions, summaries, and test reports may support
those transitions but may not manufacture authority.

## Revision result

Rev0877 closes a load-bearing gap introduced by the first authenticated delivery
service in rev0876. The service previously accepted a public
`SyncReplicaDeliveryChannelContext`. Its actor and exporter bytes described an
authenticated TLS channel but were freely constructible by an ordinary caller.
The record layer required an opaque TLS capability; the durable service did not.
Transport authority and SQLite authority were therefore split.

The new `SyncReplicaDeliveryChannelAuthority` is privately minted, move-only,
non-copyable, process-bound, thread-lifetime-bound, and optionally backed by a
live transport verifier. Every delivery-service entry validates this authority
before reading its context or touching `SyncReplicaSqliteOwner`. The
TLS-backed verifier re-observes the exact profile, peer SPKI, and RFC 9266
exporter binding before every service or record use. A stale authority after
`SSL_clear()` or a fresh handshake fails before SQLite mutation.

This is explicit authority-flow and same-process domain separation. It is not a
security boundary against hostile code with arbitrary memory access, undefined
behavior, debugger control, or a compromised process.

## Adjacent corrections

The deep audit corrected three further high-risk or wasteful seams:

1. The TLS channel now retains its own OpenSSL reference with `SSL_up_ref()` and
   releases it with `SSL_free()`, so callers may release their original
   reference without leaving a dangling apparent capability.
2. A failed live-session check, uncertain read/write frontier, partial framed
   record, or invalid peer frame permanently poisons the channel. Bytes cannot
   be silently reinterpreted after the stream cutpoint becomes unknowable.
3. `claim_next_outbox_for_delivery_or_throw()` validates the first ready
   canonical operation against the complete wire model before lease mutation.
   A locally unsendable operation remains at attempt zero instead of entering a
   claim/encode/fail/expiry loop.

The third correction deliberately fails closed and can head-of-line block later
work. A typed permanent rejection/dead-letter state, policy generation, operator
visibility, and explicit reclassification are still required before scanning
past an incompatible first-ready intent is safe.

## Audit/refactor result

Three existing clock/lease/owner audits were coupled to the old public claim
function body. Both public claim APIs now delegate to one private audited core;
the audits verify delegation and the load-bearing ordering inside that core.
This avoids duplicating entropy, writer authority, restore, clock, lease, and
publication proofs.

An initially ad hoc TLS fork probe was rejected by the cube's raw-fork audit and
moved to the shared inherited-process harness. The final process topology has
one raw `fork()` call in one owned test-harness translation unit, 14 inherited
consumer translation units, 25 inherited spawn sites, eight fresh-image
campaigns, and 33 combined process sites.

A new 18-check delivery-channel source audit verifies lexical/source-shape
hygiene and explicitly disclaims behavioral authority. Runtime tests provide the
load-bearing evidence for rollback, move/fork/thread fences, retained OpenSSL
lifetime, stale-session rejection, and sticky stream poison.

## Validation authority

The final source state passed:

- GCC 14.2 Debug complete all-target build and no-work dependency closure;
- 180/180 registered tests in one CTest invocation;
- 55/55 audit-named registered tests;
- 2,896/2,896 focused runtime checks under GCC Debug;
- 2,896/2,896 focused checks under Clang 17 Release with C++ warnings fatal;
- 2,896/2,896 focused checks under GCC ASan/UBSan with leak detection and bundled
  SQLite 3.53.3 instrumented;
- owner/service/TLS stress totaling 5,790/5,790 repeated checks; and
- 100/100 focused clock, lease, SQLite-owner, and channel source-audit checks.

Exact logs and machine-readable reports are in `validation/`. The parent archive
SHA-256 was independently recomputed this turn. Its 179/179 registry result is
inherited from the sealed rev0876 evidence and was not rerun as a parent build.

## Largest remaining gap

No production executable calls the delivery service or authenticated TLS
channel. The new path remains evidence-terminal rather than effect-terminal: it
has no payload transfer, content verification, receiver effect intent, atomic
filesystem publication, directory durability, independently durable terminal
receipt, membership/key lifecycle, reconnect manager, or complete retry policy.

The next high-value revision should compose one narrow restart-safe executable
through bounded payload transfer and one atomic visible effect. Further
horizontal assurance work on the isolated library path should be secondary to
that executable composition.

The full mission analysis, primary-source research, speculation, risks, and
nonclaims are in `AUTHENTICATED_CHANNEL_CAPABILITY_AUDIT_rev0877.md`.
