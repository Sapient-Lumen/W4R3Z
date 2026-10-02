# ADR 0172: Qualify bounded multi-route sync cancellation

Status: accepted for one positively progressing auxiliary pull on direct UDP and forced TCP,
2026-08-25.

## Context

ADR 0171 proved that admitted work affects later route placement, but Gate 4 still lacked an exact
cancellation tail. The existing `sync-file-cancel` cell observed primary-transport progress through
`iotox files`. Auxiliary file managers deliberately own separate file-number domains, so projecting
only the primary manager could not prove that bytes had crossed the selected worker. Treating
positive `admitted-work` as byte progress would weaken the experiment and conflate scheduler
admission with transport effects.

## Decision

`SyncPullSnapshot` retains its random transfer FileIds only inside the process. `sync-status` joins
those identities to live auxiliary-worker transfer snapshots under the pull's exact route key and
worker incarnation. It renders only three content-free aggregates per job:
`carrier-active-receives`, `carrier-receive-position`, and `carrier-receive-bytes`. It does not render
FileIds, paths, content, or peer labels. No network frame, signed artifact, route binding, or durable
format changes.

The new `sync-tree-route-cancel` Sandwurm cell constructs one protected primary and two
reciprocally authenticated bulk routes per guest. The subscriber uses the conservative adaptive
selector for one two-object tree pull and waits until the exact chosen worker reports a positive,
nonterminal receive position. Before cancellation it binds the pull job, route key, worker ID, one
adaptive decision, and positive signed coordinator work. It then invokes the ordinary
`sync-cancel JOB_ID` control and polls—without a fixed settling sleep—until all of these are true:

1. the same job is terminal `cancelled` and retains the same carrier incarnation;
2. no incoming offer, active receive, or paused receive remains;
3. private staging is empty and no accepted HEAD or activation exists;
4. aggregate signed route work is zero, both bulk workers remain `ready`, and the cancellation caused
   no reassignment.

The construction gate rejects a cancellation tail above 5,000 ms and records the observed monotonic
tail. Afterward the protected primary completes 40 ordered Ratox samples below 250 ms. Raw and compact
verification bind all counters, both role receipts, route class, and exact binary. Direct UDP
`pair.fpkne1pg` and forced TCP `pair.r_4luysy` pass against the same binary.

## Consequences

- Gate 4's bounded cancellation-tail row is closed for one positively progressing whole-object pull
  on this exact two-bulk-route topology and both native carrier classes.
- Local cancellation terminal-fences work instead of migrating it. Healthy auxiliary workers remain
  available, and signed work is released exactly once.
- The 5-second value is a fail-closed construction ceiling, not a production SLA. The accepted cells
  observed 70 ms over direct UDP and 80 ms over forced TCP.
- The test does not prove that the publisher receives a remote cancellation acknowledgement, byte
  prefix reuse, cancellation fairness across many simultaneous jobs, or fault ordering. It does not
  turn adaptive selection on by default.
- ADR 0173 subsequently closes one bounded eight-job small-object population/resource row. Gate 4
  remains open for randomized route startup/fault order, larger-object throughput/resource
  attribution, concurrent cancellation, and distinct-relay topology. ADR 0174 subsequently closes
  bounded four-job concurrent withdrawal while leaving cancellation during loss and common-link QoS
  open. ADR 0175 subsequently closes the exact loss→reassignment→replacement-progress→cancel order;
  opposite/simultaneous order remains open.

## Verification

The owned registry checks transfer-ID joins for object and range pulls and the content-free status
surface. `tools/run-sandwurm-pair.py` rejects a missing positive position, carrier/worker mismatch,
zero pre-cancel work, residual work, reassignment, an excessive tail, route degradation, accepted
HEAD/activation, or protected Ratox failure. `tools/verify-sandwurm-pair.py` independently replays the
secret-free compact proof and rejects altered additive fields.
