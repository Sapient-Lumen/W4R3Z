# Reports

`grlab report` builds `report.json` for a run directory.

The report is a lightweight summary over match artifacts intended for quick comparisons and plotting.

## Row fields

Each entry in `report.json.rows` is a per-task summary with (when present):
- `task_id`, `world_id`, `a`, `b`
- `rounds` (executed rounds; can vary under geometric termination)
- `avg_a`, `avg_b`, `coop_a`, `coop_b`, `mutual_c`

## Notes

- `--use-db` reads from `queue.sqlite3`’s artifact index; without it, `grlab` reads artifact files directly.
- Reports are not an authority on provenance; use `docs/PROVENANCE.md` and `grlab verify` for integrity checks.

## HTML view

`grlab report-html runs/<run_id>` renders `report.json` into a static `report.html` (with artifact links when `manifest.json` is present).
