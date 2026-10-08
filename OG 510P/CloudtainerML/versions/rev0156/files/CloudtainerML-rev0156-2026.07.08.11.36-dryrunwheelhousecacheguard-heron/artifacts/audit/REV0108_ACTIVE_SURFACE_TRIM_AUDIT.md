# Active surface trim audit — REV0108

Status: `fail`  
Promotion allowed: `false`

Stable run wrapper: `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`  
Stable prepare wrapper: `artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh`

## Errors

- `stable_prepare_alias_not_current`
- `top_doc_missing_current_trace_entrypoint:START_HERE_SLIM.md`
- `top_doc_missing_current_trace_entrypoint:PRIORITY-LIST.md`
- `top_doc_missing_current_trace_entrypoint:NEXT-TURN-PROMPT.md`

## Debt

- `74 historical revision-specific capture scripts retained as provenance; top docs now use stable aliases`

## Interpretation

This removes execution drag: a future runner can use the stable alias and still land on the current revision-specific packet. Historical scripts stay as provenance, not active instructions.
