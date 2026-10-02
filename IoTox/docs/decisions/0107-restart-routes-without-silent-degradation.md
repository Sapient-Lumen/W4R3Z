# ADR 0107: restart routes without silent degradation

- Status: accepted construction policy; product route manager pending
- Date: 2026-08-21
- Scope: multi-route establishment and pre-workload recovery
- Depends on: ADR 0016, ADR 0030, ADR 0056, and ADR 0106

## Context

Four forced-TCP routes can carry the qualified 32-stream Ratox workload, but one otherwise identical
run stopped with both guests at three confirmed routes. A whole experiment retry succeeded. Treating
that as ordinary operation would make convergence fragile; silently running the workload on three
routes would also violate the measured eight-stream per-route headroom.

## Decision

1. Each auxiliary route retains its own Tox savedata and stable transport key while sharing the same
   higher-level IoTox device principal. Restart recovers that route; it does not mint a substitute.
2. Route establishment uses at most two automatic process restarts per auxiliary route. Retry
   intervals are finite and staggered between peers to avoid correlated replacement.
3. No Ratox-plus-bulk workload starts until every named route has confirmed the expected connection
   class. Exhaustion fails the gate instead of silently degrading capacity or moving Ratox.
4. Receipts record total and deliberately injected route-process restarts. Convergence checkpoints
   expose only route counts, the last confirmed route, and the aggregate restart count.
5. This policy covers pre-workload establishment only. A route lost with active transfers does not
   authorize transparent replay, reassignment, or duplicate effect.

## Evidence

`.sandwurm/exports/pairs/pair.fmf8pynz` deliberately stopped the device's fourth route after its
friend request had been applied, restarted it from the same savedata, and then required all four
distinct routes to confirm over forced TCP. One injected and two automatic restarts were recorded.
After convergence, all 32 transfers were active and advanced, Ratox rendered 40/40 exact samples
with no 250 ms miss, and cancellation reached an empty transfer set.

## Consequences

- Establishment can repair bounded process-lifetime failures without replacing route identity.
- An incomplete route set is an explicit unavailable state, not reduced hidden capacity.
- Retry count and wall time are now visible optimization targets; this successful gate took about
  361 seconds end to end.
- Live lane loss still needs frozen pause/cancel/reassignment semantics before a product scheduler.
