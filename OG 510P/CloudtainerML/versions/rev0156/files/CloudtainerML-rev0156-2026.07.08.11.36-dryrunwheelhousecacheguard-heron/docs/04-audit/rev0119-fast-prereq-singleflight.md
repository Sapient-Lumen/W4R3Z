# rev0119 audit/refactor — fast prerequisite single-flight gate

## Risk selected

The riskiest unfinished lane is still the public TinyLlama trace. Rev0118 made the readiness gate logically fail-fast, but a blocked run in this capsule still spent roughly 25 seconds spawning Python subprocesses before reporting blockers already visible from cheap module and filesystem checks.

## Change made

- Added `tools/public_trace_fast_prereq_gate.py`.
- Patched `artifacts/capture-kit/REV0119_RUN_TINYLLAMA_PUBLIC_TRACE.sh` so it runs the fast gate before the broad readiness chain.
- Patched `tools/public_trace_dependency_lock_audit.py` so it avoids importing heavy modules when the cheap dependency surface is already incomplete.
- Patched smoke and the fail-fast contract audit so the current wrapper must contain both the fast gate and the full readiness gate.

## Why this is substantive

This does not add a registry. It removes waste from the only path that matters: `bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`. In the present capsule, the run should stop at `REV0119_PUBLIC_TRACE_FAST_PREREQ_GATE` with missing `transformers` and missing snapshot blockers rather than spending a long pass through downstream readiness probes.

## Still missing

- Installable/importable `transformers` stack.
- Complete reviewed TinyLlama snapshot at the pinned revision.
- Real NPZ/provenance trace.
- Selector/evaluation receipts on that trace.
- Named-hardware timing evidence.
