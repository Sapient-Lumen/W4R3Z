# Mission audit — REV0117 live-path script guard

Status: `pass_with_blockers`  
Promotion allowed: `false`  
Package: `CloudtainerML-rev0117-2026.07.06.18.58-livepathscriptguard-lanner`  
Generated: `2026-07-06T18:58:00-04:00`

## Heart of the mission

CloudtainerML is a claim compiler, not a registry. The useful unit is an architecture claim compiled into a hostile falsifier, exact trace/provenance receipt, selector-entry receipt, portable handoff gate, named-hardware timing, and a promote/kill/pivot decision.

## Riskiest unfinished thing

The riskiest gap is still the same: a real public TinyLlama trace has not been produced. The new concrete defect found this turn was more basic and more dangerous than doctrine gaps: the current one-shot capture script referenced two Python tools that were absent from the archive. That means an operator could get past the visible current alias repair and still lose the session inside the live lane.

## What changed

- Added `tools/current_live_script_dependency_audit.py` to statically close the active shell-script dependency surface before capture.
- Added the two missing live-lane tools: `tools/public_trace_surrogate_rejection_audit.py` and `tools/public_trace_current_trace_lane_audit.py`.
- Patched the current run and one-shot wrappers so they run the dependency-closure audit before spending time on capture.
- Patched `tools/smoke_validate.py` so missing Python targets inside current shell wrappers fail package smoke.
- Advanced current wrappers to `REV0117_*` and retargeted stable aliases to them.
- Added supply-chain/reproducibility research notes to keep the handoff archive moving toward standard attestation, provenance, and reproducible-build expectations without adding registry bureaucracy.
- Added a current `REV0117_TINYLLAMA_SOURCE_LOCK.json`; `tools/source_lock_audit.py` now passes.
- Ran local dependency/preflight gates; this cloudtainer is blocked specifically by `transformers_not_importable`, absent complete local HF snapshot with downloads disabled, and no CUDA for named-hardware timing.
- Added a timeout guard and post-audit forced exit to `tools/public_trace_env_preflight.py` so local import/cache or torch-shutdown hangs become bounded blockers.

## What is still missing

1. Real public TinyLlama trace NPZ/provenance.
2. Accepted evaluation receipt, selector-entry receipt, selector-replay, and real-trace portable handoff archive.
3. Named-hardware sparse-vs-dense timing against modern exact/KV/sparse baselines.
4. A stop/pivot memo if the runtime remains unavailable after another direct attempt.

## What went wrong or wasteful

The cube keeps creating gates that are not always forced through the same entrypoint the operator uses. That is wasteful because it allows the archive to look controlled while the live command remains breakable. rev0117 corrects one more instance: active shell scripts now have a dependency-closure audit, and smoke checks that live script targets exist.

## Speculation after online research

The next durable direction is to align the portable handoff with external provenance and reproducibility norms: SLSA/in-toto-style subject digests, fixed build inputs, reproducible timestamp discipline, and standard runtime/resource metadata. That should remain lightweight: the cube needs evidence receipts first, not a standards bureaucracy.

## Next command

```bash
bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```
