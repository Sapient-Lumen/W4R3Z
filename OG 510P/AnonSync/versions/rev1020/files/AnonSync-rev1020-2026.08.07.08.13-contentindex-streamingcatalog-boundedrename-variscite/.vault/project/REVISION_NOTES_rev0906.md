# AnonSync rev0906 revision notes

## Release identity

- Revision: `rev0906`
- Parent package: `rev0905`
- Parent archive SHA-256:
  `b773e651a1a4b4bf31cedb5e403d7c0e0f17d163f8d1d2db2323802935e8b8c7`
- Package filename: `AnonSync-rev0906-2026.07.26.21.24-boundedsessions-causaldispatch-pressurestop-opalcurrent.zip`
- Theme: bounded multi-session product supervision, causal outbox dispatch, and
  fail-closed pressure stopping
- Source VCS metadata: unavailable in the imported cloudtainer archive; source
  identity is the byte-exact parent archive, changeset, and active projection

## Heart of the mission

AnonSync is an evidence-authorized, crash-consistent, bounded convergence engine.
Exact validated history and explicit live capabilities are authority. Projections,
indexes, clocks, leases, retries, receipts, pathnames, sockets, and reports may
coordinate or describe work but must not silently create a newer cutpoint or
broader permission.

Rev0906 applies that rule to product scheduling. A canonical digest order may
attest state; it may not become causal dispatch policy merely because it is the
order in which rows were loaded. A batch bound may authorize a finite sequence
of sessions; it may not become an implicit daemon or retry loop.

## Implementation changes

### Shared bounded session executors

1. Added `send-batch --max-sessions N` and `serve-batch --max-sessions N`, with
   `N` required in `[1, 256]`.
2. Refactored `send-one` and `serve-one` into thin wrappers over the same shared
   executors with a bound of one, preserving their output and exit behavior.
3. The sender retains one manifest, existing-only database authority set,
   immutable payload snapshot, fixed endpoint/peer identity, and TLS context,
   while creating fresh staged absolute deadlines per session.
4. The receiver retains one listener/TLS/store authority set and refreshes
   anchored membership before each session after the first.
5. Added aggregate JSON results with attempted sessions, applied/sent receipts,
   settled/deferred deliveries, stop reason, and per-session records.
6. No-ready work, listener timeout, session bound, and authenticated receiver
   deferral are successful bounded stops. Claim/receipt ambiguity and transport
   failure remain errors.
7. Receiver deferral stops rather than sleeping or immediately retrying. The
   revision adds no daemon, backoff, retry, concurrency, or background authority.

### Causal outbox priority

1. Preserved canonical outbox attestation order by destination and operation ID.
2. Changed claim selection to choose the oldest available matching durable intent
   by `enqueued_generation`, destination, then operation ID.
3. Preserved permanent wire and payload policy validation before any lease for
   every matching claimable candidate.
4. Added an owner test that deliberately finds operation IDs whose lexical order
   conflicts with enqueue chronology and proves the oldest generation claims first.
5. Extended the real TCP/TLS two-process spine to settle two causally ordered
   deliveries in one bounded sender/receiver invocation.

## Corrected severe and wasteful behavior

The severe liveness defect was accidental scheduling authority. The loaded
outbox was canonically sorted by cryptographic operation ID, and the claimant
selected the first row. A causally later operation could therefore be dispatched
before its predecessor, receive an authenticated evidence-pending receipt, be
released, and be selected first again. That could starve the predecessor and
prevent convergence despite correct receiver behavior. Dispatch order is now
separate from attestation order.

The broader waste remains assurance/product inversion: a very large proof and
owner surface exists without one continuous product loop. Rev0906 deliberately
spends its primary delta on a real multi-session product path rather than a new
isolated lexical proof. The codebase still carries overlapping legacy/new sync
architectures, giant translation units, hundreds of CMake targets/tests, and
more than five thousand historical evidence files. These should be corrected by
measured consolidation after product parity, not by deleting proofs prematurely.

## Validation summary

- GCC 14.2 clean Debug full graph and registry: **226/226 passed**.
- Clang 17.0 clean Debug full graph and registry: **226/226 passed**.
- Clang 17 ASan+UBSan focused modified/product lane: **3/3 passed**.
- SQLite owner direct result: **250 checks passed**.
- Deployment binding: **27/27**.
- Database-open policy: **38/38**.
- Bootstrap authority: **25/25**.
- Parent rev0905 package backward verification: **32/32**.

The first full GCC run caught one policy regression: candidate selection could
bypass an oversized committed payload. The final implementation validates every
matching candidate before leasing and passes the complete registry under both
compilers plus the sanitizer lane.

## Research and dependency status

SQLite 3.53.4 was published on 2026-07-24. The official `sqlite3.c` SHA3-256 is
`67f423e9ebbbdc473cbc4772c872ee6b89f31fde4ed0279a5c25d5f65c043a16` and
the official amalgamation ZIP SHA3-256 is
`628a44cfe82c66aed1ccbbe85a562d2e33ebe64b3288981ed76285612227934e`.
The cloudtainer's permitted archive-media bridge refused to materialize the ZIP,
and its shell network path could not resolve it. Rev0906 leaves bundled SQLite
3.53.3 untouched rather than importing bytes that cannot be independently
verified. The update remains an isolated next revision.

Comparisons with Syncthing, Willow, Noise, and MLS reinforce four priorities:
a continuous product scheduler, bounded/selective interest exchange, a formal
metadata/anonymity threat model, and a separate key-evolution authority plane.
These are research directions, not rev0906 claims.

## Explicit nonclaims and remaining work

- This is not a daemon, automatic retry/backoff engine, or continuous sync loop.
- The batch has a session-count bound and fresh per-session deadlines, not one
  command-wide absolute time budget.
- The payload inventory is frozen at command start; later payloads wait for a
  later invocation.
- Oldest durable generation repairs the observed local starvation but is not a
  general topological scheduler for arbitrary imported DAGs.
- Complete directory/delete/rename/symlink/permission/platform-name semantics,
  scalable anti-entropy, safe GC, cross-store atomicity, and operator quarantine
  workflows remain missing.
- TLS authentication is not anonymity. At-rest key lifecycle, forward secrecy,
  post-compromise recovery, private interests, endpoint hiding, and traffic
  analysis resistance remain outside the implementation.
- The release is Linux-specific, self-attested, and unsigned; it has no
  ThreadSanitizer or formal-proof claim.
- Bundled SQLite remains 3.53.3.

See
`BOUNDED_CAUSAL_SESSION_SUPERVISOR_AND_OUTBOX_PRIORITY_AUDIT_rev0906.md` and
`REVISION_EVIDENCE/rev0906/` for the detailed assessment, research, lineage,
changeset, and machine-readable validation record.
