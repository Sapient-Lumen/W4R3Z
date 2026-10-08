# Startup owner handoff, duplicate-launch risk, and drift-history interface spec

## Purpose

The archive already has bring-up review, installation attestation, service-promotion continuity, runtime-status bridges, and outside follow-through truth.
What it still lacked was one explicit contract for a different question that operators repeatedly need after install and after promotion:

> who actually owns background startup on this host right now, is that ownership singular, and has it drifted recently?

That question matters because `installed`, `service promoted`, `started once`, and `will come back correctly after reboot/login` are not the same truth.
A sync daemon can look healthy today while tomorrow's startup posture is actually:

- singular and stable
- duplicated across more than one startup owner
- missing entirely
- ambiguous because one startup lane is conditional, generated, or stale

AnonSync should therefore treat startup ownership as first-class operator state instead of a side effect hidden in service managers, desktop startup lists, or remembered installer choices.

## Core decision

AnonSync must expose one reviewed **startup-owner** object that keeps these truths separate:

- requested startup posture
- candidate startup-owner lanes that currently exist on the host
- which lane is presently effective
- whether ownership is singular, duplicated, missing, or ambiguous
- whether the currently running daemon actually matches the declared startup owner
- whether startup ownership has drifted recently

The operator must be able to answer:

- who is supposed to start this node on next boot/login
- who could actually start it now
- whether more than one lane may launch the same node
- whether current runtime came from the reviewed owner or from an accidental/manual path
- whether the host recently drifted away from the intended ownership model

## Why this matters

The comparison datacubes made this seam hard to ignore.
VHK's installed startup-handoff work sharpened a law that AnonSync still needed too:

> a node's startup owner is not equivalent to `installed`, `service enabled`, or `launch at login checked`.

That law fits AnonSync especially well because duplicate or missing startup ownership can silently falsify later readiness claims:

- a daemon may be healthy now only because it was launched manually
- a background service may be continuity-correct but still not be the active startup owner
- both a user-service lane and a desktop-autostart lane may claim the same node at once
- a generated or conditional owner may exist but not mean the same thing as ordinary explicit enablement
- a stale startup owner may survive after service migration, uninstall, or runtime-seat change

AnonSync should therefore hold one stronger rule:

> startup ownership is a reviewed continuity-bearing runtime fact, not a convenience checkbox.

## Fixed review order

Every startup-owner surface should render the same sections in the same order:

1. **Requested startup posture**
2. **Candidate owner lanes**
3. **Effective ownership and duplicate/missing risk**
4. **Current runtime correlation**
5. **Recent drift history**
6. **Startup-owner receipt**

### 1) Requested startup posture

Show:

- whether the reviewed intent is `manual-only`, `user-service`, `system-service`, `desktop-autostart`, `reviewed-mixed`, or `blocked`
- which seat / principal the operator expects to own startup
- whether the reviewed posture came from install, bring-up, service promotion, or later mutation
- whether any compensating caveat already exists

The operator must be able to answer: **what startup model did we actually choose?**

### 2) Candidate owner lanes

Show one row per candidate startup lane, for example:

- user service manager lane
- system service manager lane
- desktop autostart / login-item lane
- scheduled-task / launch-agent lane where applicable
- manual-only / no owner lane

Each row should state:

- owner kind
- owner principal or scope
- host-local source of truth
- activation posture (`enabled`, `disabled`, `generated`, `transient`, `conditional`, `missing`, `unknown`)
- any gating condition that may suppress actual launch

The operator must be able to answer: **which lanes still claim startup, and under what kind of claim?**

### 3) Effective ownership and duplicate/missing risk

Show one explicit current verdict:

- `singular-primary-owner`
- `singular-fallback-owner`
- `duplicate-owner-risk`
- `missing-owner`
- `ambiguous-owner`
- `manual-only-by-choice`
- `blocked`

Also show:

- which row is considered effective now
- why another row is only fallback / duplicate / stale / blocked
- whether duplicate launch could target the same state root
- whether missing ownership means the node will not return after reboot/login without manual action

The operator must be able to answer: **who actually owns startup now, and is that ownership safe?**

### 4) Current runtime correlation

Show:

- whether the currently running daemon matches the effective startup owner
- whether it was started manually outside the reviewed owner lane
- whether runtime is absent even though ownership exists
- whether runtime exists under a duplicate or stale owner
- whether the current control surface is reading the same node that startup ownership refers to

