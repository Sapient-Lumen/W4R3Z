# 51 — Rust/Tokio Async Architecture (v0.19)

You asked whether ADCC/AAR must be “highly performant” or if Python is fine.
CPU is not your bottleneck; coordination and I/O are.
Rust + Tokio help because you need:
- clean async I/O across multiple PTYs/processes
- bounded queues + backpressure (prevent memory blowups)
- robust shutdown and recovery

## 1) Runtime shape (tasks)
Recommended task graph:

- `state_store`: owns WS/Ledger/event_log, applies mutations, emits deltas
- `view_assembler`: builds per-agent views with hard caps
- `agent_io[Ai]`: spawns/attaches to each CLI process; reads stdout/stderr; writes stdin
- `parser[Ai]`: extracts CTRL/CTRLJSON early (streaming bridge), emits control events
- `telemetry`: aggregates metrics (time_to_ctrl, truncation signals, parse rate)
- `gearbox_ui` (optional): TUI that issues router CLI commands
- `verifier_runner` (optional): runs registered checks under cost budgets
- `checkpoint_manager`: snapshots state at defined moments

Everything communicates via bounded channels.

## 2) Channels and backpressure
- Use bounded `tokio::sync::mpsc::channel(N)` for nearly all internal queues.
- Prefer “drop or compress” behavior for noisy channels:
  - e.g., coalesce multiple DELTA events into one “delta batch” per agent.
- Use `oneshot` for request/response (e.g., “render view for A3 now”).

## 3) Streaming and early header capture
- The parser should look for `@CTRL` / `CTRLJSON=` as early as possible.
- Once CTRL is seen, the router can:
  - stop reading further for that slice (optional)
  - or keep reading but prioritize committing control events first

## 4) Graceful shutdown
- Use a single cancellation trigger (Ctrl+C / SIGTERM) that:
  - stops spawning new work
  - drains verifier jobs if feasible
  - checkpoints if safe
  - terminates child processes

## 5) Why this matters for unknown slices
Async I/O + bounded queues let you treat each agent like an unreliable stream:
- salvage partial control headers
- avoid stalls when one agent hangs
- keep the rest moving

## 6) “Performance” definition (your real bottleneck)
The system’s “performance” is:
- percent of slices that yield parseable control headers
- time_to_ctrl
- percent of time spent on evidence (E#/checks) vs chatter
- boundedness (no WS bloat)

Not raw CPU throughput.

See also: 59_pty_and_agent_io_notes.md (portable PTY integration) and 61_golden_tests_and_simulated_agents.md (testing async I/O).

Mode switching should be driven by telemetry; see 69_mode_transition_matrix.md and 56_slice_telemetry_and_budget_adaptation.md.

Backpressure and coalescing policy are specified in 76_backpressure_delta_coalescing_and_drop_policy.md.
