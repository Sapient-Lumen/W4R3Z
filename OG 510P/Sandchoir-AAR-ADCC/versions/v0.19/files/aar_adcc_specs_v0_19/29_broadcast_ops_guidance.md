# 29 — Broadcast Ops Guidance (Terminator / operator notes) (v0.19)

Broadcast is convenient, but has known “double input” failure modes in Terminator/group broadcast on some setups.
Treat broadcast as **unsafe** for long or destructive commands.

## Safe usage pattern
- Broadcast only the minimal “start-of-turn” trigger (idempotent).
- Disable broadcast immediately after sending.
- Prefer pasting a single command rather than typing interactively while broadcast is on.

## Guard rails
- Start with a sentinel: `echo __ADCC_BROADCAST_START__`
- Verify each terminal printed the sentinel exactly once.
- If duplication appears: stop broadcast; switch to per-terminal paste; log incident.

## Workaround
Maintain `boot_prompt.txt` and broadcast:
- `cat boot_prompt.txt | <your_llm_cli>`
This reduces keystroke duplication risk.

See also: 33_operator_io_layer_and_broadcast_alternatives.md

The Gearbox TUI should surface I/O incidents so broadcast glitches don't masquerade as model failure (see 52_gearbox_tui_spec_ratatui.md).

Operator broadcast runbook and anomaly detection: see 75_broadcast_and_operator_sync_protocol.md.
