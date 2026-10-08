# Live execution path repair audit — REV0116

Status: `pass_with_blockers`  
Promotion allowed: `false`

## What went wrong

The riskiest defect was not an exotic sparse-attention bug. It was that the current stable run and prepare aliases could send an operator back into historical wrappers while the package still looked broadly coherent. That is how a cube turns into registry archaeology instead of an executable claim compiler.

## What changed

- Added current revision run/one-shot/prepare/bootstrap wrappers.
- Retargeted `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh` and `artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh` to the current wrappers.
- Tightened `tools/smoke_validate.py` so future packages fail if current aliases drift.
- Added `tools/public_trace_handoff_builder.py` and `tools/public_trace_handoff_builder_audit.py` so an accepted trace can be converted into a portable handoff archive without another doctrine turn.
- Rewrote current docs around `bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`.

## Remaining blockers

- Real public TinyLlama NPZ/provenance pair is still absent.
- Builder handoff is fixture-proven only until a real trace passes.
- Named-hardware sparse-vs-dense timing is still absent.

## Next command

```bash
bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```
