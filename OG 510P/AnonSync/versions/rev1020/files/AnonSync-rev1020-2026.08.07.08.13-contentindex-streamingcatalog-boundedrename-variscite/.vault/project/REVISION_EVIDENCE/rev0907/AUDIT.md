# AnonSync rev0907 implementation and release audit

## Mission

AnonSync is an evidence-authorized, crash-consistent, bounded causal convergence
engine. Exact validated history and explicit live capabilities authorize effects.
Indexes, clocks, deadlines, leases, transport sessions, close alerts, counters,
pathnames, and reports may restrict or describe execution; they must not invent
work, success, retry authority, or a newer durable cutpoint.

## Product and refactor increment

Rev0907 extracts multi-session composition policy from the large CLI translation
unit into `sync_replica_session_supervisor.hpp/.cpp`. The typed owner validates
session/runtime bounds, establishes one optional whole-command absolute deadline,
clamps all five session stages to it, classifies sender and receiver terminal
states, recognizes exact clean dispatch expiry and authenticated zero-application-
byte closure, and derives the minimum safe static claim-lease horizon.

`send-batch` and `serve-batch` now require both a session bound and
`--max-runtime-seconds`. The deadline begins before manifest, database, payload,
listener, membership, and TLS preflight. This is cooperative deadline accounting,
not asynchronous cancellation of arbitrary blocking local work.

## Corrected composition and authority defects

1. **Receiver drain failure.** A sender with more allowed sessions than ready
   work authenticated one final time, emitted no application bytes, and closed as
   `no_ready_delivery`; the receiver previously failed that exact valid drain.
   It now succeeds only under the exact typed
   `authenticated_peer_closed_idle` predicate. This is not queue or catalog
   evidence.
2. **Post-deadline claim admission.** After mutual authentication the client
   could enter durable claim selection before its first request-deadline check.
   `DispatchDeadlineExpired` now observes the request cutpoint before any claim,
   operation ID, digest, prefix, frame, body, or receipt authority is created.
3. **Contradictory lease horizon.** The former 30-second default lease could
   expire while the sender's own valid receipt deadline remained open. The
   minimum is now derived from `4*T`, durable forward/lag limits, uncertainty,
   and integer exclusive-expiry allowance. Under current limits, T=5 requires
   641 seconds and T=10 requires 661 seconds. Shorter explicit values are
   rejected before operational authority opens.
4. **Sanitizer topology omission.** The new supervisor test was initially
   instrumented but not linked to sanitizer runtimes. The CMake inventory now
   includes both compile and executable-link instrumentation.

## Validation

- GCC 14.2 Debug complete graph and registry: **227/227**.
- Clang 17.0 Debug complete graph and registry: **227/227**.
- Clang 17 ASan+UBSan focused product lane: **5/5**.
- Session-supervisor direct proof: **75 checks**.
- SQLite replica owner direct proof: **250 checks**.
- Source authority audits: **27/27**, **38/38**, and **25/25**.
- Parent rev0906 package: **32/32** under the current verifier.
- Changeset reconstruction: **736/736** non-evidence files matched.
- Real process proof covers two settled deliveries, a third authenticated idle
  close, whole-command accept expiry, request pre-claim expiry, and mutation-free
  rejection of an undersized lease.

## Explicit remaining gaps

The deadline is not a hard preemptive wall-clock kill. SQLite waits, filesystem
calls, process descheduling, local receipt application, and suspend may cross an
outer expectation. A synchronous claim or payload reproof started before the
request deadline still needs a transactional second check immediately before the
request prefix. Transport uses a steady clock while durable lease observations
use suspend-aware `CLOCK_BOOTTIME`; suspend policy is not unified.

The supervisor is process-local and not durably resumable. The project still
needs a continuous scan/reconcile/claim/transfer/apply lifecycle, complete
filesystem semantics, explicit DAG readiness, scalable indexed anti-entropy,
quarantine and repair, retention/GC, cross-store cutpoints, key evolution, and a
precise anonymity/privacy threat model.
