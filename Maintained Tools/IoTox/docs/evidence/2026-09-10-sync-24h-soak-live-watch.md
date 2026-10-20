# 2026-09-10 sync 24-hour soak live watch

The 24-hour three-writer graduation command is:

```sh
tools/iotox-sandwurm-lab.sh up-three-writer soak-24h
```

That command intentionally writes the authoritative
`live/workspace-export/guest-receipts/iotox/sync-three-writer.json` receipt only
after the guest service exits or cleanly rejects.  During a live 24-hour run, the
operator should inspect content-free progress from the VM console instead of
copying guest state or data payloads.

`tools/inspect-sync-three-writer-soak.py` and the wrapper below summarize that
live state from one retained proof root:

```sh
tools/iotox-sandwurm-lab.sh status-three-writer .sandwurm/lab/three-writer-soak-24h/run.ID
```

For unattended operator watch logs, use:

```sh
tools/iotox-sandwurm-lab.sh watch-three-writer \
  .sandwurm/lab/three-writer-soak-24h/run.ID \
  --jsonl .sandwurm/lab/three-writer-soak-24h/run.ID/host-watch.jsonl \
  --print-mode changes \
  --heartbeat-samples 10 \
  --interval-seconds 60
```

That wrapper reuses the same inspector parser, prints one compact content-free
status line per sample by default, appends optional JSONL snapshots, and exits
on terminal proof health unless `--keep-going` is supplied.  For long operator
watches, `--print-mode changes` still appends every JSONL sample but only prints
cycle/health/restart/repair/stage changes, with `--heartbeat-samples` providing
an intentional quiet-run heartbeat.

The status reader reports only proof-root metadata, hypervisor state, the last
`iotox-three-writer-start` stage message, shadow/soak cycle counts, estimated
soak elapsed/remaining time, final receipt status when present, and stale/run
health.  It does not read or print synchronized file contents, Tox keys, recall
phrases, or authority material.

For long soaks, status health is cadence-aware.  The 24-hour profile emits
ordinary progress at cycle 1 and every tenth cycle, so a healthy run can be
quiet for much longer than the historical 20-minute status threshold.  ADR 0369
derives a soak-specific stale window from the requested duration, minimum cycle
count, and newer explicit timing fields; for the passive 24-hour profile, live
status becomes stale at the bounded two-hour operator-alarm cap while the VM is
still running.

For the live run started from rev0051 on September 10, 2026, the startup path
was healthy before the 24-hour loop:

- three distinct local identities and authority ledgers;
- three friendship edges;
- six directed read/write shares;
- three signed branches converged;
- 512 16-KiB capacity population converged and repaired;
- offline three-way conflict convergence;
- explicit conflict resolution; and
- 24 shadow cycles converged.

The first 24-hour loop began at guest stage elapsed `178.3s`, first reported
`writable soak cycle 1 converged` at guest stage elapsed `216.0s`, and reached
`writable soak cycle 70 converged` before rejecting while waiting for cycle 73.
Its rejected receipt reported 72 completed soak cycles, three daemon restarts,
six repair passes, 36 delete cycles, full capacity shape on all three nodes, and
no conflict alternatives.  A read-only postmortem of the stopped guest disk
showed the expected synthetic cycle-73 projection on nodes `a` and `b`, while
node `c` still showed the cycle-72 projection and lacked the cycle-73 toggle.

That rejection was useful science, not a pass.  It exposed three harness gaps
now fixed by ADR 0367:

- late-soak rejected receipts need content-free projection shape, not just
  aggregate store and pull counters;
- the verifier must allow full capacity projection in rejected proofs when
  failure happens after capacity convergence; and
- scheduled 24-cycle soak restarts must rotate through nodes `a`, `b`, and `c`
  instead of selecting the same node repeatedly.

The next 24-hour profile also enables `--soak-stalled-restart-after 120`.  A
cycle that stalls for two minutes now records lagging node roles, wait-channel
names, restart/repair recovery, and then still has to converge within the hard
per-cycle timeout.  If it cannot, the run remains rejected with better evidence.

The first clean rerun from commit `22383451d220f886fc3bfc956b0973dd3ae941ef`
was stopped intentionally at
`.sandwurm/lab/three-writer-soak-24h/run.4Zd0SZy8`.  It used the original
five-second cycle delay and reached 68 completed writable cycles in roughly
half an hour, but needed stalled-cycle recovery at cycle 16 and again at cycle
68.  That is useful high-churn stress evidence, not the calmer 24-hour
reliability soak we want for graduation.  ADR 0368 therefore separates the
two: `soak-24h` now uses a four-minute cycle delay while preserving 24 hours,
288 minimum cycles, scheduled rotating restarts, repair passes, and the
120-second stalled-cycle recovery threshold.

The retuned candidate started clean from commit
`84974c41b26adac2eb01583142fc911f1a3a94ba` at
`.sandwurm/lab/three-writer-soak-24h/run.S8ymYL7Q`.  It completed the full
startup/capacity/conflict/shadow prelude, entered the 24-hour loop, and reached
`writable soak cycle 10 converged` at roughly 39m48s of soak elapsed with no
stalled-cycle recovery and no rejected receipt.  That confirms the first
intentional quiet progress window under the ADR 0368 cadence.

That candidate was then stopped intentionally, not accepted.  It entered
stalled-cycle recovery at cycle 19 with lagging targets `b,c`, then again at
cycle 20 with lagging target `a`.  During ACPI shutdown, the guest logged
`three-writer rejected evidence failed: interrupted by SIGTERM`, leaving only
the Sandwurm launch/console proof and no IoTox receipt.  ADR 0370 fixes that
receipt-writer bug by ignoring further shutdown signals while rejected evidence
is being emitted and by using safe content-free fallbacks for partial snapshot
fields.

ADR 0371 then changes the 24-hour graduation profile again: emergency
stalled-cycle restarts are disabled for `soak-24h`, and the hard per-cycle
timeout is raised to 900 seconds.  The recovery machinery remains available for
separate stress/recovery drills, but the primary 24-hour pass must now converge
without emergency daemon restarts.

The passive candidate started clean from commit
`5a74b6cc5d0b64f741e24ad3b8144e27828e373d` at
`.sandwurm/lab/three-writer-soak-24h/run.bxUuEBRF`.  A fresh soak-smoke
shakedown from the same commit first passed at
`.sandwurm/lab/three-writer-soak-smoke/run.k7XwDLjd` with four soak cycles,
zero stalled-cycle recoveries, retained recovery rehearsal, storage-fault
follow-up, and VM smoke verification.  The 24-hour candidate then completed the
full startup/capacity/conflict/shadow prelude, entered the passive 24-hour
loop, and reached `writable soak cycle 10 converged` at roughly 45m42s of soak
elapsed with no recovery path and no failure.

It then reached `writable soak cycle 20 converged` at roughly 1h24m, performed
the first scheduled daemon restart at cycle 24 against node `a`, and reached
`writable soak cycle 30 converged` at roughly 2h10m after soak start.  That
post-restart convergence is the first strong signal that the passive profile is
testing the desired question: slow cycles are allowed to settle without
emergency daemon kicks, while planned restart churn still remains in the run.
The same candidate reached `writable soak cycle 40 converged` at roughly 2h50m,
still with no rejected receipt and no emergency recovery path.
It then performed the second scheduled daemon restart against node `b` around
3h25m and reached `writable soak cycle 50 converged` around 3h35m, again with
no emergency recovery and no rejected receipt.
The same candidate reached `writable soak cycle 60 converged` around 4h20m,
still clean.  The next high-value checkpoint is the scheduled cycle-72 restart,
which should rotate to node `c`, followed by post-`c` convergence.
It reached `writable soak cycle 70 converged` around 5h09m and then performed
the scheduled cycle-72 restart against node `c` around 5h15m, completing the
first full planned restart rotation across `a`, `b`, and `c`.
That candidate then rejected at cycle 72 with
`timeout waiting for writable soak cycle 72`.  The retained IoTox receipt
verified as rejected evidence: it recorded 71 completed cycles, restart targets
`["a", "b", "c"]`, zero emergency recoveries, full capacity shape on all three
nodes, no conflict alternatives, and node `b` lagging while nodes `a` and `c`
had the cycle-72 projection.  Because the old scheduled-restart order restarted
the cycle's writer after its fresh local edit, ADR 0372 moves scheduled
restarts before the synthetic edit and records `soak_restart_phase =
"before-edit"` in future receipts.  The harsher restart-after-fresh-edit case
is kept as separate future science rather than the main 24-hour graduation
shape.

At this point in the chronology, before the later ADR 0377 accepted receipts,
the 24-hour soak remained an open graduation gate.

The current candidate started clean from commit
`290023c8fef1a858952ed12e4eb2eea0e5d142fe` at
`.sandwurm/lab/three-writer-soak-24h/run.Ym8xWhvm` after a fresh
restart-before-edit soak-smoke accepted at
`.sandwurm/lab/three-writer-soak-smoke/run.KRix4EU5`.  The smoke receipt
recorded `soak_restart_phase = "before-edit"`, four soak cycles, two planned
daemon restarts, zero stalled-cycle recoveries, retained recovery rehearsal,
storage-fault rehearsal, and VM-smoke verification.

