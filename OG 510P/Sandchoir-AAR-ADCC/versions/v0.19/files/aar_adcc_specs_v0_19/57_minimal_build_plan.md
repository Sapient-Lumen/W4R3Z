# 57 — Minimal Build Plan (Rust-first) (v0.19)

This is the shortest path to a *working* ADCC+AAR router with MetaLLM steering.
It explicitly optimizes for “unknown slice counts” and “free-user CLI constraints.”

## Phase 0: Skeleton + persistence (1–2 days)
Deliverable: a binary that can start, keep state, and shut down cleanly.
- On-disk state directory with:
  - event log (append-only)
  - WS snapshot (JSON or msgpack)
  - config (weights, caps, budget profile)
- CURSOR increments for each mutation.
- `snapshot create/restore`, `thread list/open/fork`.
- Gearbox: minimal CLI (TUI later).

Acceptance:
- can run overnight and recover next day from checkpoint.

## Phase 1: BCC parsing + bounded views (core loop)
Deliverable: the router can accept agent outputs (even partial) and assemble bounded views.
- Agent I/O abstraction (mock first).
- Streaming parser that extracts @CTRL / CTRLJSON early.
- JSON healing (Tier 1a) before re-ask.
- View assembly contract (47_) enforced by hard caps (line-based).
- DELTA feed by CURSOR.

Acceptance:
- 80% of “test agent outputs” yield parseable CTRL (after healing/repair).
- views never exceed caps.

## Phase 2: Multi-agent PTY integration (real CLI)
Deliverable: attach to 3 agent terminals and feed them composed views.
- PTY spawn/attach (portable-pty or platform-specific).
- Bounded queues per agent; avoid stalls when one agent hangs.
- Time-to-CTRL telemetry.

Acceptance:
- system stays responsive with one agent stalled.
- time_to_ctrl is measurable per agent.

## Phase 3: Integrator + patch lane (minimum viable engineering)
Deliverable: patch proposals become a real workflow.
- Selected patch state + integrator selection (floor vote).
- Soft leases; integrator arbitration (37_).
- Patch-shaped exports (git diff or unified diff) stored in ledger with WS pointers.

Acceptance:
- “DIVERGE → SELECT → INTEGRATE” works on a toy repo.

## Phase 4: Evidence lane (verifiers)
Deliverable: evidence moves votes in a bounded way.
- Verifier registry + economics (36_).
- Suggestion policy (43_).
- E# evidence cards; logs to ledger; caching by snapshot key.

Acceptance:
- selected patches trigger cheap checks.
- certified CE path exists.

## Phase 5: Gearbox TUI + MetaLLM loop
Deliverable: operator can steer mid-run without chaos.
- Ratatui UI for:
  - mode, H0, selected patch, integrator, certified CE
  - telemetry per agent
  - quick actions (compact/snapshot/cap probe)
- MetaLLM as a *client* of router CLI:
  - reads telemetry
  - proposes mode/budget/weight changes
  - files REQs / selects checks

Acceptance:
- “weeks-long i3 session” is practical.

## Cut line (what not to build early)
- protocol elections
- cross-agent personalization in view assembly
- self-modifying kernel
- CRDT text merge

Add early: Router CLI contract (79_) and Telemetry schema (82_) so MetaLLM can operate from day 1.
