# Data Management

## Artifact Classes

- `goldens/`: committed reference baselines.
- `artifacts/`: ephemeral outputs from checks/runs.
- `runs/`: experiment-run outputs.

## Retention

- Use `make clean-test-artifacts` (dry-run default) to prune stale files.
- Keep golden baselines small, textual, and reviewable.

## Provenance

- Keep all claims linked to hashed artifacts and definitions.
- Export public bundles via redaction workflows.
