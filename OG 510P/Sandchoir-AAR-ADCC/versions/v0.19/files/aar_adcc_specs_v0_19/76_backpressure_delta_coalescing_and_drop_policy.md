# 76 — Backpressure, Delta Coalescing, and Drop Policy (v0.19)

To survive weeks-long sessions, the router must not accumulate unbounded queues.
This doc makes queue behavior explicit.

## 1) Channel types
- `agent_in[Ai]`: bytes from PTY → parser
- `control_events`: parsed CTRLJSON + tags → state_store
- `delta_events`: state mutations → view assembler / telemetry
- `gearbox_cmds`: operator commands → state_store

## 2) Bounded queues everywhere
Every channel is bounded.
Default capacities are small (e.g., 32–256 messages) and tuned empirically.

## 3) Coalescing
Some events are compressible:
- multiple deltas can be merged into “delta batch per agent per cursor window”
- repeated telemetry updates can drop intermediate samples (keep latest)
- repeated “HOT list changed” events can collapse to last state

Coalescing should happen BEFORE queues overflow.

## 4) Drop policy (never drop these)
- CTRL parsed events (control plane)
- snapshot/checkpoint commands
- certified CE / selected patch state changes

Drop candidates first:
- telemetry samples (keep latest)
- redundant delta batches (keep last)
- low-priority logs

## 5) Backpressure signals
Expose queue depths in gearbox.
If a queue is near capacity:
- shrink view budgets
- disable exploration
- suggest Freeze/Recovery mode

## 6) Crash safety
Even if queues overflow, the state_store should remain consistent:
- apply events sequentially
- checkpoints are transactional snapshots
