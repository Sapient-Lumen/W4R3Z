# Cube hygiene / refactor — rev0029

Scope: compactness and reproducibility cleanup.

## Change

Generated pytest cache directories were pruned from `maintainer_artifacts`:

```text
.pytest_cache/
__pycache__/
```

These directories are runtime byproducts, not source evidence. The reusable evidence remains in:

```text
maintainer_artifacts/*/test_*.py
evidence/*-pytest-run.txt
evidence/*-source-trace.md
data/*_probe_summary.csv
```

## Rationale

```text
- Keep the cube compact and easier to diff.
- Avoid carrying interpreter-version-specific `.pyc` files.
- Preserve reproducibility through explicit tests and captured pytest logs.
```

## Validation

The rev0029 audit checks:

```text
pytest_cache_dirs=0
pycache_dirs=0
embedded_source_dirs=NONE
```
