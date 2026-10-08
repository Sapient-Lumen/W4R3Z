# 50 — Kernel Invariants + Versioning (v0.19)

This document is the “things we refuse to break,” even as plugins and heuristics evolve.
If you later regret something, regret the *invariants* last.

## 1) Kernel vs plugins
**Kernel** = minimal router that:
- maintains WS/Ledger and CURSOR
- assembles bounded per-agent views
- parses control headers (BCC / CTRLJSON)
- applies deterministic promotion/compaction rules
- exposes a small CLI and a stable on-disk state format

**Plugins** = optional modules that:
- compute budgets, hotness heuristics, exploration
- propose verifier runs
- integrate structured decoding backends
- provide TUI/gearbox UX
- add new object types (carefully)

## 2) Invariants (must-haves)
### Control-plane invariants
- **H0 always appears first** in every view.
- View section ordering is stable (see 47_view_assembly_and_token_budgeting_contract.md).
- Every WS mutation increments CURSOR and is logged (event log semantics).
- Any agent output is treated as an **anytime packet**: salvage what you can.
- All directed messages are typed objects (REQ#, not freeform DMs).

### Coordination invariants
- Votes guide attention/resource allocation; they do not prove truth.
- “Integrator arbitration” exists: one integrator merges/applies canonical state (see 37_...).
- Soft/hard leases exist; canonical changes require a selection path (vote/human/integrator).

### Boundedness invariants
- WS has hard caps, and compaction produces SUM# (see 28_...).
- Views have hard caps; overflow truncates lowest priority content.
- No unbounded logs in WS (logs go to Ledger).

### Safety/ergonomics invariants (your intent)
- Human can always override top priority.
- Human can set agent weights; higher-quality models can outweigh smaller ones (see 41_...).
- The system must degrade gracefully when agents fail to emit structured control headers.

## 3) Versioning policy
- **Wire format version** (BCC) changes only when view parsing changes.
- **View assembly contract** changes are rare and visible.
- Plugin versions can change often.
- On disk: store both kernel version and active plugin config hashes in checkpoints.

## 4) Compatibility stance
- Backends churn (structured outputs, decoding constraints). Treat these as plugins.
- The kernel should never depend on a specific LLM backend feature.
