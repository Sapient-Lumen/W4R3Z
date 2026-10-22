# Finite Loops

## Purpose

Define the first bounded delegation substrate for self-stopping Overseer loops.

This is intentionally smaller than the future full Overseer runtime.
It gives the house a truthful place to put delegated work that:

- has an explicit turn budget,
- is expected to stop on its own,
- should not pollute the primary interactive session,
- and must leave readable receipts behind.

## Current Packet

- `updated_at = 2026-03-22T16:51:08Z`
- `loop_id = loop-20260322T165107Z-bc10d0`
- `loop_class = generic`
- `state = running`
- `phase = turn-1-starting`
- `session_policy = separate-session`
- `lineage_root = loop-20260322T165107Z-bc10d0`
- `lineage_depth = 0`
- `followup_of = none`
- `hold_status = none`
- `hold_scope = loop`
- `turn_budget_remaining = 2`
- `turn_count = 0`

## First decision

The first bounded delegation substrate is:

- a finite-loop ledger under `/home/overseer/state/finite-loops/`
- a small registry CLI at `/home/overseer/scripts/finite_loop_registry.py`
- a first bounded executor at `/home/overseer/scripts/finite_loop_executor.py`
- a one-command spawn surface at `/home/overseer/scripts/spawn_finite_loop.py`
- explicit separate-session policy by default
- shared Codex load-balancer use through that executor

That means the house is deciding this now:

- finite loops do not share the primary interactive Codex session id by default
- finite loops are daemon-class work and therefore subordinate to interactive work
- finite loops are expected to self-terminate on completion, budget exhaustion, or explicit block/cancel conditions
- same-family Codex finite loops are currently bounded first by class, mission, turn budget, and receipts rather than by a host-level sandbox

## Why separate-session first

The current local and upstream Codex continuity surfaces are not trustworthy enough to make shared-session delegation the first default.

For bounded delegates, a fresh local session with clear receipts is the truthful posture.
If future evidence proves some shared-session continuation is safe and valuable, it can be added as a narrower explicit policy later.

The current construction bias is also `manager -> worker`, not peer handoff between coequal loopers.

## Runtime isolation posture

Finite loops are now expected to carry their own local runtime surfaces.

The current truthful posture is:

- separate local `CODEX_HOME` per loop
- separate per-loop auth file
- separate per-loop session/history roots
- separate git worktree for repo-backed mutation when possible
- fallback task directory when the workspace is not inside git
- profile-scoped runtime lock when the daemon runner is given a loop runtime root

This is the first house answer to the earlier concurrency problem.
The house no longer has to choose between:

- one interactive sovereign thread, or
- any bounded daemon work at all

It can now allow bounded daemon work on a different profile without letting that
daemon share the interactive session id, `auth.json`, or worktree by accident.

The next truthful requirement after that proof is room legibility:

- a running loop should be visible as running even before it writes a final receipt
- the audit room should prefer the current active or held audit worker over the last completed findings packet
- concurrent work should be reopened from loop/runtime/active-run surfaces together, not from a stale terminal note

## Runtime artifacts

- state root: `/home/overseer/state/finite-loops/`
- run directories: `/home/overseer/state/finite-loops/runs/<loop_id>/`
- receipts: `/home/overseer/state/finite-loops/receipts/`
- checkpoints: `/home/overseer/state/finite-loops/checkpoints/`
- recovery notes: `/home/overseer/state/finite-loops/recovery/`
- follow-up receipts: `/home/overseer/state/finite-loops/followups/`
- lineage packets: `/home/overseer/state/finite-loops/lineages/`
- global events: `/home/overseer/state/finite-loops/events.jsonl`
- latest pointer: `/home/overseer/state/finite-loops/latest.json`
- active/terminal index: `/home/overseer/state/finite-loops/index.json`

## Current CLI

The registry CLI currently supports:

