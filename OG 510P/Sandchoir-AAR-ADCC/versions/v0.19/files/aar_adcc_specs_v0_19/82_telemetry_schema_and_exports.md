# 82 — Telemetry Schema + Exports (v0.19)

Telemetry is the only route to optimizing unknown slice behavior.

## 1) Per-agent telemetry fields
- `agent`
- `cursor_window`
- `time_to_first_token_ms`
- `time_to_ctrl_ms`
- `ctrl_parse_ok` (bool)
- `ctrl_parse_repaired` (bool)
- `ctrl_parse_reason` (enum)
- `output_bytes`
- `truncation_suspected` (bool)
- `repair_attempted` (bool)
- `stop_after_ctrl` (bool)
- `view_profile` (normal/emergency)
- `mode`
- `evidence_emitted` (count)
- `patch_proposed` (count)

## 2) Router telemetry fields
- queue depths per channel
- compaction frequency
- ws size/utilization
- selected patch/integrator churn
- verifier runtime stats + cache hit rate

## 3) Export formats
- JSON Lines to disk (default)
- optional: OpenTelemetry spans
- optional: csv snapshots

## 4) Convenience queries (for MetaLLM)
- `telemetry show --agent A1 --window 10`
- `telemetry summary --window 50`
- `telemetry failures --top 5`
- `telemetry export --format jsonl --since <cursor>`
