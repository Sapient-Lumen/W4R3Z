# AnonSync rev0907 revision notes

## Release identity

- Revision: `rev0907`
- Parent package: `rev0906`
- Parent archive SHA-256:
  `0a7ccd4ee7663cd68408654250b4873644ffd7a1df145153e47fe3d491cf9872`
- Package filename: `AnonSync-rev0907-2026.07.26.23.37-commandbudget-idleclose-leasehorizon-opalwatch.zip`
- Theme: absolute command budget, exact authenticated idle closure,
  pre-claim request cutpoint, and claim-lease horizon
- Source VCS metadata: unavailable in the imported cloudtainer archive; source
  identity is the exact parent archive, changeset, and active projection

## Mission

AnonSync is an evidence-authorized, crash-consistent, bounded convergence engine.
Exact validated history and explicit live capabilities are authority. A timeout,
TLS close, lease, retry clock, counter, projection, path, or report may restrict
or describe execution but must not invent work, success, or durable state.

Rev0907 applies that rule to the composition above one TLS conversation. A
session-count cap is not a whole-command deadline. A clean TLS close is not queue
emptiness. A request deadline is not meaningful if a durable claim may begin
after it. A lease is not safe if it can expire during the same protocol's valid
receipt horizon.

## C++ implementation and refactor

1. Added `sync_replica_session_supervisor.hpp/.cpp`, a typed process-local owner
   for finite session admission, one optional absolute command deadline, staged
   deadline clamping, sender/receiver stop policy, exact idle/clean-expiry
   predicates, and claim-lease horizon validation.
2. `send-batch` and `serve-batch` now require
   `--max-runtime-seconds` in `[1, 86400]` in addition to
   `--max-sessions` in `[1, 256]`.
3. The command cutpoint starts before manifest, store, listener, membership, and
   TLS preflight. Poll-driven session stages are clamped to it. Synchronous local
   work is cooperative and charged at the next observation; it is not forcibly
   preempted.
4. `send-one` and `serve-one` continue through the same executors with one
   session and no command-wide runtime, avoiding a parallel authority path.
5. A receiver now succeeds as `authenticated_peer_closed_idle` only after an
   authenticated close with zero request/receipt application bytes and no
   inbound or receipt frontier. This is not evidence that the peer had no work.
6. The client now observes the request-admission deadline immediately after peer
   authentication and before the first durable outbox claim. Clean expiry emits
   no operation ID, claim, digest, prefix, frame, body, or receipt state.
7. The former 30-second default lease was removed. The sender derives a necessary
   minimum from the receipt horizon and the exact durable clock policy. With the
   default clock envelope, a 5-second stage requires 641 seconds and the default
   10-second stage requires 661 seconds.
8. Explicit shorter leases fail before deployment, database, payload, or TLS
   authority opens. The process test proves database-family and payload-directory
   snapshots remain unchanged.
9. Authenticated receiver deferral is successful bounded progress for both
   one-shot and batch senders; it does not authorize sleep, immediate retry, or
   causally later work.
10. The new supervisor shares the existing file-TLS product library rather than
    adding another one-file archive. Its deterministic test is present in native,
    CTest, compile-sanitizer, and link-sanitizer inventories.

## Corrected failures

### Receiver rejected a valid bounded drain

When the sender used a larger session bound than available work, its final
mutually authenticated `no_ready_delivery` session sent no application bytes and
closed cleanly. The receiver previously classified that exact close as failure.
The new exact idle predicate makes the pair composable without treating TLS
shutdown as catalog evidence.

### Durable claim could start after the request cutpoint

Handshake and peer-profile work could consume the request budget before the
claim path began. The new `DispatchDeadlineExpired` frontier prevents claim and
prefix authority after an already-expired request-admission deadline.

### Default lease expired inside a valid protocol window

With 10-second stages, the receipt deadline is 40 seconds from admission, already
longer than the former 30-second lease. The durable clock movement envelope makes
the necessary default lower bound 661 seconds. Rev0907 rejects contradictory
time policy instead of hiding it.

### Sanitizer proof topology was incomplete

The new unit target was initially compiled with sanitizer flags but omitted from
sanitizer runtime link targets. The audit caught and corrected that before final
sanitizer evidence.

## Validation summary

- GCC 14.2 Debug full graph and registry: **227/227 passed**.
- Clang 17.0 Debug full graph and registry: **227/227 passed**.
- Clang 17 ASan+UBSan focused modified/product lane: **5/5 passed**.
- Session-supervisor direct proof: **75 checks passed**.
- Deployment binding source audit: **27/27 passed**.
- Database-open policy source audit: **38/38 passed**.
- Bootstrap-authority source audit: **25/25 passed**.
- Real process spine covers two settled deliveries, authenticated no-work close,
  receiver idle success, command accept cutpoint, request pre-claim cutpoint, and
  mutation-free short-lease rejection.

## Explicit nonclaims and next work

- The command deadline is cooperative, not an asynchronous hard kill. SQLite
  waits, filesystem calls, local receipt work, process descheduling, and suspend
  can cross an outer wall-clock expectation.
- A synchronous claim started before the request deadline can still complete
  after it; a second transactional pre-prefix deadline guard remains necessary.
- Transport deadlines use `steady_clock`, while durable lease observations use
  suspend-aware Linux `CLOCK_BOOTTIME`; suspend policy is not unified.
- `authenticated_peer_closed_idle` is not a signed no-work message, queue proof,
  or catalog cutpoint.
- The supervisor is process-local and not durably resumable.
- This remains a bounded product spine, not a daemon, fairness scheduler,
  continuous scanner, complete filesystem synchronizer, scalable anti-entropy
  engine, retention/GC owner, key-evolution system, or anonymity proof.
- Bundled SQLite remains verified 3.53.3.

See
`ABSOLUTE_COMMAND_DEADLINE_IDLE_CLOSE_PRECLAIM_AND_LEASE_HORIZON_AUDIT_rev0907.md`
and `REVISION_EVIDENCE/rev0907/` for the detailed authority analysis, research,
lineage, changeset, and machine-readable validation record.
