# Reproducibility

Concord reproducibility relies on deterministic execution and auditable artifacts.

## Controls

- Fixed environment defaults: `TZ=UTC`, `LC_ALL=C`, `PYTHONHASHSEED=0`.
- Explicit test seed policy with replay support.
- Seed, timing, and environment metadata artifacts emitted per run.
- No-network defaults for test harnesses.

## Repro Bundle

Use:

```bash
make report-repro-bundle
```

This writes `artifacts/reports/repro_bundle_index.json`, which enumerates evidence files and replay commands.
