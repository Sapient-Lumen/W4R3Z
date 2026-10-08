# Current live script dependency audit — REV0140

Status: `pass`  
Promotion allowed: `false`

Static closure audit for the active live shell surface. It checks stable aliases plus current run/one-shot/prepare/bootstrap wrappers for missing Python, shell, and requirement-file targets; stale revision executable references; and non-portable direct exec of nested shell scripts before an operator spends time on a long capture attempt.

## Active scripts checked

- `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`
- `artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh`
- `artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh`
- `artifacts/capture-kit/REV0140_RUN_TINYLLAMA_PUBLIC_TRACE.sh`
- `artifacts/capture-kit/REV0140_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh`
- `artifacts/capture-kit/REV0140_PREPARE_TINYLLAMA_SNAPSHOT.sh`
- `artifacts/capture-kit/REV0140_BOOTSTRAP_PUBLIC_TRACE_ENV.sh`
- `artifacts/capture-kit/REV0140_FIRST_REAL_TRACE_ONE_COMMAND.sh`

## Errors

- none

## Warnings

- none
