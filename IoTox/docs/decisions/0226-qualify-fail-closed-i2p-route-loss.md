# ADR 0226: Qualify fail-closed I2P route loss

Status: accepted implementation, deterministic verifier gates, and genuine bounded Sandwurm
qualification, 2026-08-28.

## Context

Route-set v2 now authenticates the exact `tox/i2p-construction` member and the positive two-guest
payload cell proves that an explicitly class-pinned pull can finish without native reassignment.
That does not prove the important negative behavior. ADR 0220 deliberately says a fail-closed job
must remain bound to its lost incarnation and must not automatically resume merely because the same
route key returns under a new worker or transport epoch.

The existing actual-I2P router-restart cell faults the protected route and proves higher-epoch text.
The existing actual-Tor sync-loss cell is availability-oriented and deliberately reassigns to
native. Neither can qualify signed-class no-downgrade behavior for immutable synchronization.

## Decision

- Add the distinct `sync-tree-route-private-actual-i2p-loss` Sandwurm scenario. It uses a native UDP
  protected route, one native bulk route, and one route-set-v2-signed I2P-construction bulk route.
- Publish a 131,369-byte tree and shape the subscriber TAP to 4 Mbit/s. The guest exports at least
  65,536 received bytes on the exact I2P member before the host stops the router; the outage itself
  freezes the remaining bytes and supplies the deterministic fault window.
- Stop only the supervised client i2pd process. Keep IoTox, the native protected route, the native
  bulk route, the guest-facing adapter listener, the server router, and all three persistent service
  fronts live.
- Before recovery, require one authoritative carrier loss, one blocked fail-closed job, the original
  `awaiting-objects` job and carrier key, and exactly zero reassignment. The ready native member is a
  positive downgrade oracle: its availability must not change the result.
- Replace the router over its preserved data directory and require adapter generation two plus the
  exact I2P signed member to return with zero IoTox worker restart and one route recovery.
- Do not implicitly rebind the old job. Explicitly cancel it, submit a fresh per-job
  `fail-closed tox/i2p-construction` pull, require a distinct job ID, and complete on the same signed
  carrier key with aggregate reassignment still zero.
- Retain one content-free host record that joins the two job IDs, positive byte checkpoint, signed
  carrier commitment, fail-closed counters, router process IDs, SAM-negative interval, preserved
  datadir, adapter generations, route recovery, cancellation, and same-carrier completion. Join that
  record to the guest receipt, topology receipt, packet containment, and compact export inventory.

The verifier has an isolated positive and negative self-test. It rejects even a syntactically valid
record that changes reassignment from zero to one.

The first genuine run reached 71,292 bytes on the exact signed I2P carrier, stopped only the client
router, and proved one carrier loss, one blocked fail-closed job, a ready native alternative, and
zero reassignment. The router was replaced over its preserved datadir after a 54.550-second hold;
adapter generation two then admitted all three committed fronts and carried substantial
bidirectional Tox traffic. The application member nevertheless did not satisfy authenticated-ready
recovery within the fixed 900-second host bound, so the run is rejected rather than retained as
qualification evidence. A content-free per-sample route lifecycle/counter heartbeat is now part of
the guest gate so a repetition can distinguish transport flapping, transcript rebinding failure,
and a predicate mismatch without weakening the acceptance criteria.

The instrumented repetition resolved that ambiguity. After a 45.970-second router outage the exact
same worker advanced from `connecting`/authentication-lost to `ready` with zero worker restarts, one
carrier recovery, and zero reassignment; generation two admitted all three committed fronts. The
fresh 16 MiB pull then exposed only a few kilobytes per second and could not finish inside the
900-second host bound. That fixture was testing the already-known large-object I2P carrier-epoch and
throughput limitation, not the recovery rule. The accepted-gate candidate therefore reuses the
131,369-byte object already qualified by ADR 0219. This changes no authority, fault, recovery, or
no-downgrade predicate and still requires more than 65 KiB before the exact process loss.

Clean compact proof `pair.jbr89_gc` accepts that corrected gate. The original pull reached 69,921
bytes on the signed I2P member before the host replaced only the client router. During the
62.453-second outage, the adapter remained reachable while SAM was absent and IoTox recorded exactly
one carrier loss, one blocked fail-closed job, and zero reassignment although native remained ready.
The same datadir returned under a distinct router PID; adapter generation two admitted the committed
fronts, the exact worker recovered once with zero restart, and the old job remained fenced until
explicit cancellation. A distinct fresh job then completed the same 131,369-byte tree through the
same signed carrier. Raw and 6.656 MB content-free compact forms independently pass the strict
verifier; the compact manifest, host record, topology, captures, and guest receipts are retained as
`evidence/2026-08-28-sandwurm-fail-closed-i2p-loss.md`.

## Consequences

IoTox now has bounded evidence that a privacy-pinned sync job does not downgrade when its actual I2P
router disappears, and that recovery preserves the explicit-authority rule rather than reviving an
old transfer incarnation. Starting again costs the partial bytes by design: fail-closed work does
not feed the cross-carrier prefix-resume mechanism.

This remains a one-host laboratory construction. It does not enable production `tox/i2p`, prove
anonymity or physical path independence, authorize implicit recovery, qualify restart-persistent
partial bytes, or establish a performance bound. The rejected larger-object attempts remain
diagnostic evidence and do not widen this accepted claim.