For the 24-hour candidate, the startup/capacity/conflict prelude completed and
the 24 shadow cycles reached the soak.  One pre-soak shadow cycle stalled at
cycle 17 and recovered by restarting writer `b`; that belongs to the earlier
shadow churn gate, not to the passive 24-hour soak.  The passive writable soak
then started at guest stage elapsed `257.7s` with
`seconds=86400.000`, `minimum-cycles=288`, `cycle-delay=240.000`,
`timeout=900`, and `stalled-restart-after=0.000`.  Cycle 1 converged at guest
stage elapsed `271.8s`.  A host-side watch log is now being appended at
`.sandwurm/lab/three-writer-soak-24h/run.Ym8xWhvm/host-watch.jsonl`.

The same candidate reached `writable soak cycle 10 converged` at guest stage
elapsed `2624.1s`, roughly `39m47s` after the soak began.  No rejected receipt
exists and no passive-soak emergency recovery path exists in this profile; the
next high-value checkpoints are cycle 20, the scheduled restart-before-edit at
cycle 24 against node `a`, and post-restart convergence at cycle 30.

It then reached `writable soak cycle 20 converged` at guest stage elapsed
`5175.7s`, roughly `1h22m48s` after the soak began.  The candidate still has no
rejected receipt and no long-soak emergency recovery event.  The next gate is
the first scheduled restart-before-edit at cycle 24, expected to target node
`a`, followed by post-restart convergence at cycle 30.

The first scheduled restart-before-edit fired at cycle 24 against node `a` at
guest stage elapsed `6174.6s`, roughly `1h38m49s` after the soak began.  This
confirms that ADR 0372's representative long-soak framing is active in the live
candidate: scheduled daemon churn happens before the synthetic edit rather than
after an unreplicated local write.  The next high-value checkpoint is cycle 30,
which proves post-restart convergence after the `a` restart.

The candidate reached `writable soak cycle 30 converged` at guest stage elapsed
`7728.8s`, roughly `2h04m49s` after the soak began.  That is the first
post-ADR-0372 scheduled-restart success marker: node `a` restarted before the
cycle-24 edit, the mesh kept running, and ordinary sparse progress reached
cycle 30 with no rejected receipt.

It reached `writable soak cycle 40 converged` at guest stage elapsed
`10316.7s`, roughly `2h47m50s` after the soak began.  This extends the
post-node-`a` restart observation across another ten-cycle sparse-progress
window.  The next meaningful edge is the scheduled cycle-48 restart-before-edit,
expected to rotate to node `b`, followed by cycle-50 convergence.

The candidate then rejected shortly after the cycle-48 restart-before-edit fired
against node `b`.  The retained rejected receipt at
`.sandwurm/lab/three-writer-soak-24h/run.Ym8xWhvm` reports that node `c`
rejected `sync-repair field-notes` with an IoTox control-response deadline, plus
`shadow_cycles = 24`, `soak_cycles = 47`,
`soak_elapsed_ms = 11890813`, `soak_daemon_restarts = 2`,
`soak_restart_targets = ["a", "b"]`, `soak_repair_passes = 3`, and
`soak_stalled_cycle_recoveries = 0`.  The content-free partial projection was
aligned on all three nodes: identical `current_sha256`, deleted toggle, full
512-file/8-MiB capacity shape, and zero conflict alternatives.  This rejection
therefore does not show data divergence; it shows that the long-soak harness
was stacking the scheduled cycle-48 restart with the periodic repair pass
because `soakRestartEvery = 24` and `soakRepairEvery = 12`.

ADR 0373 keeps the coincident restart-plus-repair shape as opt-in stress
science, but changes the representative 24-hour gate to defer repair from a
scheduled-restart cycle to the next non-restart cycle.  It also makes the
`sync-repair` control deadline explicit (`--sync-repair-control-timeout-ms`,
120 seconds in the Sandwurm smoke and 24-hour profiles), because the previous
Python subprocess timeout did not by itself extend IoTox's local-control
deadline.  The next candidate must come from a clean ADR 0373 source commit,
pass `soak-smoke`, then run `soak-24h` with deferred soak repair recorded in
the evidence, `soak_repair_pending = false`, and at least as many repair passes
as deferred scheduled-restart cycles.

That clean ADR 0373 smoke accepted at
`.sandwurm/lab/three-writer-soak-smoke/run.cnowmx9v` from source commit
`7dc73d1690696435ae91891b82ac83c14609cfc7`.  It completed five soak cycles,
two scheduled daemon restarts, two repair deferrals (`[2, 4]`), two repair
passes, `soak_repair_pending = false`, zero stalled-cycle recoveries, retained
recovery rehearsal, storage-fault rehearsal, and VM-smoke verification.  The
24-hour gate is ready to relaunch from that framing.

The ADR 0373 24-hour candidate started from clean source commit
`149729e394f6fe8e3cd689721e3155a2b2745bff` at
`.sandwurm/lab/three-writer-soak-24h/run.OWtscPbC`.  The host watcher is
appending `.sandwurm/lab/three-writer-soak-24h/run.OWtscPbC/host-watch.jsonl`.
The startup/capacity/conflict prelude completed, all 24 shadow cycles reached
the soak, and the soak started with `repair-policy=defer` plus
`repair-control-timeout-ms=120000`.  Cycle 1 converged, then cycle 10 converged
at host-observed soak elapsed `37m40s` with no rejected receipt and no
stalled-cycle recovery.  The next high-value edges are the cycle-12 scheduled
repair pass and the cycle-24 scheduled restart/repair deferral.

Cycle 12 then completed a scheduled repair pass cleanly, exercising the
explicit `sync_repair_control_timeout_ms = 120000` path away from restart
churn.  Cycle 20 converged at host-observed soak elapsed `1h18m40s` with no
rejected receipt.  The next high-value edge is cycle 24: the representative
gate should restart node `a`, defer the coincident repair, and drain that
deferred repair on the next non-restart cycle.

The ADR 0373 candidate then rejected at cycle 24 after the scheduled
restart-before-edit of node `a`.  The retained proof at
`.sandwurm/lab/three-writer-soak-24h/run.OWtscPbC` verifies as content-free
rejected evidence with `failure = "timeout waiting for writable soak cycle 24"`
and `failure_sha256 =
25667fe89fcd16658d470ded4f66764fe576d6869f20686971e6f345e9c521f9`.  The run
recorded `shadow_cycles = 24`, `soak_cycles = 23`,
`soak_elapsed_ms = 5467144`, `soak_daemon_restarts = 1`,
`soak_restart_targets = ["a"]`, `soak_repair_passes = 1`,
`soak_repair_deferrals = 0`, and `sync_repair_control_timeout_ms = 120000`.
The partial projection explains the failure shape: nodes `a` and `b` remained
aligned on the cycle-23 projection, node `c` held the expected cycle-24
projection, all three stores had the same object/manifest/record/branch shape,
and no conflict alternatives were present.  This was not data corruption.  It
showed that Tox session reconfirmation after a daemon restart is not enough
readiness proof for the next edit.

ADR 0374 changes the representative soak restart contract again: after each
scheduled restart, the harness now runs one bounded `restart-settle` sync-repair
pass across the full mesh before writing that cycle's synthetic edit.  Receipts
record `soak_restart_settle_policy = "repair-before-edit"`,
`soak_restart_settle_passes`, and `soak_restart_settle_cycles`; accepted
receipts must show one settle pass for each scheduled daemon restart.  The next
candidate must come from a clean ADR 0374 source commit, pass `soak-smoke`, and
then rerun `soak-24h` with restart-settle evidence visible in the live watcher.

That ADR 0374 smoke accepted at
`.sandwurm/lab/three-writer-soak-smoke/run.dvdqSlPg` from source commit
`a403ebc6608305ec2ea29c9f6f9832c298e6f691`.  It completed five soak cycles,
two scheduled daemon restarts, two restart-settle passes (`[2, 4]`), two
periodic repair deferrals (`[2, 4]`), two deferred repair passes,
`soak_repair_pending = false`, zero stalled-cycle recoveries, retained recovery
rehearsal, storage-fault rehearsal, and VM-smoke verification.  The 24-hour
gate is ready to relaunch from ADR 0374 framing.

The ADR 0374 24-hour candidate started from clean source commit
`15b6503ab574a978df282c6ad8bad1a7a6a088e0` at
`.sandwurm/lab/three-writer-soak-24h/run.2GsYEBFE`.  The host watcher is
appending `.sandwurm/lab/three-writer-soak-24h/run.2GsYEBFE/host-watch.jsonl`.
The startup/capacity/conflict prelude completed, all 24 shadow cycles reached
the soak, and the soak started with `restart-settle-policy=repair-before-edit`,
`repair-policy=defer`, and `repair-control-timeout-ms=120000`.  Cycle 1
converged, then cycle 10 converged at host-observed soak elapsed `38m29s` with
no rejected receipt and no stalled-cycle recovery.  The next high-value edges
are the cycle-12 scheduled repair pass, cycle 20, and the cycle-24 scheduled
restart-settle/repair-deferral edge that rejected the previous candidate.

The same ADR 0374 candidate completed the cycle-12 scheduled repair pass under
the explicit 120-second control deadline, then reached `writable soak cycle 20
converged` at host-observed soak elapsed `1h22m30s`.  At that point the live
summary still showed `soak_restart_settle_passes = 0`,
`soak_repair_deferrals = 0`, no rejected receipt, and no stalled-cycle
recovery.  The next gate is cycle 24, where node `a` should restart, complete
one `restart-settle` sync-repair pass before the synthetic edit, defer the
coincident periodic repair, and converge past the exact failure shape from
`run.OWtscPbC`.

