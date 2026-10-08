# Public trace snapshot intake audit — REV0102

Status: `not_provided`  
Promotion allowed: `false`

Model id: `TinyLlama/TinyLlama-1.1B-Chat-v1.0`  
Model revision: `fe8a4ea1ffedaf415f4da2f062534de366a451e6`  
Local snapshot dir: `not set`

## Blockers

- none

## Warnings

- `local_snapshot_dir_not_set`

## Interpretation

This audit enables an offline/operator path: set `LOCAL_SNAPSHOT_DIR` to a reviewed flat snapshot directory, keep `MODEL_ID` as the canonical HF id, and let the launcher pass `--public-model-id` so provenance does not become a local filesystem path.
