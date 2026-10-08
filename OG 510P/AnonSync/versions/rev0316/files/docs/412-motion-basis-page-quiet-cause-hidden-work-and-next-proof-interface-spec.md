# Motion basis page — quiet cause, hidden work, and next-proof interface spec

## Purpose

The archive already has rate policy, pause semantics, background delivery, queue pages, and activity metrics.
What it still lacked was one ordinary page for the simpler question:

> why is this subject quiet right now, and is the honest answer no work, hidden work, missing source, suppressed participation, missing runtime, or a bottleneck elsewhere?

Current official Resilio docs make this seam concrete.
They still say scheduled `Paused` leaves some signals alive, mobile/runtime policy can take the core offline, hidden internal tasks can continue before visible transfer, and some missing downloads are really source-absence rather than delay.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Motion basis** page for every subject with recent change activity, pending transfer expectation, or operator-visible quiet / slow concern.

The page exists to answer five things in one place:

1. whether quiet currently means `nothing to do` or `work still underway`
2. whether the active blocker is source absence, route absence, runtime absence, or policy suppression
3. which hidden work phase is consuming time before visible transfer
4. what concrete evidence would change next if the system is healthy
5. what least-widening next action would actually alter the answer

## Fixed page order

1. **Current motion verdict**
2. **Quiet cause decomposition**
3. **Hidden work lane**
4. **Expected next proof**
5. **Least-widening next actions**

### 1) Current motion verdict

Show:

- `motion_basis_page_id`
- subject scope
- current `motion_verdict` (`idle-no-work`, `hidden-work`, `transfer-active`, `policy-suppressed`, `runtime-absent`, `source-absent`, `route-absent`, `bottlenecked`, `mixed`, `unknown`)
- strongest honest summary
- last materially motion-shaping event time

The operator must be able to answer:

> why does this subject look quiet right now?

### 2) Quiet cause decomposition

Show rows for the major cause families:

- no detected changes pending
- detecting / indexing / hashing still in progress
- route exists but source currently unavailable in full
- seat/runtime offline, asleep, killed, or forbidden by network/power posture
- transfer policy suppressing some lanes but not others
- practical bottleneck (relay, disk, workload shape, remote-upload ceiling, host interference)

Each row must show `active`, `not active`, or `plausible but unproven`.

The page must make it ordinary to answer:

> what exact family owns the current quiet period?

### 3) Hidden work lane

Show:

- current hidden phase rows such as `detecting`, `indexing`, `hashing`, `block-check`, `local-block-copy`, `merge-tree`, `queue-build`, `none`, `unknown`
- whether the phase is expected, long-running-but-recoverable, or overdue
- whether visible transfer may still remain at zero during this phase
- the strongest adjacent resource pressure signal

This section must not flatten all non-visible work into one vague `internal tasks` badge.

### 4) Expected next proof

Show the next observable state that should change if the current verdict is healthy:

- change publication should advance to `indexed`
- fetchability should gain a live full source
- queue should materialize an execution row
- route should move from `candidate` to `active`
- wake/resume should re-enter detection
- or `no next proof until a new change arrives`

The page must answer:

> what exact evidence should change next if we simply wait?

### 5) Least-widening next actions

Actions may include:

- `Wait for hidden work`
- `Open bottleneck cause page`
- `Open quiet window page`
- `Open resume catch-up page`
- `Verify source availability`
- `Repair route`
- `Wake or restart runtime`
- `Run reviewed rescan`

Each action must preview the resulting motion-verdict delta and its non-effects.

## Public object

### Motion basis page

Fields:

- `motion_basis_page_id`
- `subject_ref`
- `motion_verdict`
- `quiet_cause_rows[]`
- `hidden_phase_rows[]`
- `source_availability_state` (`full-source-present`, `announced-no-live-source`, `source-offline`, `unknown`)
- `runtime_presence_state` (`continuous`, `sleeping`, `stopped`, `killed`, `forbidden-network`, `unknown`)
- `policy_suppression_state` (`none`, `partial`, `full`, `unknown`)
- `bottleneck_state` (`none-proven`, `relay`, `disk`, `small-files`, `remote-upload`, `security-software`, `mixed`, `unknown`)
- `expected_next_proof`
- `next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. subject
2. motion verdict
3. dominant quiet cause
4. next proof
5. next least-widening action

Example:

```text
Project Alpha     hidden-work     hashing + queue-build     queue row should appear     Wait for hidden work
```

## Non-goals

This page does **not** prove that the subject is fresh, that transfer is globally fast, or that the current route is already optimal.
It proves only the current **motion basis** and what evidence would honestly change next.
