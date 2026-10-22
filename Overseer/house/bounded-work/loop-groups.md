# Loop Groups

## Purpose

Define the first grouping substrate above bounded finite loops.

The house now has one room for individual self-stopping delegated loops and a second room for coherent collections of those loops.
This lets the Overseer name and reconstruct stable or unstable clusters of delegated work without pretending a full orchestration runtime already exists.

## Current Packet

- `generated_at = 2026-04-18T00:17:56Z`
- `active_group_count = 1`
- `planned_group_count = 1`
- `paused_group_count = 0`
- `terminal_group_count = 0`
- `latest_group_id = group-20260313T024702Z-dd403f`
- `latest_group_state = active`
- `latest_group_stability_class = unstable`
- `latest_group_coordination_mode = serial`
- `latest_group_member_count = 193`
- `latest_group_purpose = bounded deadman rescue probes`
- next planned group kept visible: `group-20260313T020747Z-ead149` carries `experimental` / `advisory` posture for `Pressure-test conductor runtime planning gate and support surfaces`

## First decision

The first grouping substrate is:

- a loop-group ledger under `/home/overseer/state/loop-groups/`
- a small registry CLI at `/home/overseer/scripts/loop_group_registry.py`
- explicit stability classes
- explicit coordination modes
- explicit membership in terms of finite-loop ids

That means the house is deciding this now:

- groups are first-class records, not folklore
- groups may be stable, unstable, or experimental
- groups may be serial, parallel, rolling, or merely advisory
- group records must survive restarts and leave readable receipts

## Why this room exists

The finite-loop ledger answers:

- what one bounded delegate is doing
- how many turns it has left
- what its latest checkpoint says

That is not enough once the house wants to reason about:

- several loops attacking one problem together
- a stable cluster of recurring delegates
- an unstable or experimental cohort being tried temporarily
- reconstruction after interruption or reboot

The house needed a room for those collections before it needed a complex orchestrator.

## Runtime artifacts

- state root: `/home/overseer/state/loop-groups/`
- group records: `/home/overseer/state/loop-groups/groups/<group_id>.json`
- receipts: `/home/overseer/state/loop-groups/receipts/`
- checkpoints: `/home/overseer/state/loop-groups/checkpoints/`
- recovery packets: `/home/overseer/state/loop-groups/recovery/`
- global events: `/home/overseer/state/loop-groups/events.jsonl`
- latest pointer: `/home/overseer/state/loop-groups/latest.json`
- group index: `/home/overseer/state/loop-groups/index.json`
  - explicit buckets: `planned`, `active`, `paused`, `terminal`
- lineage-aware reconstruction fields now also appear inside group status and recovery packets:
  - `lineage_count`
  - `lineage_state_counts`
  - `member_lineages`
  - `lineage_reopen_order`
  - the current lineage tip's continuity/demotion memory when it already exists
    below the group layer

## Current CLI

The registry CLI currently supports:

- `create`
- `attach-loop`
- `detach-loop`
- `checkpoint`
- `reconcile`
- `reconstruct`
- `retire`
- `status`

That is enough to:

- allocate a group id
- declare the group intent and stability class
- attach finite-loop members
- record group-level progress and resume hints
- derive a truthful paused/active posture back from current member loops
- keep paused groups out of the `active` bucket so the index itself stays truthful
- write a recovery packet that points back toward the right member loops and group artifacts
- widen reconstruction from an attached loop to the live tip of its bounded follow-up chain without rewriting explicit membership
- retire the group with a readable outcome

It is not yet a loop executor or scheduler.

## Minimum group record

Every loop group should be able to answer:

- what problem or theme the group exists for
- whether it is stable, unstable, or experimental
- how its members are intended to coordinate
- which finite loops belong to it
- what its latest resume hint is
- whether it is still active or why it stopped
- what member loops should be reopened first when the house needs to reform the group
- what lineage tips sit behind those explicit member loops when follow-up chains already exist
- and, when a lineage tip already has turn-artifact continuity memory, whether
  that tip last ran fresh because a requested resume was demoted by
  `cold-required`

## Coordination rule

- loop groups do not outrank the primary interactive session
- loop groups sit above finite loops and below any future full Overseer runtime
- group state should help the house reconstruct coordinated work after interruption
- group state should not silently replace loop-level receipts
- group state may now reconcile itself back from member-loop truth instead of staying forever active by inertia
- group state should now also be able to emit a compact recovery packet instead of making reopen depend on manual inspection of several files
- group reconstruction may now widen from explicit attached loops to lineage tips, but the stored member list remains explicit and human-readable

## Relationship to finite loops

The finite-loop ledger tracks bounded delegate truth.
The loop-group ledger tracks grouped-delegate truth.

Those are related, but not identical:

- a loop can exist without a group
- a group can exist before all of its member loops exist
- a group may summarize a cluster of loops as stable or unstable even when individual loops are still changing
- a group may attach an older loop explicitly and still reconstruct through the current lineage tip if bounded follow-up successors already exist

## Current limitation

The group room exists now, but it does not launch or schedule loops.
That is deliberate.

The house needed a truthful place to name and reconstruct groups before it needed a more forceful orchestration layer.
It can now reconstruct through lineage tips, but it still does not get to rewrite membership or spawn work on its own.
