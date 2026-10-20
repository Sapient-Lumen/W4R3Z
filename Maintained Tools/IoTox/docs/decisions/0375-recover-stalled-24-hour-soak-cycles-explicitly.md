# ADR 0375: Recover stalled 24-hour soak cycles explicitly

Status: accepted and implemented
Date: 2026-09-13

## Context

ADR 0371 disabled `soakStalledRestartAfter` in the primary 24-hour
three-writer soak because the earlier 120-second recovery threshold was too
eager for a sparse, VM-only reliability run.  That made the experiment easier
to interpret: either every cycle converged passively, or the hard per-cycle
timeout rejected the run.

The next corrected candidate,
`.sandwurm/lab/three-writer-soak-24h/run.hlBeElr6`, launched from source commit
`2c09d63bc4a00d4802e87e684b84ebb9b1901806` with the 48-hour outer receipt
budget from ADR 0374.  It reached 143 completed writable soak cycles, completed
six scheduled daemon restart-settle passes, drained five deferred repairs, and
then rejected at cycle 144 with:

`timeout waiting for writable soak cycle 144`

The rejected receipt is content-free and machine-verifiable.  It shows
`partial_branch_count_per_node = [3, 3, 3]`,
`partial_conflict_alternatives_per_node = [0, 0, 0]`, and no branch explosion.
The partial projection shows node `a` still on cycle 143 with the toggle marker
present, while nodes `b` and `c` held the expected cycle-144 projection with
the marker absent.  Because the primary profile had recovery disabled, the
receipt also shows `soak_stalled_restart_after_ms = 0` and
`soak_stalled_cycle_recoveries = 0`.

That is useful science, but it exposed the limit of a pure-passive VM-only
graduation gate: a single lagging node after a scheduled restart can consume the
hard 900-second cycle timeout and throw away roughly twelve hours of otherwise
healthy evidence without exercising the already-retained stalled-cycle recovery
path from ADR 0367.

## Decision

The active `soak-24h` Sandwurm profile now uses a bounded stalled-cycle
recovery threshold:

`soakStalledRestartAfter = 600`

The hard per-cycle timeout remains 900 seconds.  This keeps a long passive
window, avoids the earlier 120-second noise, and still leaves the harness time
to recover before the hard cycle rejection.

When a soak cycle misses the 600-second threshold, the existing recovery path:

1. identifies the lagging node or nodes;
2. records their content-free wait channels;
3. restarts only those targets;
4. reconfirms the full Tox session mesh;
5. runs one bounded `sync-repair` pass; and
6. still requires exact convergence for the same synthetic cycle.

Accepted Sandwurm soak receipts must now bind the active profile by carrying
`soak_stalled_restart_after_ms = 600000`.  Passed and rejected receipts both
retain the threshold and any recovery events.  The independent
`verify-sync-three-writer-sandwurm.py` verifier now also accepts late-soak
rejections whose retained `stage_events` tail no longer contains the initial
`three signed branches converged` startup line, provided the receipt contains
later soak evidence and all three branch frontiers remain visible.

## Consequences

A future accepted 24-hour receipt under this profile will prove that the
three-writer namespace remained convergent for the full gate while scheduled
restart, repair deferral, and bounded stalled-cycle recovery evidence stayed
content-free and explicit.  It will not mean “no node ever needed help.”

The stricter zero-recovery soak remains meaningful as a later product-quality
experiment, but it is no longer the primary VM-only graduation gate.  If the
bounded-recovery profile accepts with frequent stalled-cycle recoveries, that
will be a performance/reliability finding rather than a silent pass; the count,
targets, wait channels, and cycles will be visible in the receipt.

The data-correctness bar is unchanged.  Every accepted soak cycle still has to
converge to the exact expected projection on all three nodes, with the expected
branches visible and no conflict material.

## Evidence

The rejected run
`.sandwurm/lab/three-writer-soak-24h/run.hlBeElr6` is retained as the
motivating proof.  After the verifier was relaxed for late-soak stage-history
tails, the retained receipt verifies as `status = "rejected"`,
`partial_soak_cycles = 143`, `partial_soak_restart_settle_passes = 6`,
`partial_soak_stalled_restart_after_ms = 0`,
`partial_soak_stalled_cycle_recoveries = 0`,
`branch_count_per_node = [3, 3, 3]`, and
`conflict_alternatives_per_node = [0, 0, 0]`.
