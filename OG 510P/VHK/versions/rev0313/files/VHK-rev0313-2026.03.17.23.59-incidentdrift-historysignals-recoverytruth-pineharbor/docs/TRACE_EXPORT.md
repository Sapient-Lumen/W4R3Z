# Trace export (Perfetto / Chrome)

VHK writes a JSONL *event log* (`run_*.jsonl`) when `settings.event_log: true`.
This log is great for the `vhk report` CLI, but sometimes you want a real
timeline UI.

VHK can export a run log into the widely supported **Chrome Trace Event** JSON
format, which you can open in:

- **Perfetto UI** (supports the legacy JSON trace format)
- Chrome's tracing viewer (`chrome://tracing` / legacy UI)

## Exporting a trace

```bash
vhk trace logs/run_20260227_120001_123.jsonl --out logs/run_20260227_120001_123.trace.json
```

Or pick the latest run from a project:

```bash
vhk trace --project . --latest --out logs/latest.trace.json
```

## Viewing in Perfetto

1. Open https://ui.perfetto.dev/
2. Drag-and-drop the exported `*.trace.json` file into the UI.

## What's inside the trace

The trace contains separate tracks per macro:

- `macro:steps` (each step attempt with duration)
- `macro:waits` (wait intervals, e.g. `wait:image`)
- `macro:attempts` (wait polling attempts)

This makes it easy to spot:

- slow steps
- retry storms
- time spent waiting vs doing

## Notes

- Trace timestamps are normalized to start at 0 for easier viewing.
- Some synthetic/test logs only have `step_end` events. In that case, VHK
  infers the start time from `ts - duration_ms`.
- Perfetto treats the Chrome JSON trace format as **legacy** and supports it
  on a best-effort basis. VHK intentionally emits mostly `X` (complete) events
  and avoids the more exotic async/flow features to maximize compatibility.
