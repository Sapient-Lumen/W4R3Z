# ADR 0174: Qualify concurrent route cancellation and separate physical QoS

Status: accepted for four balanced simultaneous withdrawals among eight adaptive jobs over direct
UDP and forced TCP, 2026-08-25.

## Context

ADR 0172 bounded one live auxiliary cancellation. ADR 0173 populated both signed bulk-route budgets
but allowed every job to finish. Gate 4 still needed to prove that concurrent local withdrawals do
not corrupt unrelated jobs, leak signed work, cause opportunistic reassignment, or starve the
protected terminal.

An initial 1 MiB/job direct-UDP experiment completed all cancellation and survivor invariants twice,
then missed the first Ratox `OPENED` receive deadline. The remote device had already created the live
session and helper, accepted its sensitive sends, and recorded negligible owner-command scheduler
wait. Every logical route nevertheless shared one 4 Mbit FIFO-shaped client TAP. Treating that
result as a cancellation failure would conflate coordinator correctness with residual physical-link
queueing; treating a protected logical route as physical QoS would overstate the design.

The experiment also exposed an independent readiness race. Device-side readiness proved that the
device saw the controller's Ratox capability, but did not prove the reverse observation after the
device's Ratox-enabling restart.

## Decision

The `sync-tree-route-concurrent-cancel` scenario starts eight independent manual-activation tree
pulls, each with one 262,211-byte artifact and manifest. The adaptive selector must produce
`01010101` across the exact two ready bulk incarnations. Indices 0, 1, 4, and 5 are selected, giving
two withdrawals per route. Four independent CLI processes issue ordinary `sync-cancel`
simultaneously.

Every selected job must become terminal `cancelled` within 5,000 ms while retaining its original
carrier and worker identity. Cancelled namespaces may retain no accepted HEAD, activation, or
staging file. Indices 2, 3, 6, and 7 must independently request, admit, and commit two objects,
activate their exact signed HEADs, and leave staging empty. The route set must finish with two ready
bulk workers, zero total work, eight adaptive selections, and zero reassignment. One
process-incarnation-fenced client resource interval covers the entire custom phase.

Before the protected Ratox probe, the controller must observe the remote session as confirmed with
`ratox-interactive-v1`, remote authority as authorized, and the expected native carrier for three
consecutive samples. The ordinary five-second `OPEN`/sample timeout remains unchanged. This is a
readiness barrier, not latency forgiveness.

Direct UDP `pair.2laq038h` and forced TCP `pair.rlpuyjth` pass raw and compact verification. Their
four-job cancellation tails are 150 ms and 100 ms. Both retain four survivor activations, work
16-to-zero, no reassignment, and 40 protected Ratox samples below 250 ms.

## Consequences

- Gate 4's bounded concurrent-job cancellation-fairness row is closed for the exact eight-job,
  two-route topology and both native carrier classes.
- Cancellation remains a local withdrawal. It does not migrate healthy survivor work and does not
  turn a cancelled attempt into an accepted or activated revision.
- Ratox readiness is now symmetric at the controller boundary after a host restart.
- “Protected route” continues to mean scheduler/admission isolation only. It does not promise NIC,
  relay, ISP, or bottleneck-queue priority.
- The repeated 1 MiB/job direct-UDP failure becomes the seed for a separate common-link
  interference/QoS gate. Candidate mechanisms such as DSCP, `SO_PRIORITY`, fair queueing, or
  physically distinct paths require explicit implementation and evidence; none is implied here.
- ADR 0175 subsequently closes one deterministic loss→reassignment→replacement-progress→cancel
  order. Opposite/simultaneous ordering, randomized selection/timing, larger-object sharing,
  independent relay diversity, and long-running policy remain open.

## Verification

`tools/run-sandwurm-pair.py` rejects an unknown carrier, a pattern other than `01010101`, an
unbalanced cancel set, fewer than four terminal withdrawals, carrier/worker drift, survivor failure,
missing activation, accepted/activated cancelled state, residual staging/work, reassignment, a
resource digest mismatch, or protected Ratox failure. `tools/verify-sandwurm-pair.py` independently
checks private raw roots and content-free compact exports and binds the client-only observation to
the two-role route inventory.
