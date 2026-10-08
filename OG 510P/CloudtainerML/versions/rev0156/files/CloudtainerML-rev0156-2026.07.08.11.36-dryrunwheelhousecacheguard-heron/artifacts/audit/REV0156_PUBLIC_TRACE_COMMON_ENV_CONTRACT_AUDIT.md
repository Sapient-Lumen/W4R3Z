# Public trace common-env contract audit — REV0156

Status: `pass`  
Promotion allowed: `false`

Ensures active public-trace wrappers source one common Hugging Face/model/offline environment contract before Python runtime imports, instead of drifting through copy-pasted cache and offline exports; also blocks accidental no-symlink cache duplication for large Hub snapshots unless explicitly approved.

## Consumer scripts

- `artifacts/capture-kit/REV0156_FIRST_REAL_TRACE_ONE_COMMAND.sh` mode=`base` sources_common=`True`
- `artifacts/capture-kit/REV0156_PREPARE_TINYLLAMA_SNAPSHOT.sh` mode=`snapshot` sources_common=`True`
- `artifacts/capture-kit/REV0156_RUN_TINYLLAMA_PUBLIC_TRACE.sh` mode=`capture` sources_common=`True`
- `artifacts/capture-kit/REV0156_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh` mode=`capture` sources_common=`True`
- `artifacts/capture-kit/REV0156_BOOTSTRAP_PUBLIC_TRACE_ENV.sh` mode=`base` sources_common=`True`

## Errors

- none

## Warnings

- none
