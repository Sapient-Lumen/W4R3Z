# Current live script dependency audit — REV0138

Status: `pass`  
Promotion allowed: `false`

Static closure audit for the active live shell surface. It checks stable aliases plus current run/one-shot/prepare/bootstrap wrappers for missing Python, shell, and requirement-file targets; stale revision executable references; and non-portable direct exec of nested shell scripts before an operator spends time on a long capture attempt.

## Active scripts checked

- `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`
- `artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh`
- `artifacts/capture-kit/REV0138_RUN_TINYLLAMA_PUBLIC_TRACE.sh`
- `artifacts/capture-kit/REV0138_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh`
- `artifacts/capture-kit/REV0138_PREPARE_TINYLLAMA_SNAPSHOT.sh`
- `artifacts/capture-kit/REV0138_BOOTSTRAP_PUBLIC_TRACE_ENV.sh`

## Errors

- none

## Warnings

- none
