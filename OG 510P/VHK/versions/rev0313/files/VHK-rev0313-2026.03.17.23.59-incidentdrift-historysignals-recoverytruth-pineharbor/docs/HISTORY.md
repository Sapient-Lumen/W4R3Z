# Run history

VHK writes one JSONL event log per run (``run_*.jsonl``) when
``settings.event_log: true``.

The `vhk history` command summarizes these logs into a quick table of recent
runs:

- OK/fail
- duration
- retry count
- how many wait-loop polling attempts happened

## Examples

Show the most recent 20 runs:

```bash
vhk history .
```

Only show failing runs:

```bash
vhk history . --status fail
```

Machine-readable JSON (good for dashboards):

```bash
vhk history . --json
```

Export as CSV:

```bash
vhk history . --csv out.csv
```

CI-friendly mode:

```bash
# exit 1 if any run in the table failed
vhk history . --status fail --check
```
