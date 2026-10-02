# ADR 0241: Qualify shared-edge fair queuing

Status: accepted with dual-carrier Sandwurm qualification, 2026-08-29.

## Context

ADR 0174 qualified eight concurrent route jobs and four simultaneous withdrawals at 256 KiB per
job. Two attempted 1 MiB/job direct-UDP cells completed every cancellation, survivor, activation,
and work-drain invariant, but the first protected Ratox `OPENED` response missed its unchanged
five-second deadline. IoTox's scheduler recorded only microsecond waits. Both authenticated bulk
routes and the protected primary nevertheless entered one host-shaped 4 Mbit FIFO TAP queue.

Logical route protection therefore did not establish common-link latency. We needed an exact
positive companion that changed only the shared-edge queue discipline, retained the failing object
scale and Ratox deadline, and recorded live kernel configuration and counters in the signed proof
bundle.

## Decision

- Add `sync-tree-route-common-link-fairness`. It reuses the ADR 0174 eight-job adaptive population,
  balanced four-job withdrawal, four-survivor activation, work-drain, resource, and protected Ratox
  contract, but restores the 1,048,576-byte payload / 1,048,643-byte treepack per job.
- Shape the client TAP with one 4 Mbit HTB `1:1` class and a 1,000-packet `fq_codel` leaf. This keeps
  the known common bottleneck while separating active transport flows inside it.
- Hold the client after protected Ratox completion until the host captures the live qdisc/class
  hierarchy. The manifest binds exact handles, parentage, byte rate, packet limit, active leaf-flow
  count, and nonnegative HTB/`fq_codel` counters; both class and leaf must have carried traffic.
- Keep the five-second Ratox `OPENED` receive deadline and the 250 ms per-sample render ceiling
  unchanged. Do not reinterpret fair queuing as application-level byte striping or route priority.
- Require genuine direct-UDP and forced-TCP cells, then independently verify both raw and compact
  evidence roots.

## Qualification

Direct UDP compact proof `pair.am47s4qe` and forced TCP compact proof `pair.78uagrhw` pass against
the same rev0045 binary. Both bind eight 1,048,643-byte jobs as `01010101`, four balanced terminal
cancellations, four survivor activations, zero reassignment, work 16-to-zero, and 40 protected Ratox
samples. Cancellation tails are 80/90 ms. The UDP/TCP fair queues carry 5,795,303/5,782,816 bytes
and 5,162/4,853 packets while reporting 522/150 controlled drops. Ratox render p95/max is
16.564/17.067 ms on UDP and 98.767/112.817 ms on forced TCP.

Exact commands, hashes, and evidence limits are retained in
`docs/evidence/2026-08-29-sandwurm-common-link-fairness.md`.

## Consequences

The previously failing larger-object protected-latency row now has a reproducible same-host
mechanism on both native carrier modes. A deployment that expects interactive latency while bulk
Tox flows share a constrained egress must provide a flow-aware queue (or a separately qualified
equivalent); IoTox's logical scheduler cannot manufacture that property above a FIFO bottleneck.

This does not make `fq_codel` a universal product default, prove strict traffic-class priority,
reserve bandwidth, guarantee arbitrary offered load, qualify a particular router/NIC, establish
independent path capacity, or turn whole-object route placement into bonding or byte striping.
