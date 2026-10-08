# Mission audit — REV0103 device/dtype/timing gate

Revision: `rev0103`  
Package: `CloudtainerML-rev0103-2026.07.06.14.08-devicedtypetiminggate-harrier`  
Status: `pass_with_blockers`  
Promotion allowed: `false`

## Heart of this turn

The riskiest unfinished work is still the real public/pretrained TinyLlama trace plus named-hardware timing. REV0103 does not add a claim; it narrows a false-green gap that could invalidate the future trace after prompt, backend, and cache identity have already been pinned.

The new contract asks a simple capture-time question: **what exact dtype, device placement, and timing clock produced the trace rows?** A trace can no longer be treated as public evidence just because tokenization/cache/backend fields pass while load dtype, parameter devices, CUDA synchronization, or timing semantics remain implicit.

## Concrete changes

- Added `trace_runtime_device_dtype_timing_v1` provenance to `experiments/public_trace_capture/hf_attention_trace_capture.py`.
- Added `--torch-dtype` and `--device` to the public capture helper and current REV0103 launchers.
- Added runtime metadata fields for requested/resolved dtype, requested/actual device, parameter dtype/device sets, CUDA availability/device identity, timing clock, CPU perf-counter timing, CUDA synchronization, capture elapsed seconds, and named-hardware timing boundary.
- Added gate-side `verify_runtime_provenance_contract(...)` rejection logic so an otherwise dense-parity-valid NPZ is refused if runtime provenance is missing or contradictory.
- Added `tools/public_trace_device_dtype_timing_audit.py` with forged/missing runtime contract cases.
- Integrated the new audit into the one-command readiness gate.
- Refactored current capture wrappers so `RUN_CURRENT_PUBLIC_TRACE.sh` routes to REV0103 and exports `TRACE_TORCH_DTYPE=float32` and `TRACE_DEVICE=auto` by default.

## Online research used

- Hugging Face model loading and generation surfaces make runtime arguments and cache behavior part of trace semantics.
- Hugging Face attention backends are selectable, so backend identity must remain coupled to dtype/device provenance.
- PyTorch CUDA events and synchronization semantics are distinct from ordinary CPU wall-clock timing; capture timing must identify which clock/sync path it used.

## Blockers intentionally preserved

- `public_pretrained_trace_missing`
- `complete_tinyllama_snapshot_missing_here`
- `runtime_dependencies_missing_here`
- `hf_network_dry_run_or_snapshot_download_not_available_here`
- `named_hardware_sparse_vs_dense_timing_missing`

## Decision

This revision is real forward motion because it makes the future capture more falsifiable, not more decorated. It reduces the chance that the eventual public trace is rejected after the fact for hidden dtype/device/timing drift.
