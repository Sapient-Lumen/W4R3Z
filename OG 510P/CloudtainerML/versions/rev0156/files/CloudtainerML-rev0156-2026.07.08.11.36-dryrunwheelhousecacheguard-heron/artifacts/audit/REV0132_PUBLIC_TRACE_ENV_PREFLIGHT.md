# Public trace environment preflight — REV0132

Status: `blocked_here`  
Promotion allowed: `false`

Trace ready: `false`  
Timing ready: `false`

## Blockers

- `transformers_not_importable`
- `no_integrity_valid_local_hf_snapshot_and_download_not_allowed`
- `no_digest_verified_local_hf_snapshot_and_download_not_allowed`

## Warnings

- `cuda_not_available_named_hardware_timing_blocked_here`

## Environment

- Python: `3.13.5`
- torch: `2.10.0+cpu`
- transformers: `missing`
- huggingface_hub: `1.16.1`
- CUDA available: `False`
- local integrity-valid snapshot: `False`
- digest-verified snapshot: `False`
- require weight hash: `True`
- allow download: `False`
- capture local-only: `True`
- allow download for snapshot preflight: `False`
- free disk GB: `8589934590.971`

## Interpretation

This is the execution gate that was missing from earlier packets. It turns an unrun public trace into a concrete repair list: dependencies, shared-integrity snapshot/cache state, download policy, disk, and timing hardware. For capture-local-only runs, download permission is ignored; a digest-verified local snapshot must exist before capture starts. It intentionally does not promote anything.
