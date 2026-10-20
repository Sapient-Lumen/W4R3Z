# ADR 0177: Qualify cancellation before route loss

Status: accepted over direct UDP and forced TCP, 2026-08-26.

## Context

ADR 0175 qualified one deterministic `loss → reassignment → progress → cancellation →
recovery` order. That result did not show what happens when local withdrawal reaches terminal durable
truth before the affected auxiliary route disappears. In particular, a late carrier loss must not
resurrect a cancelled pull, assign its immutable objects to another worker, retain staging, or spend
more than the signed restart budget.

Stopping a route at a byte threshold cannot answer the opposite-order question: by construction it
introduces loss while the receive is live. Host TAP failure is also too broad because it removes the
protected primary and both auxiliary identities together. The experiment needs one exact retained
pull carrier to fail only after `sync-cancel` has fenced the job and completed local cleanup.

## Decision

Add one default-off qualification-only Agent option:

```text
--qualify-route-stop-after-cancel
```

It requires synchronization and signed route workers and is mutually exclusive with
`--qualify-route-stop-after-bytes`. The Agent watches for the first settled cancelled pull whose
retained carrier is auxiliary. It then stops only that exact route key and worker incarnation. The
pull tombstone remains cancelled; it is not rewritten to failed or awaiting objects.

The coordinator must account for one carrier loss with zero auxiliary reassignment. Once the loss is
visible and the cancelled pull remains terminal, the existing qualification recovery path may spend
one signed restart-budget unit, reconstruct the same savedata identity under a fresh process-local
worker ID, authenticate its reciprocal binding, and return it to ready. The local status record adds
`qualification-fault-after-cancel=1`; the ordinary progress-first seam retains zero for that field.
Normal production configuration remains unchanged.

The Sandwurm `sync-tree-route-cancel-loss` cell uses one protected primary and two signed bulk
workers. It first binds positive immutable-object progress and admitted work to one exact carrier,
withdraws the pull through the ordinary local control command, and requires the job to be cancelled,
all incoming transfers and staging absent, and signed work drained to zero within five seconds. Only
then may the qualification seam stop the retained carrier. The cell requires one loss, zero
reassignment, at least one fenced late terminal, one recovery, the same exact route key ready with
one restart, both bulk routes ready, and 40 protected Ratox samples below 250 ms.

Direct UDP `pair.yv4txv1r` and forced TCP `pair.m2396itk` pass raw and compact verification against
the same exact binary. Cancellation tails are 80 ms and 70 ms respectively. Both cells release
signed work from two to zero, report one carrier loss, zero reassignment, two fenced terminals, and
one recovery.

## Consequences

- Deterministic loss-before-cancellation and cancellation-before-loss orders are both qualified.
- A late route failure cannot make a settled cancelled pull eligible for reassignment.
- Recovery is route-capacity recovery, not pull recovery: the cancelled job remains terminal and no
  HEAD is accepted or activated.
- The route public key is stable across recovery while the process-local worker incarnation changes.
- The seam is not an operator route-control API or automatic production restart policy.
- Simultaneous loss/cancel races, randomized delay distributions, multiple concurrent affected
  pulls, common-link QoS, throughput, and relay diversity remain open.
- No framing, route inventory, scheduler identity, or authority capability changes.

## Verification

The CLI registry rejects detached use and conflicting progress-first/cancellation-first fault modes.
Existing direct supervisor coverage binds exact stop/restart to one auxiliary incarnation. The
subscriber snapshot carries the existing process-private settled-cleanup bit; direct regression
coverage holds it false across an injected cleanup failure and true only after exact retry. The
genuine guest, runner, verifier, and compact exporter recognize `sync-tree-route-cancel-loss` and
require strict zero defaults from every other scenario.

The raw direct-UDP and forced-TCP cells independently pass strict verification. Each 241,664-byte
compact proof then replays with every file digest, receipt hash, binary hash, carrier class,
cancellation invariant, loss/recovery counter, route inventory, and protected Ratox artifact bound.
Exact results live in `evidence/2026-08-26-sandwurm-sync-route-cancel-loss.md`.