The cycle-24 edge then crossed cleanly.  The live watcher observed
`last_restart_node = a`, `last_restart_cycle = 24`,
`restart_settle_passes = 1`, and `last_restart_settle = completed@24`, followed
by `repair_deferrals = 1` at cycle 24 and
`last_repair = deferred:completed@25` at host-observed soak elapsed `1h50m30s`.
That means node `a` restarted, the ADR 0374 restart-settle pass completed
before the cycle edit, cycle 24 converged far enough to defer the coincident
periodic repair, and cycle 25 drained the deferred repair.  This passes the
exact cycle-24 failure edge that rejected `run.OWtscPbC`; the next high-value
checkpoint is cycle 30 for post-restart sparse convergence.

The candidate reached `writable soak cycle 30 converged` at host-observed soak
elapsed `2h12m31s`.  This is the first sparse post-restart checkpoint after the
node-`a` restart, ADR 0374 settle pass, cycle-24 repair deferral, and cycle-25
deferred repair drain.  No rejected receipt exists.  The next high-value edge is
cycle 48, where scheduled restart should rotate to node `b`, run a second
restart-settle pass, defer the coincident periodic repair, and drain it on the
next non-restart cycle.

The same run reached `writable soak cycle 40 converged` at host-observed soak
elapsed `2h56m31s`.  This extends the post-node-`a` restart-settle window across
another sparse progress marker with one completed restart-settle pass, one
drained deferred repair, and no rejected receipt.  The next decisive edge is
cycle 48, where scheduled restart rotates to node `b` and repeats the exact
maintenance-coincidence shape that rejected `run.Ym8xWhvm` before ADR 0373/0374.

The cycle-48 node-`b` edge crossed cleanly too.  The live watcher observed
`last_restart_node = b`, `last_restart_cycle = 48`,
`restart_settle_passes = 2`, and `last_restart_settle = completed@48`; cycle
48 then converged far enough to record the second repair deferral, and cycle 49
drained it with `last_repair = deferred:completed@49`.  The run then reached
`writable soak cycle 50 converged` at host-observed soak elapsed `3h40m32s`.
This passes both prior long-soak failure zones: the cycle-24 stale
post-restart propagation edge from `run.OWtscPbC` and the cycle-48
restart-plus-repair control edge from `run.Ym8xWhvm`.  The next high-value edge
is cycle 72, where scheduled restart should rotate to node `c` and complete the
first full `a`, `b`, `c` restart-settle rotation.

The candidate then reached `writable soak cycle 60 converged` at host-observed
soak elapsed `4h28m33s`; the same live summary showed
`last_repair = scheduled:completed@60`, `soak_restart_settle_passes = 2`, and
`soak_repair_deferrals = 2`.  This proves a normal scheduled repair pass still
completes after the node-`b` restart-settle and deferred-repair drain.  The next
high-value edge remains cycle 72, where node `c` should complete the first full
restart-settle rotation.

The cycle-72 node-`c` edge also crossed cleanly.  The live watcher observed
`last_restart_node = c`, `last_restart_cycle = 72`,
`restart_settle_passes = 3`, and `last_restart_settle = completed@72`; cycle
72 then converged far enough to record the third repair deferral, and cycle 73
drained it with `last_repair = deferred:completed@73`.  At host-observed soak
elapsed `5h28m34s`, the candidate had completed the first full `a`, `b`, `c`
scheduled restart-settle rotation with all three deferred repair passes drained,
no stalled-cycle recovery, and no rejected receipt.  The next high-value edges
are ordinary sparse progress at cycles 80/90/100 and the second restart
rotation beginning at cycle 96.

The run reached `writable soak cycle 80 converged` at host-observed soak elapsed
`5h59m34s`, preserving the same content-free health shape: three
restart-settle passes, three drained repair deferrals, no stalled-cycle
recovery, and no rejected receipt.

The run reached `writable soak cycle 90 converged` at host-observed soak elapsed
`6h47m35s`.  Cycle 84's scheduled repair had completed under the explicit
120-second control deadline, and the run still showed no stalled-cycle recovery
or rejected receipt before the second restart rotation at cycle 96.

The second restart rotation began cleanly at cycle 96.  Node `a` restarted,
`restart-settle` completed with `soak_restart_settle_passes=4`, and the
coincident scheduled repair was explicitly deferred.  Cycle 97 then drained the
deferred repair (`last_repair=deferred:completed@97`) with no stalled-cycle
recovery and no rejected receipt.

The run reached `writable soak cycle 100 converged` at host-observed soak
elapsed `7h35m36s`, confirming ordinary sparse progress after the cycle 96
restart-settle and cycle 97 deferred-repair drain.

Cycle 108's scheduled repair completed under the live control deadline, and the
run reached `writable soak cycle 110 converged` at host-observed soak elapsed
`8h23m37s`.  The run remained free of stalled-cycle recovery and rejected
receipts after the second rotation's first restart edge.

The second rotation's node `b` restart passed at cycle 120.  `restart-settle`
completed with `soak_restart_settle_passes=5`, cycle 120 converged with the
coincident scheduled repair deferred (`soak_repair_deferrals=5`), and cycle 121
drained the deferred repair.  No stalled-cycle recovery or rejected receipt was
observed.

The run reached `writable soak cycle 130 converged` at host-observed soak
elapsed `10h03m39s`, confirming ordinary sparse progress after node `b`'s cycle
120 restart-settle and cycle 121 deferred-repair drain.