- `create`
- `checkpoint`
- `hold`
- `release-hold`
- `complete`
- `reconstruct`
- `status`
- explicit follow-up spawn via `/home/overseer/scripts/spawn_followup_loop.py`
- explicit lineage packet via `/home/overseer/scripts/finite_loop_registry.py lineage`

That is enough to:

- allocate a loop id,
- record the initial bounded request,
- advance semantic progress,
- mark a terminal outcome,
- write a recovery packet for cheap truthful reopen,
- and reopen the latest active or terminal loop state cheaply.

It is not yet the full loop executor.

The first bounded executor now exists separately at:

- `/home/overseer/scripts/finite_loop_executor.py`
- `/home/overseer/docs/finite-loop-executor.md`
- `/home/overseer/scripts/spawn_finite_loop.py`

The current ergonomic rule is:

- use `finite_loop_registry.py` when the house wants to inspect or edit loop records directly
- use `spawn_finite_loop.py` when the house wants to create and execute a bounded delegate as one coherent action
- use `spawn_followup_loop.py` when the house wants a bounded successor linked back to an existing loop or recovery packet
- use `finite_loop_registry.py lineage` when the house wants the whole successor chain reopened as one bounded object

The registry now also carries the first live hold model:

- loops can record an explicit hold record beside their coarse state
- `planned` plus `phase = waiting_for_capacity` no longer has to speak only by implication
- recovery packets and the audit room can now say `held for capacity` directly
- groups can now reopen held lineages without pretending they were actively runnable

## Minimum loop record

Every finite loop should be able to answer:

- what it is trying to do
- how many turns it was allowed
- how many turns remain
- whether it is still running or why it stopped
- what session policy it used
- what Codex/load-balancer consumer it should eventually map to
- what the latest resume hint is
- what files should be reopened first when the house needs to reconstruct it

## Coordination rule

- interactive human work outranks finite loops
- finite loops should eventually consume Codex only through the shared load balancer
- finite loops should identify themselves as distinct daemon consumers
- finite loops should leave receipts even when they never reach successful execution
- finite loops do not become mini-sovereigns merely because they may have broad host capability

## Power stance

Current planning posture:

- same-family Codex finite loops keep broad house capability by default
- the real first boundary is authority, not technical clipping
- authority is carried by loop class, mission, turn budget, and result receipts

See `/home/overseer/POWERS.md` and `/home/overseer/docs/delegation-power-model.md`.

## Relationship to daemon checkpoints

The current daemon wrapper checkpoints in `state/codex-load-balancer/checkpoints/` remain important.
The finite-loop ledger sits above them:

- the load balancer tracks daemon-runtime truth
- the finite-loop ledger tracks bounded delegated-work truth
- the loop-group ledger tracks grouped delegated-work truth

Those are related, but not identical.

See also:

- `/home/overseer/HOLDS.md`
- `/home/overseer/docs/loop-pauses-and-holds.md`

## Current limitation

The ledger and the first executor now both exist.
What does not exist yet is a richer long-lived orchestration runtime.

That is still deliberate.

The house needed the room, the contract, and the receipts before it needed a more forceful scheduler.
The house now also expects each loop to be able to write a reconstruction packet on demand instead of making reopen depend on manual path spelunking.
The house now also expects bounded continuation to be explicit: successor loops should carry lineage and follow-up receipts rather than hiding continuation inside folklore.
The house now also expects explicit chain truth: a follow-up family should be reconstructable as a lineage instead of only as separate loops.
The house now also expects explicit source continuity memory in those follow-up
receipts when it already exists below them: if the source loop last ran fresh
because a requested resume was demoted by `cold-required`, the follow-up room
should preserve that source-side split instead of flattening it back to source
state and phase alone.
The group room may now consume that lineage truth during reconstruction, but it still does not get to rewrite the explicit member list behind the house's back.
The house now also expects the first runtime hold surface to stay small: explicit loop-level hold records are real, but this is not permission for a hidden scheduler.
