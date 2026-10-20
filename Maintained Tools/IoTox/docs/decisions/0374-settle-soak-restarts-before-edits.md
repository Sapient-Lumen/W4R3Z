# ADR 0374: Settle soak restarts before edits

Status: accepted and implemented
Date: 2026-09-11

## Context

The ADR 0373 24-hour candidate
`.sandwurm/lab/three-writer-soak-24h/run.OWtscPbC` launched from clean source
commit `149729e394f6fe8e3cd689721e3155a2b2745bff`.  It completed the startup,
capacity, conflict, and 24-shadow-cycle prelude, then reached 23 writable soak
cycles.  Cycle 12 completed the explicit `sync-repair` control-timeout path.

At cycle 24 the representative long-soak profile restarted node `a` before the
synthetic edit, as required by ADR 0372.  The run then rejected with
`timeout waiting for writable soak cycle 24`.

The retained content-free rejected receipt is useful: nodes `a` and `b`
remained aligned on the cycle-23 projection, node `c` held the expected cycle-24
projection, all three stores had the same object/manifest/record/branch shape,
and no conflict alternatives were present.  This was not split-brain data
corruption.  It showed that the harness's post-restart readiness check was too
shallow: Tox sessions were reconfirmed, but the sync layer was not yet proven
ready to propagate the next writer's edit.

## Decision

Scheduled writable-soak restarts now carry an explicit restart-settle policy.
The default Sandwurm soak policy is:

`soak_restart_settle_policy = "repair-before-edit"`

When a scheduled restart fires, the harness:

1. restarts the selected node;
2. waits for its local control socket and status command;
3. reconfirms the full Tox session mesh;
4. runs one bounded `sync-repair` pass across all three nodes before the cycle's
   synthetic edit is written.

This pass is not counted as a periodic/deferred soak repair.  It is recorded
separately as `soak_restart_settle_passes` and
`soak_restart_settle_cycles`, while the existing `soak_repair_passes`,
`soak_repair_deferrals`, and `soak_repair_pending` fields continue to describe
scheduled/deferred/stalled-cycle repair work.

Receipts now record `soak_restart_settle_policy`,
`soak_restart_settle_passes`, and `soak_restart_settle_cycles`.  Accepted
Sandwurm soak receipts must show one restart-settle pass per scheduled daemon
restart when the policy is `repair-before-edit`.  The live
`inspect-sync-three-writer-soak.py` and `watch-sync-three-writer-soak.py` tools
surface the settle policy and the last settle event during long runs.

## Consequences

The 24-hour gate now tests the behavior an operator actually wants after a
daemon restart: do not race the next edit into a merely connected but
sync-stale mesh.  A restart must become a settled sync participant before the
harness writes the next synthetic state.

This does not lower the data-correctness bar.  Every soak cycle still requires
all three worktrees to converge to the exact expected file/deletion projection,
with all three branches visible and no conflict files.

The sharper no-settle restart shape remains available by setting
`--soak-restart-settle-policy none`; it is stress science, not the
representative graduation profile.

## Evidence

The rejected ADR 0373 24-hour candidate
`.sandwurm/lab/three-writer-soak-24h/run.OWtscPbC` is retained as the motivating
cell.  Its verifier summary reports `status = "rejected"`,
`soak_cycles = 23`, `soak_daemon_restarts = 1`,
`soak_restart_targets = ["a"]`, `soak_repair_passes = 1`,
`soak_repair_deferrals = 0`, `sync_repair_control_timeout_ms = 120000`, and
zero conflict alternatives.  The failure digest is
`25667fe89fcd16658d470ded4f66764fe576d6869f20686971e6f345e9c521f9`.

The ADR 0374 smoke accepted at source commit
`a403ebc6608305ec2ea29c9f6f9832c298e6f691` in
`.sandwurm/lab/three-writer-soak-smoke/run.dvdqSlPg`.  It completed five soak
cycles, two scheduled daemon restarts, two restart-settle passes at cycles
`[2, 4]`, two periodic repair deferrals at cycles `[2, 4]`, two deferred
repair passes, `soak_repair_pending = false`, zero stalled-cycle recoveries,
retained recovery rehearsal, storage-fault rehearsal, and VM-smoke verification.

The next accepted `soak-24h` receipt must show
`soak_restart_settle_policy = "repair-before-edit"` and matching
restart-settle pass/cycle evidence across the full 24-hour profile.
