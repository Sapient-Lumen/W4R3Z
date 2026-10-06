# RFC-0017: Workload rollout, reconciliation, and rollback semantics

- Status: draft
- Author(s): (add names)
- Created: 2026-02-23
- Last updated: 2026-02-23

## Summary
Define how DeriveBSD host generations specify desired microVM state and how vmmd reconciles it.

## Proposal (v1)
- Host generation includes a workloads set (desired state descriptors).
- Activation reconciles VMs to the set (start/stop/restart).
- Rollback restores previous desired state and reconciles.
- Stateful workloads use external ZFS datasets with explicit snapshot policy.

## Open questions
- Blue/green traffic shift primitives (pf vs bridge switching)
- What “health” signals gate rollout completion
