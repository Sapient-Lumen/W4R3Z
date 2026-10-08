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
