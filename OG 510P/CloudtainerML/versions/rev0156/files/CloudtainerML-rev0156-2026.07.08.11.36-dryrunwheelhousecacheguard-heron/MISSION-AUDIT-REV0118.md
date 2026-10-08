# MISSION-AUDIT-REV0118 — fail-fast readiness gate

Revision: `rev0118`  
Package: `CloudtainerML-rev0118-2026.07.06.19.20-failfastreadinessgate-harrier`  
Status: `pass_with_blockers`  
Promotion allowed: `false`

## Heart of the mission

CloudtainerML is most valuable when it acts as a claim compiler: architecture claims must become executable falsifiers, source locks, trace receipts, selector/evaluation gates, and named-hardware timing boundaries. The mission is not to grow registries; it is to make untrusted claims run into evidence or a crisp blocker.

## Risk chosen this turn

The riskiest unfinished path is the public TinyLlama trace lane. In rev0117 the stable live path could enter broad readiness and expensive model/backend probes even after local prerequisite checks already knew this capsule was blocked. That wastes session time and produces ambiguous failure logs instead of the receipt the next operator needs.

## Concrete change

- Reworked `tools/public_trace_readiness_gate.py` into a prerequisite-aware fail-fast gate.
- Retargeted current wrappers to `REV0118_*` scripts.
- Made the stable run wrapper call `public_trace_readiness_gate.py --local-only --strict` unless `ALLOW_DOWNLOAD=1`, in which case it calls `--download --strict`.
- Made one-shot capture and snapshot prepare require `public_trace_env_preflight.py --strict trace`.
- Added `tools/readiness_failfast_contract_audit.py` and smoke coverage for the anti-waste contract.

## What changed philosophically

The cube now treats a blocked runtime as a first-class result. A missing dependency/snapshot/CUDA device should produce a short, named blocker receipt and stop before post-trace or timing probes. That is forward motion because it narrows the next operator's work from “the trace path may be broken” to “repair these prerequisites, then rerun this exact command.”

## What is still missing

- A complete reviewed TinyLlama snapshot under immutable revision control.
- A real NPZ/provenance trace from the public model.
- Selector/evaluation receipts over that real trace.
- Named-hardware CUDA timing receipts.

## Speculation / waste to correct over time

The deepest project risk is that every blocker spawns another layer of doctrine. Rev0118 deliberately adds only one new audit because it closes a live execution defect. Future work should be ruthless: remove or quarantine documents that do not shorten the path to a real trace, and keep the active surface to `RUN_CURRENT_PUBLIC_TRACE.sh`, the source/dependency locks, and the receipts needed to accept or reject promotion.

## Next operator command

```bash
bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```

Expected in this capsule: fail-fast blocker receipt until `transformers`, a complete local snapshot or allowed materialization path, and CUDA timing hardware are available.
