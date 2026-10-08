# 56 — Slice Telemetry + Budget Adaptation (v0.19)

Because slice counts and truncation are unknown, you need a telemetry loop that adapts budgets and protocols mid-flight.

## 1) Slice observables (per agent)
- `time_to_ctrl_ms` (p50/p90)
- `ctrl_parse_success_rate`
- `avg_output_bytes`
- truncation markers (missing terminators, abrupt EOF)
- re-ask frequency (how often repair loop triggers)

## 2) Adaptive budget policy
If time_to_ctrl is high:
- shrink view (line caps) and push mandatory/HOT only
If parse failure is high:
- enable stronger BCC; enable CTRLJSON; enable JSON healing
- CAP probe and enable guided decoding if available
If truncation spikes:
- disable DISCOVERY/RANDOM
- switch to Freeze or PatchOnly to reduce churn

## 3) “Anytime collapse” rule (cheap)
If an agent output ends without `@CTRL`:
- salvage any partial structured content
- post a “missing CTRL” marker to ledger
- do not immediately re-ask unless the system is in a strict mode

## 4) Measurement windows
Use a short rolling window:
- last 10 slices per agent (or last N minutes)
Expose it in the Gearbox.

## 5) What counts as success
- CTRL seen early
- evidence produced
- canonical state changes only after checks
- WS stays under caps

AAR routing is deterministic and testable; see 58_aar_routing_pseudocode.md.

CAP probing + slice proxies: see 71_cli_client_cap_probing_and_slice_measurement.md.

Telemetry fields and exports: see 82_telemetry_schema_and_exports.md.
