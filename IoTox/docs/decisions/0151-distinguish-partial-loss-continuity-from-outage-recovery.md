# ADR 0151: Distinguish partial-loss continuity from outage recovery

Date: 2026-08-24

Status: accepted

## Context

The Sandwurm pair laboratory already proves complete packet blackhole and subsequent Tox session
recovery. That does not show whether an established session stays usable when packets are dropped but
the route remains viable. Direct UDP and forced TCP also expose different semantics: a Tox lossy
custom packet crosses UDP without retransmission, while a forced-TCP relay can recover an IP packet
drop below Tox through TCP retransmission. Treating both results as one generic loss percentage would
hide the behavior an interactive operator actually experiences.

## Decision

- Add a separate `packet-loss` two-guest scenario; do not weaken or replace the 100% blackhole gate.
- Apply independent random 5% `netem` loss to both task-owned TAP egress paths with fixed seeds
  `20260824` and `20260825`, leaving TAP carriers, VMs, agents, and the bootstrap/relay fixture live.
- Start only after both IoTox sessions are confirmed. Each guest emits 128 exact 1,200-byte lossy
  custom probes at 5 ms spacing with a 2.5 second completion deadline.
- Retain every probe ordinal, nonce, RTT or explicit miss, arrival rank, copy count, and send status.
  Require a complete unique ordinal inventory, no local send rejection, at least one delivery per
  role, and at least one application-level miss per role on direct UDP.
- Require each host qdisc to report positive packet and drop counts. Fixed configuration seeds make
  the chosen impairment reproducible; exact counters are observations, not invariant golden values.
- Require ordinary bidirectional Tox text to complete while loss remains active, require both peers
  to remain confirmed on the requested carrier at the unchanged online epoch, remove only the exact
  TAP qdiscs, and require fresh text after restoration.
- Permit zero application-level misses over forced TCP only when the qdisc proves real lower-layer
  drops. This records TCP retransmission as a property rather than misclassifying the gate as inert.

## Consequences

M3 now has a retained controlled partial-loss cell on direct UDP and forced TCP. The evidence
separates route continuity, lossy-carrier delivery, durable normal-text behavior, and outage recovery:
an unchanged epoch is required here, while a strictly advancing epoch is required after the existing
100% blackhole.

This gate does not qualify delay, jitter, reorder, duplication, constrained queues, public relays,
provider upgrades, Ratox PTY latency, two physical machines, or arbitrary kernels. The custom probe
remains unadvertised research traffic outside frozen Ratox framing.
