# Audited backlog addendum — rev0017

## New verified audited-backlog item

### PENDING-CONN-BUDGET-01 / U-181

**Status:** source-traced and no-network tested across `3.3.10`, `3.3.x`, and `master`.

**Decision:** verified hardening candidate; **not strict-promoted**.

The current behavior retains outbound peer messages in pending connection state while address resolution or socket-cap connection establishment is unresolved. The maintainer witness uses `UserInfoRequest` and `SharedFileListRequest` messages to prove per-user and global growth, offline cleanup behavior, and socket-cap deferred growth.

Machine-readable evidence:

```text
data/rev0017_pending_conn_budget_probe_summary.csv
data/rev0017_public_overlap_pending_conn.csv
data/rev0017_pending_conn_budget_coherence_refactor.csv
```

Human evidence:

```text
evidence/rev0017-pending-conn-budget-probe.md
evidence/rev0017-pending-conn-budget-source-trace.md
evidence/rev0017-web-public-overlap-pending-conn.md
```

## Backlog priority change

U-181 is no longer “needs harness.” It is now “verified audited backlog / budget hardening.” It remains below strict/front-lane items because impact depends on server timing, socket pressure, and local/plugin/UI request fanout.

## Next substantive target

The next high-value target should move away from connection-management backpressure and back toward transfer provenance:

```text
TRANSFER-SIZE-PROVENANCE-01 / U-69 + U-107 + U-198
```

Reason: that cluster has a better chance of producing a stronger strict candidate if the source proves transfer-size/opened-file provenance consequences, while U-146/U-159 are likely to remain request-throttle/budget hardening.