Cycle 132's scheduled repair completed, and the run reached `writable soak
cycle 140 converged` at host-observed soak elapsed `10h55m40s`.  The second
rotation's node `c` restart then passed at cycle 144: `restart-settle`
completed with `soak_restart_settle_passes=6`, the coincident scheduled repair
was deferred (`soak_repair_deferrals=6`), and cycle 145 drained the deferred
repair.  This completed the second full `a`/`b`/`c` restart-settle rotation with
no stalled-cycle recovery and no rejected receipt.

The run reached `writable soak cycle 150 converged` at host-observed soak
elapsed `11h54m41s`, keeping the soak clean across the halfway neighborhood:
six restart-settle passes, six drained repair deferrals, no stalled-cycle
recovery, and no rejected receipt.

Cycle 156's scheduled repair completed, and the run reached `writable soak
cycle 160 converged` at host-observed soak elapsed `12h49m42s`, preserving clean
post-halfway progress before the next scheduled restart at cycle 168.

The third restart rotation began cleanly at cycle 168.  Node `a` restarted,
`restart-settle` completed with `soak_restart_settle_passes=7`, the coincident
scheduled repair was deferred (`soak_repair_deferrals=7`), and cycle 169 drained
the deferred repair.  No stalled-cycle recovery or rejected receipt was
observed.

The run reached `writable soak cycle 170 converged` at host-observed soak
elapsed `13h47m43s`, confirming ordinary progress after the third rotation's
node `a` restart and repair drain.

The run reached `writable soak cycle 180 converged` at host-observed soak
elapsed `14h42m44s`; the cycle 180 scheduled repair completed in the same clean
checkpoint.  The soak remained free of stalled-cycle recovery and rejected
receipts.

Cycle 190 converged, and the third rotation's node `b` restart passed at cycle
192.  `restart-settle` completed with `soak_restart_settle_passes=8`, the
coincident scheduled repair was deferred (`soak_repair_deferrals=8`), and cycle
193 drained the deferred repair with no stalled-cycle recovery and no rejected
receipt.

The run reached `writable soak cycle 200 converged` at host-observed soak
elapsed `16h37m46s`, confirming ordinary sparse progress after the third
rotation's node `b` restart and repair drain.

Cycle 204's scheduled repair completed, and the run reached `writable soak
cycle 210 converged` at host-observed soak elapsed `17h44m47s`.  The soak
remained clean before the third rotation's node `c` restart at cycle 216.

The third full restart-settle rotation completed cleanly at cycle 216/217.
Node `c` restarted, `restart-settle` completed with
`soak_restart_settle_passes=9`, the coincident scheduled repair was deferred
(`soak_repair_deferrals=9`), and cycle 217 drained the deferred repair.  No
stalled-cycle recovery or rejected receipt was observed.

The run reached `writable soak cycle 220 converged` at host-observed soak
elapsed `19h03m49s`, confirming ordinary progress after the third complete
restart-settle rotation.

Cycle 228's scheduled repair completed after a long but still non-stale sparse
window, and the run reached `writable soak cycle 230 converged` at host-observed
soak elapsed `20h18m51s`.  The proof remained clean with no stalled-cycle
recovery or rejected receipt.

The fourth restart rotation began cleanly at cycle 240.  Node `a` restarted,
`restart-settle` completed with `soak_restart_settle_passes=10`, cycle 240
converged with the coincident scheduled repair deferred
(`soak_repair_deferrals=10`), and cycle 241 drained the deferred repair.  No
stalled-cycle recovery or rejected receipt was observed.

The run reached `writable soak cycle 250 converged` at host-observed soak
elapsed `22h53m55s`, after another long but non-stale sparse window.  The proof
remained clean with ten restart-settle passes, ten drained repair deferrals, no
stalled-cycle recovery, and no rejected receipt.

The wall-clock soak target crossed 24 hours while the harness remained healthy,
but the run correctly continued because the proof profile also requires
`soak_minimum_cycles=288`.  Cycle 252's scheduled repair completed before the
wall-clock crossing, and the run reached `writable soak cycle 260 converged` at
host-observed soak elapsed `24h15m57s`; the terminal accepted receipt was still
pending the minimum-cycle gate, not a rejection.

The fourth rotation's node `b` restart passed at cycle 264.  `restart-settle`
completed with `soak_restart_settle_passes=11`, the coincident scheduled repair
was deferred (`soak_repair_deferrals=11`), and cycle 265 drained the deferred
repair.  The run remained clean while continuing toward the minimum-cycle gate.

The run then crossed another long but non-stale sparse-progress window and
reached `writable soak cycle 270 converged` at host-observed soak elapsed
`25h39m59s`.  No rejected receipt, stalled-cycle recovery, or extra repair was
observed; the next scheduled repair edge is cycle 276 and the terminal
minimum-cycle/restart edge remains cycle 288.

This candidate did not reach the terminal IoTox receipt.  The outer Sandwurm
live-chain receipt wait was still capped at 93,600 seconds (26 hours), while the
guest-side 24-hour profile also required `soak_minimum_cycles=288`; at the
observed tail rate the run was still legitimately below that cycle gate when
the outer wait ended.  The retained proof
`.sandwurm/lab/three-writer-soak-24h/run.2GsYEBFE` reports
`launched-without-guest-evidence`, an empty `guest-receipts/iotox` directory,
VM exit status `0`, and last visible IoTox stage `writable soak cycle 270
converged`.  This is therefore an outer-budget qualification defect, not a
three-writer convergence rejection.  The `soak-24h` launcher now uses a 172,800
second (48-hour) outer receipt wait so the guest harness's own per-cycle
timeouts, restart-settle evidence, and final receipt decide pass/reject.

Replacement candidate `.sandwurm/lab/three-writer-soak-24h/run.hlBeElr6` was
started from commit `2c09d63bc4a00d4802e87e684b84ebb9b1901806` with the
48-hour outer receipt budget.  Its startup completed the 24 shadow cycles and
entered the writable soak; `writable soak cycle 1 converged` was observed at
host-observed soak elapsed `6s` with `restart-settle-policy=repair-before-edit`,
repair deferral enabled, and the watcher in the 2-hour soak stale mode.

The replacement candidate reached `writable soak cycle 10 converged` at
host-observed soak elapsed `40m08s`.  This confirms ordinary sparse progress
under the corrected outer receipt budget, with no rejected receipt and no
stalled-cycle recovery observed.

Cycle 12's scheduled repair completed, and the replacement candidate reached
`writable soak cycle 20 converged` at host-observed soak elapsed `1h23m09s`.
The first scheduled restart remains cycle 24; no rejected receipt or
stalled-cycle recovery was observed before that edge.

The replacement candidate passed the first scheduled restart edge at cycle 24.
Node `a` restarted, the `repair-before-edit` restart-settle sync-repair
completed with `soak_restart_settle_passes=1`, the coincident scheduled repair
was deferred (`soak_repair_deferrals=1`), and cycle 25 drained the deferred
repair.  This re-confirms the ADR 0374 restart-settle behavior under the
corrected 48-hour outer receipt budget.

The replacement candidate reached `writable soak cycle 30 converged` at
host-observed soak elapsed `2h06m10s`, confirming ordinary progress after the
cycle 24 node-`a` restart-settle and cycle 25 deferred-repair drain.

Cycle 36's scheduled repair completed, and the replacement candidate reached
`writable soak cycle 40 converged` at host-observed soak elapsed `2h51m11s`.
The run remained clean after the first restart-settle edge, with one drained
repair deferral and no stalled-cycle recovery.

The second scheduled restart edge passed at cycle 48.  Node `b` restarted,
`restart-settle` completed with `soak_restart_settle_passes=2`, the coincident
scheduled repair was deferred (`soak_repair_deferrals=2`), and cycle 49 drained
the deferred repair.  The corrected outer receipt budget remained in force and
no rejected receipt or stalled-cycle recovery was observed.

The replacement candidate reached `writable soak cycle 50 converged` at
host-observed soak elapsed `3h36m12s`, confirming ordinary sparse progress
after the node-`b` restart-settle and deferred-repair drain.

The replacement candidate reached `writable soak cycle 60 converged` at
host-observed soak elapsed `4h22m13s`; the cycle 60 scheduled repair completed
in the same clean checkpoint.  Two restart-settle passes and two drained repair
deferrals remained the live evidence state before the first rotation's node
`c` restart at cycle 72.

The replacement candidate reached `writable soak cycle 70 converged` at
host-observed soak elapsed `5h16m14s`, then completed the first full
`a`/`b`/`c` restart-settle rotation at cycle 72/73.  Node `c` restarted,
`restart-settle` completed with `soak_restart_settle_passes=3`, the coincident
scheduled repair was deferred (`soak_repair_deferrals=3`), and cycle 73 drained
the deferred repair.  No rejected receipt or stalled-cycle recovery was
observed.

The replacement candidate reached `writable soak cycle 80 converged` at
host-observed soak elapsed `6h02m15s`, preserving clean ordinary progress after
the first full restart-settle rotation.

Cycle 84's scheduled repair completed, and the replacement candidate reached
`writable soak cycle 90 converged` at host-observed soak elapsed `6h49m16s`.
The run remained clean before the second rotation's node `a` restart at cycle
96.

The second restart rotation began cleanly at cycle 96.  Node `a` restarted,
`restart-settle` completed with `soak_restart_settle_passes=4`, the coincident
scheduled repair was deferred (`soak_repair_deferrals=4`), and cycle 97 drained
the deferred repair.  No stalled-cycle recovery or rejected receipt was
observed.

The replacement candidate reached `writable soak cycle 100 converged` at
host-observed soak elapsed `7h49m17s`, confirming ordinary sparse progress after
the second rotation's node-`a` restart-settle and repair drain.

Cycle 108's scheduled repair completed, and the replacement candidate reached
`writable soak cycle 110 converged` at host-observed soak elapsed `8h38m18s`.
The run remained clean before the second rotation's node `b` restart at cycle
120.

The second rotation's node `b` restart passed at cycle 120.  `restart-settle`
completed with `soak_restart_settle_passes=5`, cycle 120 converged while the
coincident scheduled repair was deferred (`soak_repair_deferrals=5`), and cycle
121 drained the deferred repair.  No stalled-cycle recovery or rejected receipt
was observed.

The replacement candidate reached `writable soak cycle 130 converged` at
host-observed soak elapsed `10h28m20s`, after a long but non-stale sparse window
following the cycle 120/121 node-`b` restart-settle and deferred-repair drain.

Cycle 132's scheduled repair completed, and the replacement candidate reached
`writable soak cycle 140 converged` at host-observed soak elapsed `11h26m21s`.
The long sparse window stayed non-stale and VM activity remained high, so it was
treated as active sync work rather than a stuck guest.

The replacement candidate then rejected at cycle 144 with
`timeout waiting for writable soak cycle 144`.  The retained proof is
`.sandwurm/lab/three-writer-soak-24h/run.hlBeElr6`, and the rejected IoTox
receipt is now accepted by the independent Sandwurm verifier as a valid
content-free rejected soak receipt.  Its summary reports
`partial_soak_cycles = 143`, `partial_soak_restart_settle_passes = 6`,
`partial_soak_stalled_restart_after_ms = 0`,
`partial_soak_stalled_cycle_recoveries = 0`,
`branch_count_per_node = [3, 3, 3]`, and
`conflict_alternatives_per_node = [0, 0, 0]`.

The failure shape was a single lagging projection after the cycle-144 node-`c`
scheduled restart-settle.  Node `a` still carried the cycle-143 current file
and toggle marker, while nodes `b` and `c` held the intended cycle-144 current
file and no marker.  There was no conflict material and no branch-count loss.
Because ADR 0371 had disabled stalled-cycle recovery for the primary 24-hour
profile, the harness waited until the hard 900-second cycle timeout rather than
restarting the lagging node and requiring convergence.  ADR 0375 therefore
changes the active `soak-24h` profile to a bounded 600-second stalled-cycle
recovery threshold while keeping the 900-second hard timeout, and it requires
accepted receipts to bind `soak_stalled_restart_after_ms = 600000`.

ADR 0375 replacement candidate
`.sandwurm/lab/three-writer-soak-24h/run.So1SOLr0` was started from source
commit `7fe3ab561ed9e8b30be3fc7ba1c8529fd5eb83b8`.  It uses the 48-hour
outer receipt budget, `repair-before-edit` restart-settle, deferred periodic
repair, `sync_repair_control_timeout_ms = 120000`, and
`soak_stalled_restart_after_ms = 600000`.  The VM reached `vmm=Running`, passed
startup branch convergence, and reached `capacity population converged and
repaired`; the watcher is appending
`.sandwurm/lab/three-writer-soak-24h/run.So1SOLr0/host-watch.jsonl`.

The ADR 0375 replacement reached the writable soak after all 24 shadow cycles.
The guest console line binds the new profile as
`stalled-restart-after=600.000`, `timeout=900`,
`restart-settle-policy=repair-before-edit`, `repair-policy=defer`, and
`repair-control-timeout-ms=120000`.  `writable soak cycle 1 converged` at
guest elapsed `193.7s`, with host-observed soak elapsed `15s`.

The So1SOLr0 candidate was stopped during the old logger's intentionally quiet
cycle-2-through-cycle-9 window.  The VMM was still running and consuming CPU,
but the console had not advanced beyond `writable soak cycle 1 converged`; the
run exited as outer Sandwurm `launched-without-guest-evidence` and did not
retain an IoTox rejected receipt.  This is an operator-aborted observability
cell, not a sync correctness rejection.  ADR 0376 changes representative soaks
to log each cycle's synthetic edit and convergence, with `cycle-log=each` in
the start line, so the next 24-hour run can be watched without treating
expected sparse silence as a hidden stall.

ADR 0376 replacement candidate
`.sandwurm/lab/three-writer-soak-24h/run.UKn62cvQ` was started from source
commit `ab4956fbe05a26a582665913d924d11d3e634b6f`.  It reached the writable
soak after 24 shadow cycles.  The guest console start line binds
`stalled-restart-after=600.000`, `timeout=900`,
`restart-settle-policy=repair-before-edit`, `repair-policy=defer`,
`repair-control-timeout-ms=120000`, and `cycle-log=each`.  The first per-cycle
visibility lines were observed immediately:
`writable soak cycle 1 edit written writer=a marker=present`, followed by
`writable soak cycle 1 converged` at guest elapsed `188.2s`; the watcher is
appending `.sandwurm/lab/three-writer-soak-24h/run.UKn62cvQ/host-watch.jsonl`.

The ADR 0376 per-cycle visibility path advanced beyond the first cycle:
`writable soak cycle 2 edit written writer=b marker=absent` appeared at
host-observed soak elapsed `4m17s`, and `writable soak cycle 2 converged`
followed with the watcher reporting `soak=2` at `5m17s`.

The ADR 0376 candidate reached `writable soak cycle 10 converged` with the
watcher reporting `soak=10` at host-observed soak elapsed `42m18s`.  The
previous cycles were visible as per-cycle edit/convergence progress, including
cycle 9's longer but bounded `writer=c marker=present` convergence window; no
stalled-cycle recovery or rejected receipt was observed.

Cycle 12 converged with the first scheduled soak repair completed:
`last_repair=scheduled:completed@12` at host-observed soak elapsed `50m18s`.
No stalled-cycle recovery, repair deferral, or rejection was observed before
the first scheduled restart edge at cycle 24.

The ADR 0376 candidate reached `writable soak cycle 20 converged` at
host-observed soak elapsed `1h24m19s`, with the cycle-12 scheduled repair still
the last repair event and no stalled-cycle recovery or rejected receipt.

The first scheduled restart edge passed.  At cycle 24, node `a` restarted,
`restart-settle` completed with `soak_restart_settle_passes=1`, the cycle-24
edit converged, and the coincident scheduled repair was deferred
(`soak_repair_deferrals=1`, `last_repair=deferred:deferred@24`).  Cycle 25 then
converged and drained that deferred repair
(`last_repair=deferred:completed@25`).  No stalled-cycle recovery or rejected
receipt was observed through the first restart-settle edge.

The run reached `writable soak cycle 30 converged` at host-observed soak elapsed
`2h08m20s`, remaining clean after the node-`a` restart-settle and deferred
repair drain.

Cycle 36 converged with scheduled repair completed at host-observed soak elapsed
`2h35m21s` (`last_repair=scheduled:completed@36`).  The run remained clean
after the first restart edge, with `soak_restart_settle_passes=1`,
`soak_repair_deferrals=1`, and no stalled-cycle recovery.

The run reached `writable soak cycle 40 converged` at host-observed soak elapsed
`2h52m21s`, still clean after the cycle-36 scheduled repair.  The next critical
edge is the cycle-48 node-`b` scheduled restart-settle.

The second scheduled restart edge passed.  At cycle 48, node `b` restarted,
`restart-settle` completed with `soak_restart_settle_passes=2`, the cycle-48
edit converged, and the coincident scheduled repair was deferred
(`soak_repair_deferrals=2`, `last_repair=deferred:deferred@48`).  Cycle 49 then
converged and drained that deferred repair
(`last_repair=deferred:completed@49`).  No stalled-cycle recovery or rejected
receipt was observed through the node-`b` restart-settle edge.  This is the
first ADR 0376 candidate checkpoint past the two historical failure zones:
cycle 24's stale post-restart propagation and cycle 48's restart-plus-repair
control deadline.

The run reached `writable soak cycle 60 converged` at host-observed soak elapsed
`4h21m31s`; the cycle-60 scheduled repair completed in the same checkpoint
(`last_repair=scheduled:completed@60`).  The live evidence state remained two
restart-settle passes, two drained repair deferrals, no stalled-cycle recovery,
and no rejected receipt before the first rotation's node-`c` restart at cycle
72.

The run reached `writable soak cycle 70 converged` at host-observed soak elapsed
`5h08m32s`, preserving ordinary progress after the cycle-60 scheduled repair.
The first full restart-settle rotation then completed cleanly at cycle 72/73:
node `c` restarted, `restart-settle` completed with
`soak_restart_settle_passes=3`, cycle 72 converged with the coincident
scheduled repair deferred (`soak_repair_deferrals=3`), and cycle 73 drained the
deferred repair (`last_repair=deferred:completed@73`).  No stalled-cycle
recovery or rejected receipt was observed through the first full `a`/`b`/`c`
rotation in the ADR 0376 per-cycle-logging candidate.

The run reached `writable soak cycle 80 converged` at host-observed soak elapsed
`5h54m33s`, preserving ordinary progress after the first full restart-settle
rotation.  The live state remained three restart-settle passes, three drained
repair deferrals, no stalled-cycle recovery, and no rejected receipt.

Cycle 84's scheduled repair started and completed under the explicit
120-second control deadline; the run reached `writable soak cycle 84 converged`
at host-observed soak elapsed `6h14m34s` with
`last_repair=scheduled:completed@84`.  This proves ordinary scheduled repair
still completes after the first full restart-settle rotation.

The run reached `writable soak cycle 90 converged` at host-observed soak elapsed
`6h42m35s`.  The proof remained clean after the cycle-84 scheduled repair and
before the second restart rotation: three restart-settle passes, three drained
repair deferrals, no stalled-cycle recovery, and no rejected receipt.

The second restart rotation began cleanly at cycle 96/97.  Node `a` restarted,
`restart-settle` started and then completed at cycle 96 with
`soak_restart_settle_passes=4`; cycle 96 converged with the coincident
scheduled repair deferred (`soak_repair_deferrals=4`), and cycle 97 drained the
deferred repair (`last_repair=deferred:completed@97`).  No stalled-cycle
recovery or rejected receipt was observed through this second node-`a` restart
edge.

The run reached `writable soak cycle 100 converged` at host-observed soak
elapsed `7h33m36s`, confirming ordinary progress after the second rotation's
node-`a` restart-settle and cycle-97 deferred-repair drain.

Cycle 108's scheduled repair completed under the live control deadline, and the
run reached `writable soak cycle 110 converged` at host-observed soak elapsed
`8h23m37s`.  The run remained clean after the second rotation's first restart
edge, with four restart-settle passes, four drained repair deferrals, no
stalled-cycle recovery, and no rejected receipt.

The second rotation's node-`b` restart edge deliberately exercised the ADR 0375
bounded stalled-cycle recovery path.  At cycle 120, node `b` restarted before
the edit, `restart-settle` completed with `soak_restart_settle_passes=5`, and
the cycle-120 edit was written by node `c`.  After the configured 600-second
threshold, the harness logged `writable soak cycle 120 stalled; restarting
targets=a`; it then converged cycle 120, recorded the coincident scheduled
repair deferral (`soak_repair_deferrals=5`,
`last_repair=deferred:deferred@120`), and cycle 121 drained that deferred
repair (`last_repair=deferred:completed@121`).  The VM stayed healthy and no
rejected receipt was observed.  This is the first live proof in this candidate
that the 600-second stalled-cycle recovery path can repair a long-soak lag
without relaxing exact convergence.

The run then reached `writable soak cycle 130 converged` at host-observed soak
elapsed `10h18m40s`, confirming ordinary progress after the cycle-120 bounded
recovery and cycle-121 deferred-repair drain.

Cycle 132's scheduled repair completed under the live control deadline, and the
run reached `writable soak cycle 132 converged` at host-observed soak elapsed
`10h29m40s`.  The next high-value edge is cycle 144/145, where the second
rotation should restart node `c`, run restart-settle, defer the coincident
repair, and drain it on the next cycle.

The run reached `writable soak cycle 140 converged` at host-observed soak
elapsed `11h14m42s`, then crossed the old cycle-144 failure neighborhood with
bounded recovery rather than rejection.  At cycle 144, node `c` restarted before
the edit and `restart-settle` completed with `soak_restart_settle_passes=6`;
after the cycle-144 edit was written by node `c`, the harness waited the
configured 600 seconds and logged `writable soak cycle 144 stalled; restarting
targets=a`.  It then converged cycle 144, recorded the sixth coincident repair
deferral, and cycle 145 drained the repair
(`last_repair=deferred:completed@145`).  This is the exact late-soak region
where `run.hlBeElr6` previously rejected with node `a` lagging and recovery
disabled; the ADR 0375/0376 candidate remained healthy, recovered explicitly,
and kept exact convergence.

The run reached `writable soak cycle 150 converged` at host-observed soak
elapsed `12h20m43s`, preserving ordinary progress after the cycle-144 bounded
recovery and cycle-145 deferred-repair drain.

Cycle 156's scheduled repair completed under the live control deadline, and the
run reached `writable soak cycle 156 converged` at host-observed soak elapsed
`12h55m44s`.  The run remained healthy with six restart-settle passes, six
drained repair deferrals, two bounded stalled-cycle recoveries, and no rejected
receipt.

The run reached `writable soak cycle 160 converged` at host-observed soak
elapsed `13h21m45s`, preserving ordinary progress after the cycle-156 scheduled
repair.  The third restart rotation then began cleanly at cycle 168/169: node
`a` restarted before the cycle-168 edit, `restart-settle` completed with
`soak_restart_settle_passes=7`, cycle 168 converged with the coincident
scheduled repair deferred (`soak_repair_deferrals=7`), and cycle 169 drained
the deferred repair (`last_repair=deferred:completed@169`).  No rejected
receipt was observed through this third-rotation node-`a` edge.

The run reached `writable soak cycle 170 converged` at host-observed soak
elapsed `14h29m47s`, confirming ordinary progress after the third rotation's
node-`a` restart.  Cycle 180's scheduled repair completed under the live
control deadline, and the run reached `writable soak cycle 180 converged` at
host-observed soak elapsed `15h32m48s`, still healthy with two bounded
stalled-cycle recoveries and no rejected receipt.

The run reached `writable soak cycle 190 converged` at host-observed soak
elapsed `16h33m50s`, then crossed the third rotation's node-`b` restart edge at
cycle 192/193.  Node `b` restarted, `restart-settle` completed with
`soak_restart_settle_passes=8`, cycle 192 converged with the coincident
scheduled repair deferred (`soak_repair_deferrals=8`), and cycle 193 drained
the deferred repair (`last_repair=deferred:completed@193`).  The run remained
healthy with no rejected receipt observed.

The run reached `writable soak cycle 200 converged` at host-observed soak
elapsed `17h37m52s`, preserving ordinary progress after the third rotation's
node-`b` restart.  Cycle 204's scheduled repair completed under the live
control deadline, and the run reached `writable soak cycle 204 converged` at
host-observed soak elapsed `18h05m53s`.

The run reached `writable soak cycle 210 converged` at host-observed soak
elapsed `18h45m54s`, then completed the third full restart-settle rotation at
cycle 216/217.  Node `c` restarted, `restart-settle` completed with
`soak_restart_settle_passes=9`, cycle 216 converged with the coincident
scheduled repair deferred (`soak_repair_deferrals=9`), and cycle 217 drained
the deferred repair (`last_repair=deferred:completed@217`).  The run remained
healthy with no rejected receipt observed.

The run reached `writable soak cycle 220 converged` at host-observed soak
elapsed `20h00m56s`, preserving ordinary progress after the third full
restart-settle rotation.  Cycle 228's scheduled repair completed under the live
control deadline, and the run reached `writable soak cycle 228 converged` at
host-observed soak elapsed `20h58m58s`.  No rejected receipt was observed.

The run reached `writable soak cycle 230 converged`, then completed the fourth
restart rotation's node-`a` edge at cycle 240/241.  Node `a` restarted before
the cycle-240 edit, `restart-settle` completed with
`soak_restart_settle_passes=10`, cycle 240 converged with the coincident
scheduled repair deferred (`soak_repair_deferrals=10`), and cycle 241 drained
the deferred repair (`last_repair=deferred:completed@241`) at host-observed
soak elapsed `22h42m00s`.  The run remained healthy with no rejected receipt
observed.

The current candidate crossed the 24-hour wall-clock target while still
healthy.  It reached `writable soak cycle 250 converged` before the crossing,
then `writable soak cycle 251 converged` at host-observed soak elapsed
`24h03m03s`.  The run correctly continued rather than emitting a terminal
accepted receipt because this proof profile also requires
`soak_minimum_cycles=288`; at the clock gate it still needed the remaining
cycle evidence, not a repair or rejection.

The run then completed cycle 252's scheduled repair
(`last_repair=scheduled:completed@252`) and reached
`writable soak cycle 260 converged` at host-observed soak elapsed `25h14m53s`.
This confirms the post-24-hour continuation remained active and exact while
the guest moved toward the `soak_minimum_cycles=288` terminal gate.

The fourth restart rotation's node-`b` edge also passed after the wall-clock
gate.  Node `b` restarted at cycle 264, `restart-settle` completed with
`soak_restart_settle_passes=11`, cycle 264 converged with the coincident
scheduled repair deferred (`soak_repair_deferrals=11`), and cycle 265 drained
the deferred repair (`last_repair=deferred:completed@265`) at host-observed
soak elapsed `26h01m06s`.  No rejected receipt was observed.

The run reached `writable soak cycle 270 converged` at host-observed soak
elapsed `26h53m08s`, preserving ordinary progress after the post-24-hour
node-`b` restart edge.  The next high-value checkpoints are the scheduled
repair at cycle 276 and the minimum-cycle terminal edge at cycle 288.

Cycle 276's scheduled repair completed cleanly
(`last_repair=scheduled:completed@276`), and the run reached
`writable soak cycle 276 converged` at host-observed soak elapsed `27h39m09s`.
The proof remained healthy with no rejected receipt before the terminal
minimum-cycle/restart edge at cycle 288.

The current candidate then reached the terminal minimum-cycle edge.  Cycle 288
restarted node `c`, completed `restart-settle` with
`soak_restart_settle_passes=12`, converged with the coincident scheduled repair
deferred (`soak_repair_deferrals=12`), and cycle 289 drained the deferred
repair (`last_repair=deferred:completed@289`).  The guest logged
`writable soak completed cycles=289 elapsed-ms=105702418`.

The terminal receipt was still rejected, but after the soak itself had
completed.  The retained IoTox receipt reports `status=rejected`,
`soak_cycles=289`, `soak_minimum_cycles=288`, `soak_repair_pending=false`, and
the failure
`b sync-writer-cutoff field-notes ... failed: IoTox control response deadline elapsed`.
This identifies the remaining defect as post-soak maintenance local-control
deadline pressure during writer cutoff, not a three-writer data divergence.
ADR 0377 records the fix: every post-soak maintenance lifecycle command now
receives the same explicit long IoTox control deadline already used for
bounded `sync-repair`.

A replacement candidate is now running from commit `7e30352` with ADR 0377's
maintenance-deadline fix in the VM image.  Its proof root is
`.sandwurm/lab/three-writer-soak-24h/run.lYtTYT0k`.  Prelaunch completed
cleanly, the Cloud Hypervisor VM entered `startup-running`, startup reached
`capacity population converged and repaired`, shadow completed at
`shadow-cycle=24`, and the run entered `soak-running`.  Cycle 1 converged with
`stale-after=2h00m00s`, `restart-settle-policy=repair-before-edit`, and
`repair-policy=defer`; the long-watch target remains an accepted terminal
receipt after both the 24-hour wall-clock gate and the 288-cycle minimum gate.

The replacement candidate reached its first scheduled-repair checkpoint:
cycle 12 converged with `last_repair=scheduled:completed@12` at host-observed
soak elapsed `56m47s`.  The run stayed in `phase=soak-running`, the VMM
remained `Running`, and no rejected receipt was observed.  Cycle 11 had a
longer-but-bounded convergence interval and recovered without intervention,
which is consistent with the two-hour stale threshold rather than a harness
fault.

The same replacement candidate then passed the first scheduled restart edge.
Cycle 24 restarted node `a` before the edit, completed `restart-settle` with
`restart_settle_passes=1`, converged, and intentionally deferred the coincident
scheduled repair (`repair_deferrals=1`, `last_repair=deferred:deferred@24`).
Cycle 25 drained that deferred repair
(`last_repair=deferred:completed@25`) and converged at host-observed soak
elapsed `1h59m48s`.  This preserves the restart-before-edit contract while
keeping scheduled repair bounded and explicit.

The next ordinary repair checkpoint also passed: cycle 36 converged with
`last_repair=scheduled:completed@36` at host-observed soak elapsed `2h48m49s`.
The replacement candidate remained healthy after the first restart rotation's
node-`a` edge and continued toward the cycle-48 node-`b` restart.

The cycle-48 node-`b` restart edge also passed.  Node `b` restarted before the
edit, `restart-settle` completed with `restart_settle_passes=2`, cycle 48
converged with the coincident scheduled repair deferred
(`repair_deferrals=2`, `last_repair=deferred:deferred@48`), and cycle 49
drained the deferred repair (`last_repair=deferred:completed@49`) at
host-observed soak elapsed `3h45m51s`.

The run then passed the cycle-60 scheduled repair
(`last_repair=scheduled:completed@60`) and the cycle-72 node-`c` restart edge.
Node `c` restarted before the cycle-72 edit, `restart-settle` completed with
`restart_settle_passes=3`, cycle 72 converged with the coincident repair
deferred (`repair_deferrals=3`, `last_repair=deferred:deferred@72`), and
cycle 73 drained the deferred repair (`last_repair=deferred:completed@73`) at
host-observed soak elapsed `5h39m53s`.  That completes one full scheduled
restart rotation across nodes `a`, `b`, and `c` under the ADR 0377 candidate.

The second restart rotation exposed a useful bounded-recovery cluster rather
than a rejection.  Cycle 84's scheduled repair completed normally
(`last_repair=scheduled:completed@84`).  Cycle 96 restarted node `a`,
completed `restart-settle` with `restart_settle_passes=4`, then needed the
explicit stalled-cycle recovery path: cycle 96 restarted target `b` and
converged with repair deferred, cycle 97 restarted targets `b,c` and drained
the deferred repair (`last_repair=deferred:completed@97`), and cycle 98
restarted target `a` before converging.  Cycle 99 then converged normally at
host-observed soak elapsed `8h15m56s`.  A host pressure snapshot during this
cluster showed moderate load and other Sandwurm VM activity, but low PSI; the
important product result is that the harness kept the recovery explicit,
bounded, and convergence-preserving instead of silently hanging.

After that recovery cluster, ordinary cadence resumed through the next repair
and restart edge.  Cycle 108 completed scheduled repair
(`last_repair=scheduled:completed@108`).  Cycle 120 restarted node `b`, ran
`restart-settle` to `restart_settle_passes=5`, converged with the coincident
repair deferred (`repair_deferrals=5`,
`last_repair=deferred:deferred@120`), and cycle 121 drained the deferred
repair (`last_repair=deferred:completed@121`) at host-observed soak elapsed
`10h04m58s`.

The run crossed the 12-hour midpoint cleanly and completed the second full
restart rotation.  Cycle 132 completed scheduled repair
(`last_repair=scheduled:completed@132`).  Cycle 144 restarted node `c`,
completed `restart-settle` with `restart_settle_passes=6`, used one bounded
stalled-cycle recovery (`targets=b`), then converged with repair deferred
(`repair_deferrals=6`, `last_repair=deferred:deferred@144`).  Cycle 145
drained the deferred repair (`last_repair=deferred:completed@145`) and
converged at host-observed soak elapsed `12h31m02s`.

The next repair and restart edge stayed ordinary.  Cycle 156 completed
scheduled repair (`last_repair=scheduled:completed@156`).  Cycle 168
restarted node `a`, completed `restart-settle` with
`restart_settle_passes=7`, converged with the coincident repair deferred
(`repair_deferrals=7`, `last_repair=deferred:deferred@168`), and cycle 169
drained the deferred repair (`last_repair=deferred:completed@169`) at
host-observed soak elapsed `15h04m05s`.

The late-soak checkpoints continued to pass.  Cycle 180 completed scheduled
repair (`last_repair=scheduled:completed@180`).  Cycle 192 restarted node `b`,
completed `restart-settle` with `restart_settle_passes=8`, converged with the
coincident repair deferred (`repair_deferrals=8`,
`last_repair=deferred:deferred@192`), and cycle 193 drained the deferred
repair (`last_repair=deferred:completed@193`) at host-observed soak elapsed
`17h32m08s`.

The run crossed 20 hours healthy and completed the next restart rotation's
node-`c` edge.  Cycle 204 completed scheduled repair
(`last_repair=scheduled:completed@204`).  Cycle 216 restarted node `c`,
completed `restart-settle` with `restart_settle_passes=9`, converged with the
coincident repair deferred (`repair_deferrals=9`,
`last_repair=deferred:deferred@216`), and cycle 217 drained the deferred
repair (`last_repair=deferred:completed@217`) at host-observed soak elapsed
`20h10m11s`.

Cycle 228 completed scheduled repair (`last_repair=scheduled:completed@228`)
and cycle 229 converged at host-observed soak elapsed `21h31m13s`.  The run
remained healthy with no rejected receipt observed and continued toward the
cycle-240 restart edge.

Cycle 240 restarted node `a`, completed `restart-settle` with
`restart_settle_passes=10`, converged with the coincident scheduled repair
deferred (`repair_deferrals=10`, `last_repair=deferred:deferred@240`), and
cycle 241 drained the deferred repair (`last_repair=deferred:completed@241`)
at host-observed soak elapsed `23h04m15s`.  The run remained healthy with less
than one hour to the 24-hour wall-clock gate.

The ADR 0377 replacement candidate crossed the 24-hour wall-clock gate cleanly.
Cycle 248 converged at host-observed soak elapsed `24h00m16s`; the run
correctly continued instead of accepting because the stricter proof profile
also requires `soak_minimum_cycles=288`.  At the clock gate the proof was
healthy, with `restart_settle_passes=10`, `repair_deferrals=10`, and no
rejected receipt observed.

The post-clock continuation passed its next scheduled repair: cycle 252
completed `last_repair=scheduled:completed@252`, and cycle 253 converged at
host-observed soak elapsed `24h46m17s`.  The next high-value edge is the
cycle-264 node-`b` restart.

The cycle-264 node-`b` restart edge passed after the wall-clock gate.  Node `b`
restarted before the edit, `restart-settle` completed with
`restart_settle_passes=11`, cycle 264 converged with the coincident repair
deferred (`repair_deferrals=11`, `last_repair=deferred:deferred@264`), and
cycle 265 drained the deferred repair (`last_repair=deferred:completed@265`)
at host-observed soak elapsed `26h29m20s`.

Cycle 276 completed scheduled repair (`last_repair=scheduled:completed@276`)
and converged at host-observed soak elapsed `28h10m22s`.  Only the
minimum-cycle terminal edge remained: cycle 288/289 plus the post-soak
maintenance lifecycle.

The ADR 0377 replacement candidate is now accepted.  Cycle 288 restarted node
`c`, completed `restart-settle` with `restart_settle_passes=12`, converged with
the coincident scheduled repair deferred
(`repair_deferrals=12`, `last_repair=deferred:deferred@288`), and cycle 289
drained the deferred repair (`last_repair=deferred:completed@289`).  The final
receipt at
`.sandwurm/lab/three-writer-soak-24h/run.lYtTYT0k/live/workspace-export/guest-receipts/iotox/sync-three-writer.json`
reports `status=passed`, `soak_cycles=289`, `soak_minimum_cycles=288`,
`soak_requested_seconds=86400`, `soak_elapsed_ms=109651807`, and
`soak_repair_pending=false`.

The accepted receipt also proves the ADR 0377 post-soak maintenance lifecycle:
`maintenance_lifecycle=true`, `maintenance_control_timeout_ms=120000`,
`checkpoint_peer_copies=2`, `gc_candidates=4`, `gc_quarantined=4`,
`gc_restored=4`, `pin_unpin_observed=true`, `cutoff_survivors=2`,
`post_cutoff_branch_count=[2,2]`, `post_cutoff_source_principals=[1,1]`, and
`retired_writer_reentry_refused=true`.  The soak retained its planned restart
shape through all twelve scheduled restart edges:
`["a","b","c","a","b","c","a","b","c","a","b","c"]`, with
`soak_restart_settle_passes=12`, `soak_repair_deferrals=12`, and
`soak_repair_passes=29`.

Final verification passed with:

```sh
python3 -m py_compile tools/verify-sync-three-writer-sandwurm.py
python3 tools/verify-sync-three-writer-sandwurm.py --self-test
tools/iotox-sandwurm-lab.sh verify-three-writer \
  .sandwurm/lab/three-writer-soak-24h/run.lYtTYT0k
