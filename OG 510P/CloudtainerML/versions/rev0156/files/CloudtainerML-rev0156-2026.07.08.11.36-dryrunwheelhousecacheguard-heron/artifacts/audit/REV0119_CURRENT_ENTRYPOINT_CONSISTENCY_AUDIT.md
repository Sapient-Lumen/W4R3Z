# Current entrypoint consistency audit — REV0119

Status: `fail`  
Promotion allowed: `false`

Stable run alias: `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`  
Stable prepare alias: `artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh`

## Errors

- `stale_revision_entrypoints_near_top`

## Debt

- `116 historical capture scripts retained as provenance only`

## Interpretation

This is the small refactor that prevents execution drag: operators start from one stable alias while revisioned wrappers remain for provenance.
