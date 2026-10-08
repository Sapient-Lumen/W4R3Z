# Current entrypoint consistency audit — REV0108

Status: `fail`  
Promotion allowed: `false`

Stable run alias: `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`  
Stable prepare alias: `artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh`

## Errors

- `stable_prepare_alias_not_current_revision`
- `top_doc_missing_current_run_alias:START_HERE_SLIM.md`
- `top_doc_missing_current_run_alias:PRIORITY-LIST.md`
- `top_doc_missing_current_run_alias:NEXT-TURN-PROMPT.md`

## Debt

- `74 historical capture scripts retained as provenance only`

## Interpretation

This is the small refactor that prevents execution drag: operators start from one stable alias while revisioned wrappers remain for provenance.
