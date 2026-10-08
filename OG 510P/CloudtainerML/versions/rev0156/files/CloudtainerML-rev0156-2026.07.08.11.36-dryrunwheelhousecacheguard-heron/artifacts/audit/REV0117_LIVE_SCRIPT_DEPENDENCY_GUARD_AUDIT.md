# Live script dependency guard audit — REV0117

Status: `pass_with_blockers`  
Promotion allowed: `false`

## What went wrong

The rev0116 live one-shot path referenced two tools that were not present: `tools/public_trace_surrogate_rejection_audit.py` and `tools/public_trace_current_trace_lane_audit.py`. Smoke validation passed because it checked current aliases and metadata, but not the closure of Python files called from the live shell wrappers.

## What changed

- Added the missing surrogate-rejection and end-of-lane audit tools.
- Added `tools/current_live_script_dependency_audit.py` to scan stable and current live shell wrappers for missing Python/shell targets and stale executable references.
- Inserted the new dependency audit into both the current run wrapper and one-shot capture wrapper.
- Patched smoke validation to perform the same fast static closure check without importing runtime-heavy model dependencies.
- Added a timeout guard and post-audit forced exit to the public-trace environment preflight so import/cache or torch-shutdown stalls become recorded blockers instead of hanging the turn.

## Remaining blockers

- Real public TinyLlama trace is still absent.
- The handoff builder remains fixture-proven until a real accepted trace feeds it.
- Named-hardware timing remains absent.
- This cloudtainer is concretely blocked by `transformers_not_importable`, no complete local HF snapshot with downloads disabled, and no CUDA timing device.

## Next command

```bash
bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```
