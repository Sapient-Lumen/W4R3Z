# ADR 0376: Log each representative soak cycle

Status: accepted and implemented
Date: 2026-09-13

## Context

ADR 0375 restarted the 24-hour three-writer soak with a 600-second bounded
stalled-cycle recovery threshold.  The replacement candidate
`.sandwurm/lab/three-writer-soak-24h/run.So1SOLr0` launched from commit
`7fe3ab561ed9e8b30be3fc7ba1c8529fd5eb83b8`, reached the writable soak, and
logged `writable soak cycle 1 converged`.

The runner then intentionally stayed quiet for ordinary cycles 2--9 because
the old soak logger emitted only cycle 1 and multiples of 10.  Under the
four-minute representative cadence, that makes the first named checkpoint after
cycle 1 land roughly forty minutes into the soak.  While technically expected,
the silence is operationally ambiguous: a human watcher cannot distinguish
healthy unlogged progress from a hidden liveness bug until much later.

The So1SOLr0 candidate was stopped during that ambiguous window.  It retained
outer Sandwurm launch evidence and console progress through cycle 1, but no
guest IoTox receipt.  That makes it an operator-aborted observability lesson,
not a sync correctness result.

## Decision

The soak runner now logs each representative cycle before and after convergence.

For every writable soak cycle it emits:

- `writable soak cycle N edit written writer=X marker=present|absent`
- `writable soak cycle N converged`

The convergence line is emitted every cycle when the configured soak is a
representative bounded run: `soak_minimum_cycles <= 1000` or
`soak_cycle_delay >= 60`.  Sharper high-churn stress profiles may keep sparse
convergence logs.  The start line records this as `cycle-log=each` or
`cycle-log=sparse`.

The new lines are content-free.  They expose only the synthetic cycle number,
the synthetic writer label, and the presence/absence of the synthetic marker.
They do not expose synchronized file contents, paths outside the harness's
synthetic soak directory, Tox keys, or principals.

## Consequences

The live watcher can now show ordinary sparse-cadence progress every cycle
instead of waiting for multiples of 10.  If a future run goes quiet after an
`edit written` line, that is a much sharper signal: the active cycle, writer,
and marker shape are known before the recovery threshold or hard timeout.

This does not lower acceptance criteria.  The final receipt still has to prove
the full duration/minimum-cycle gate, restart-settle evidence, repair deferral
drainage, bounded recovery events, exact projection convergence, and
content-free status.
