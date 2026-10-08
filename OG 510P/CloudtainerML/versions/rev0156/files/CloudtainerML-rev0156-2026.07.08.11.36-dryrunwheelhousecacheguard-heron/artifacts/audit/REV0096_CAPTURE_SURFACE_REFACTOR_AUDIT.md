# Capture surface refactor audit — REV0096

Status: `pass_with_debt`  
Promotion allowed: `false`

## Active scripts

- `artifacts/capture-kit/REV0096_RUN_TINYLLAMA_PUBLIC_TRACE.sh`
- `artifacts/capture-kit/REV0096_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh`
- `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`
- `artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh`

Historical capture scripts retained: `22`

## Errors

- none

## Debt

- `capture_kit_history_retained_but_deprioritized`
- `mission_audit_history_retained_but_deprioritized`

## Interpretation

The live path is now stable alias -> current revision-specific packet. Historical files remain for provenance and should not be edited before the real trace/timing question is resolved.
