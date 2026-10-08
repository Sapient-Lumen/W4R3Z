# Public trace capture-start preflight report — REV0136

Status: `blocked_here`  
Decision: `do_not_start_capture`  
Promotion allowed: `false`

## Blockers

- `local_digest_verified_tinyllama_snapshot_not_available`
- `local_integrity_valid_tinyllama_snapshot_not_available`
- `transformers_not_importable`

## Warnings

- none

## Selected snapshot for capture

- path: `none`
- contract: `digest_verified_local_snapshot_path_v1`

## Next repair

- run HASH_WEIGHTS=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh to materialize and hash-check the reviewed TinyLlama snapshot, or mount it via LOCAL_SNAPSHOT_DIR
- install the capture runtime so numpy, torch, transformers, huggingface_hub, and safetensors are visible to this Python interpreter
- rerun capture with ALLOW_DOWNLOAD=0 CAPTURE_LOCAL_ONLY=1 after the local digest-verified snapshot is present
