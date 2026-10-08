# Active surface trim audit — REV0101

Status: `pass_with_debt`  
Promotion allowed: `false`

Stable run wrapper: `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`  
Stable prepare wrapper: `artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh`

## Errors

- none

## Debt

- `44 historical revision-specific capture scripts retained as provenance; top docs now use stable aliases`

## Interpretation

This removes execution drag: a future runner can use the stable alias and still land on the current revision-specific packet. Historical scripts stay as provenance, not active instructions.