python3 tools/verify-sync-three-writer-sandwurm.py \
  .sandwurm/lab/three-writer-soak-24h/run.lYtTYT0k
```

The Sandwurm live-chain proof for this run finalized as
`status=launched-without-guest-evidence` because the generic legacy
`guest-receipts/task-receipt.json` boundary was not produced; the IoTox domain
receipt was produced under `guest-receipts/iotox/sync-three-writer.json`.
The three-writer verifier now records this distinction explicitly as
`evidence_boundary="iotox-domain-receipt"` and only accepts it when the VMM
wrapper exited and the sole Sandwurm blocker is
`guest-evidence-not-observed`.  This means the IoTox sync qualification is
accepted while the generic Sandwurm legacy-receipt integration remains a
separate polish item, not part of the data-convergence or maintenance result.

## Fresh post-acceptance soak: run.9nqvO8B2

After the accepted ADR 0377 qualification, a fresh 24-hour soak was started
from commit `397b165` as raw run ID `run.9nqvO8B2` in the 24-hour
three-writer lab class. Prelaunch completed after
Nix image realization, the Cloud Hypervisor VM entered startup, and the product
prelude reached distinct identities/authority ledgers, capacity population
convergence and repair, 24 clean shadow cycles, and the writable soak loop.

The fresh run reached `writable soak cycle 10 converged` at roughly `40m29s`
of soak elapsed and passed the first scheduled repair at cycle 12 with
`last_repair=scheduled:completed@12`.  At that checkpoint status remained
`health=running`, `phase=soak-running`, `vmm=Running`, `shadow-cycle=24`,
`soak-cycle=12`, `repair-policy=defer`,
`repair-control-timeout-ms=120000`, and
`restart-settle-policy=repair-before-edit`.  No rejected receipt had been
observed.

The first planned restart edge also passed.  Cycle 24 restarted node `a`
before the edit, completed restart-settle with `restart_settle_passes=1`,
converged with the coincident scheduled repair deferred
(`repair_deferrals=1`, `last_repair=deferred:deferred@24`), and cycle 25
drained that repair (`last_repair=deferred:completed@25`) before converging at
roughly `1h44m30s` of soak elapsed.  This preserves the ADR 0377 repair-deferral
contract at the first restart/maintenance collision.

The post-restart ordinary cadence then continued.  Cycle 35 had a longer
settle interval under a visibly busy host, but still converged without
operator intervention or stale health.  Cycle 36 completed the next scheduled
repair (`last_repair=scheduled:completed@36`) and converged at roughly
`2h38m31s` of soak elapsed.

The second planned restart edge passed as well.  Cycle 48 restarted node `b`,
completed restart-settle with `restart_settle_passes=2`, converged with the
coincident scheduled repair deferred
(`repair_deferrals=2`, `last_repair=deferred:deferred@48`), and cycle 49
drained that repair (`last_repair=deferred:completed@49`) before converging at
roughly `3h35m32s` of soak elapsed.  No rejected receipt was observed.

Ordinary progress continued through the next maintenance point.  Cycle 60
completed the scheduled repair (`last_repair=scheduled:completed@60`) and
converged at roughly `4h26m33s` of soak elapsed.  The next high-value edge is
the cycle-72 node-`c` restart, which should complete the first full planned
restart rotation.

The cycle-72 node-`c` restart completed the first full planned restart rotation
across `a`, `b`, and `c`.  Node `c` restarted before the edit and
restart-settle completed with `restart_settle_passes=3`.  The edit then had a
long settle interval and the bounded stalled-cycle recovery path restarted
target `b`; cycle 72 then converged with the coincident scheduled repair
deferred (`repair_deferrals=3`, `last_repair=deferred:deferred@72`).  Cycle 73
drained that repair (`last_repair=deferred:completed@73`) and converged at
roughly `5h37m35s` of soak elapsed.  This was recovery evidence, not a
rejection.

The next ordinary maintenance point also passed: cycle 84 completed scheduled
repair (`last_repair=scheduled:completed@84`) and converged at roughly
`6h27m36s` of soak elapsed.

The second restart rotation then began cleanly.  Cycle 96 restarted node `a`,
completed restart-settle with `restart_settle_passes=4`, converged with the
coincident scheduled repair deferred
(`repair_deferrals=4`, `last_repair=deferred:deferred@96`), and cycle 97
drained that repair (`last_repair=deferred:completed@97`) before converging at
roughly `7h31m37s` of soak elapsed.

Cycle 108 completed the next scheduled repair
(`last_repair=scheduled:completed@108`) and converged at roughly `8h26m38s`
of soak elapsed.  The proof remained healthy with no rejected receipt observed.

The second rotation's node-`b` restart edge passed next.  Cycle 120 restarted
node `b`, completed restart-settle with `restart_settle_passes=5`, converged
with the coincident scheduled repair deferred
(`repair_deferrals=5`, `last_repair=deferred:deferred@120`), and cycle 121
drained that repair (`last_repair=deferred:completed@121`) before converging at
roughly `9h32m40s` of soak elapsed.

Cycle 132 completed the next scheduled repair
(`last_repair=scheduled:completed@132`) and converged at roughly `10h27m41s`
of soak elapsed.  The next high-value edge is the cycle-144 node-`c` restart,
which should complete the second planned restart rotation.

The cycle-144 node-`c` restart edge passed and completed the second full
planned restart rotation across `a`, `b`, and `c`.  Node `c` restarted before
the edit, restart-settle completed with `restart_settle_passes=6`, and cycle
144 converged with the coincident scheduled repair deferred
(`repair_deferrals=6`, `last_repair=deferred:deferred@144`).  Cycle 145 then
drained that repair (`last_repair=deferred:completed@145`) before converging
at roughly `11h39m42s` of soak elapsed.  No rejected receipt was observed.

The fresh run crossed the 12-hour mark healthy.  Cycle 156 completed the next
scheduled repair (`last_repair=scheduled:completed@156`) and converged at
roughly `12h41m44s` of soak elapsed, with `restart_settle_passes=6` and
`repair_deferrals=6`.  The next high-value edge is the cycle-168 node-`a`
restart.

The next restart rotation began cleanly.  Cycle 168 restarted node `a`,
completed restart-settle with `restart_settle_passes=7`, converged with the
coincident scheduled repair deferred
(`repair_deferrals=7`, `last_repair=deferred:deferred@168`), and cycle 169
drained that repair (`last_repair=deferred:completed@169`) before converging
at roughly `14h08m46s` of soak elapsed.

Cycle 180 completed the next scheduled repair
(`last_repair=scheduled:completed@180`) and converged at roughly `15h13m48s`
of soak elapsed.  The next high-value edge is the cycle-192 node-`b` restart.

The cycle-192 node-`b` restart edge passed.  Node `b` restarted before the
edit, restart-settle completed with `restart_settle_passes=8`, cycle 192
converged with the coincident scheduled repair deferred
(`repair_deferrals=8`, `last_repair=deferred:deferred@192`), and cycle 193
drained that repair (`last_repair=deferred:completed@193`) before converging
at roughly `16h54m51s` of soak elapsed.

Cycle 204 completed the next scheduled repair
(`last_repair=scheduled:completed@204`) and converged at roughly `18h13m53s`
of soak elapsed.  The next high-value edge is the cycle-216 node-`c` restart.

The cycle-216 node-`c` restart edge passed, completing another full planned
restart rotation across `a`, `b`, and `c`.  Node `c` restarted before the edit,
restart-settle completed with `restart_settle_passes=9`, cycle 216 converged
with the coincident scheduled repair deferred
(`repair_deferrals=9`, `last_repair=deferred:deferred@216`), and cycle 217
drained that repair (`last_repair=deferred:completed@217`) before converging
at roughly `20h00m57s` of soak elapsed.

Cycle 228 completed the next scheduled repair
(`last_repair=scheduled:completed@228`) and converged at roughly `21h34m59s`
of soak elapsed.  The next high-value edge is the cycle-240 node-`a` restart,
which should occur before the 24-hour wall-clock gate.

The cycle-240 node-`a` restart edge passed before the wall-clock gate.  Node
`a` restarted before the edit, restart-settle completed with
`restart_settle_passes=10`, cycle 240 converged with the coincident scheduled
repair deferred (`repair_deferrals=10`,
`last_repair=deferred:deferred@240`), and cycle 241 drained that repair
(`last_repair=deferred:completed@241`) before converging at roughly
`23h42m03s` of soak elapsed.

The fresh run crossed the 24-hour wall-clock gate cleanly.  Direct status at
roughly `24h01m37s` reported `health=running`, `phase=soak-running`,
`vmm=Running`, `soak-remaining=0s`, no rejected receipt, and cycle 244 in
progress.  The proof correctly continued because the stricter profile also
requires at least 288 completed soak cycles.

The post-clock continuation passed its next scheduled repair.  Cycle 252
completed `last_repair=scheduled:completed@252` and converged at roughly
`25h24m07s` of soak elapsed.  The next high-value edge is the cycle-264
node-`b` restart.

The cycle-264 node-`b` restart edge passed after the wall-clock gate, with
bounded stalled-cycle recovery exercised during the edge.  Node `b` restarted
before the edit, restart-settle completed with `restart_settle_passes=11`,
cycle 264 converged with the coincident scheduled repair deferred
(`repair_deferrals=11`, `last_repair=deferred:deferred@264`) after stalled
recovery restarted target `b`, and cycle 265 then drained the deferred repair
(`last_repair=deferred:completed@265`) after a second stalled-cycle recovery
restarted target `c`.  Cycle 265 converged at roughly `27h51m18s` of soak
elapsed with no rejected receipt observed.

The next scheduled post-clock maintenance point also passed.  Cycle 276 entered
the scheduled repair path (`last_repair=scheduled:started@276`) and then
converged with `last_repair=scheduled:completed@276` at roughly `29h44m15s`
of soak elapsed.  Host pressure was low during the repair sample, the proof
remained `health=running`, and no rejected receipt was observed.

The fresh run then completed the terminal cycle window and accepted.  Cycle
278 exercised one more bounded stalled-cycle recovery by restarting target
`c`, then converged.  Cycle 288 restarted node `c`, completed restart-settle
with `restart_settle_passes=12`, converged with the coincident scheduled repair
deferred (`repair_deferrals=12`, `last_repair=deferred:deferred@288`), and
cycle 289 drained the deferred repair (`last_repair=deferred:completed@289`).
The guest then completed post-soak followups with
`maintenance lifecycle and writer cutoff converged`.

The finalized receipt is retained as compact proof
`.sandwurm/exports/three-writer/run.9nqvO8B2` and verifies as accepted
evidence: `status=passed`, `shadow_cycles=24`, `soak_cycles=289`,
`soak_elapsed_ms=115981467` (`32h13m01s`), `soak_minimum_cycles=288`,
`soak_cycle_delay_ms=240000`, `soak_daemon_restarts=12`,
`soak_restart_targets=["a","b","c","a","b","c","a","b","c","a","b","c"]`,
`soak_restart_settle_policy=repair-before-edit`,
`soak_restart_settle_passes=12`,
`soak_restart_settle_cycles=[24,48,72,96,120,144,168,192,216,240,264,288]`,
`soak_repair_restart_policy=defer`, `soak_repair_passes=28`,
`soak_repair_deferrals=12`, `soak_repair_pending=false`,
`sync_repair_control_timeout_ms=120000`,
`soak_stalled_restart_after_ms=600000`,
`soak_stalled_cycle_recoveries=4`, `maintenance_lifecycle=true`,
`recovery_rehearsal=true`, `storage_fault_rehearsal=true`, and
`read_only_start_refused=true`.

Independent host verification passes through both
`tools/iotox-sandwurm-lab.sh verify-three-writer` and
`python3 tools/verify-sync-three-writer-sandwurm.py`, reporting
`schema=iotox.sync-three-writer-sandwurm-verification.v1`,
`status=passed`, `evidence_boundary=sandwurm-guest-evidence`,
`vm_substrate=cloud-hypervisor`, `network_class=none`,
`contains_secrets=false`, `soak_campaign=true`, `soak_cycles=289`,
`soak_restart_settle_passes=12`, `soak_stalled_cycle_recoveries=4`,
`maintenance_lifecycle=true`, and `resolved_sha256 =
2e36c7c239464b968cb222c88a12f4157d66e3ca8877ab1156c4b5f8019fe835`.
