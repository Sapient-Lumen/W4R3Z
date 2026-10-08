# 15 — Streaming Bridge (Optional) (v0.19)

If the CLI/client allows partial streaming reads, the router may “early-capture” control-plane data.

## Allowed early-capture
- `@CTRL` and `@VOTE` lines only.

## Disallowed early-capture
- patch diffs
- exports / artifact content
- long notes

## Early-capture rules
- If partial `@CTRL` is incomplete/unparseable: do not promote; wait or request repair.
- Emit telemetry: `bcc.ctrl_seen(t_ms)` even if partial.
- Early-capture never changes canonical state directly; it only informs views and budgets.

See also: 26_capability_handshake.md (CAP#) and 09_bandwidth_adapter_plugin.md (budget tuning).