The operator must be able to answer: **does today's running daemon actually come from the reviewed startup owner, or are we living on borrowed truth?**

### 5) Recent drift history

Show a short local timeline of startup-owner snapshots.
Each snapshot should preserve:

- effective owner class at that time
- current effective lane
- duplicate / missing / ambiguous flags
- any observed principal or state-root mismatch
- whether the drift was introduced, recovered, or remains chronic

The operator must be able to answer: **is startup ownership stable, newly broken, recently repaired, or flapping?**

### 6) Startup-owner receipt

Record:

- requested startup posture
- candidate owner rows considered
- effective owner verdict
- runtime correlation verdict
- drift class since prior snapshot if known
- next honest action

The operator must be able to answer: **what later proves who owned startup and whether that truth changed?**

## Public objects

### `startup_owner_snapshot`

Fields:

- `startup_owner_snapshot_id`
- `node_ref`
- `requested_startup_posture`
- `candidate_owner_rows[]`
- `effective_owner_verdict`
- `effective_owner_row_ref` nullable
- `duplicate_risk_class` (`none`, `same-node-double-start-risk`, `different-node-risk`, `unknown`)
- `runtime_correlation_verdict` (`matches-owner`, `manual-outside-owner`, `runtime-missing`, `runtime-under-duplicate`, `unknown`)
- `drift_state` (`stable`, `changed-recently`, `recovered`, `chronic-duplicate`, `chronic-missing`, `flapping`, `unknown`)
- `next_honest_action`
- `generated_at`

### `startup_owner_receipt`

Fields:

- `startup_owner_receipt_id`
- `snapshot_ref`
- `previous_snapshot_ref` nullable
- `drift_class` (`none`, `owner-changed`, `duplicate-introduced`, `duplicate-cleared`, `owner-lost`, `owner-restored`, `runtime-mismatch-cleared`, `flapping-observed`, `unknown`)
- `operator_action_ref` nullable
- `created_at`

## Main surface

A compact row should read like one of these, not just `launch at login enabled`:

- `startup owner: user service · singular · runtime matches owner`
- `startup owner: duplicate risk · user service + desktop autostart`
- `startup owner: missing · current runtime is manual only`
- `startup owner: ambiguous · generated desktop lane plus stale user-service intent`
- `startup owner: recovered to primary owner · duplicate cleared yesterday`

## Event language

Use phrases such as:

- `startup ownership is singular and stable`
- `duplicate startup owners may launch the same node`
- `current runtime does not come from the reviewed startup owner`
- `startup ownership missing; node will not return automatically`
- `startup ownership recovered to primary lane`

Avoid phrases such as:

- `launch at login enabled`
- `service enabled`
- `auto-start on`
- `background mode active`

Those lines are too lossy to prove who will actually launch the current node.

## CLI shape

```text
anonsync startup-owner show
anonsync startup-owner review
anonsync startup-owner receipt show <receipt>
anonsync startup-owner history
```

The CLI must preserve the difference between `candidate owners`, `effective owner`, `runtime correlation`, and `drift history`.

## Edge cases

### Service promotion succeeded, but startup ownership is still unresolved

That is legitimate.
A same-node service promotion receipt may exist while startup-owner review still says `ambiguous-owner` or `missing-owner`.
The product must keep those truths separate.

### Current runtime is healthy, but only because an operator launched it manually

That is not a stable startup answer.
The status bridge may show healthy runtime while startup-owner review still says `manual-outside-owner`.

### Multiple owners exist on purpose during migration

That may be temporarily acceptable only if explicitly reviewed.
The verdict should remain `duplicate-owner-risk` until one owner is retired or the mixed posture is explicitly time-bounded and receipted.

### Generated or conditional owners

Generated or conditional lanes are real facts, but they must not be flattened into ordinary explicit enablement.
The product should preserve their class and any gating condition that explains why startup may still not occur.

## Non-clone reason

Current Linux startup reality already spreads meaning across unit-file states, desktop-autostart rules, generator behavior, and manual launch history.
AnonSync should not reproduce that fragmentation with one vague `launch at login` checkbox or one vague `service enabled` badge.
It should instead give the operator one reviewed startup-owner surface and one durable drift/history receipt proving who actually owns background return on this host.
