# Reporting on runs (event logs)

VHK can write a lightweight **JSONL event log** for each macro run. These logs
record step start/end events, retries, and wait loops. The intent is to power a
future Studio “timeline” UI, but the CLI already provides useful summaries.

## `vhk report`

Summarize a single `run_*.jsonl` file:

```bash
vhk report logs/run_20260227_120001_123.jsonl
```

Show only the slowest steps (similar to pytest’s `--durations` report):

```bash
vhk report logs/run_*.jsonl --durations 15 --durations-min 0.05
```

Use the newest run from a project:

```bash
vhk report --project . --latest
```

Machine-readable output (for dashboards / CI):

```bash
vhk report --project . --latest --json
```

Exit non-zero if the run failed:

```bash
vhk report --project . --latest --check
```

## What the report shows

- Overview: run id, macro, duration, success/failure.
- Slowest steps: aggregated by `step_id` + `step_type` (total/avg/max duration).
- Wait attempts: how many polling loops executed per wait kind.
- Wait durations: total/avg/max time spent inside each wait kind (best-effort).
- Failing steps: error type/message and any captured screenshot path.
- Optimization advice: heuristic guidance for common Linux automation bottlenecks such as delay-heavy runs, vision-heavy waits, retry/capability issues, and slow text injection.


## Why the advice exists

VHK already has a large feature surface (vision, IPC watchers, clipboard rules, portal-aware diagnostics, recorder cleanup). The hard part is helping authors connect a *specific slow/flaky run* back to the right lever.

The advice section in `vhk report` is intentionally conservative:

- it only uses data already present in the event log
- it points toward existing VHK primitives instead of abstract "AI tuning"
- it is designed so future Studio surfaces can reuse the same summarized data

Treat it as a Linux-native counterpart to the "record, inspect, clean up" loop that makes tools like Pulover's Macro Creator productive.
