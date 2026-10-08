# Mission audit — REV0138

Status: `non_promotional_forward_progress`  
Promotion allowed: `false`  
Current run alias: `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`

## Heart of the mission

CloudtainerML is a **claim compiler**. Its product is not a list of ideas, a registry of sparse-attention mechanisms, or a growing set of policy documents. The useful unit is: architecture claim → hostile falsifier → exact/provenance/cost gate → replayable selector/evaluation receipt → portable reviewer handoff → named-hardware timing → promote/kill/pivot.

The current center is therefore the TinyLlama public-trace lane: prove that a public pretrained model, selected by immutable snapshot/digest identity, can produce a trace whose score path, cache path, masks, positions, token provenance, generation settings, backend identity, and downstream receipts are replayable by a cold reviewer.

## What is missing

1. A complete local digest-verified TinyLlama snapshot.
2. An importable `transformers` runtime in the capture environment.
3. A real accepted public-trace NPZ/provenance pair.
4. Accepted evaluation and selector-entry receipts over the real trace.
5. A portable handoff archive whose subject digests replay outside the original session.
6. Named-hardware sparse-vs-dense timing before any performance/promotion claim.

## What should change

The cube should become more ruthless about distinguishing **mission machinery** from **mission-adjacent doctrine**. Add gates only when they shorten the path to the real trace or prevent a concrete live-path failure. Everything else should be summarized, content-addressed, or quarantined as historical context.

Operationally, the next work should be boring and direct: prepare/mount the snapshot, install/import the runtime, run the stable alias, and capture receipts. Mechanism ideation should pause until the public trace produces actual selector/cost evidence.

## What went severely wrong or wasteful this turn

The active shell path was broken in a very practical way. In this extracted zip, `RUN_CURRENT_PUBLIC_TRACE.sh` and `PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh` directly `exec`ed revision-specific scripts that were not executable. That means the package could pass static current-script closure audits while the operator-facing command failed with `Permission denied` before reaching the intended preflight blocker. The bootstrap script also referenced a missing current requirements file.

This is wasteful because it burns the first operator action and hides the real blockers behind a transport/permission accident. Rev0138 corrects it by using `exec bash ...`, copying the requirements file forward, and extending the dependency audit to reject direct shell `exec` and missing requirement locks.

## Speculation

The deepest long-term risk is not that CloudtainerML lacks ideas; it has too many candidate lanes. The risk is that it learns to celebrate well-instrumented blockers while never producing the first real public trace. If the next few turns cannot materialize the TinyLlama snapshot/runtime, the honest move is a stop/pivot memo plus an external-runner packet, not more internal audits.

A second risk is trace-semantic drift. Modern Transformers exposes multiple attention and cache paths; eager attention may be the right trace semantics lane, while SDPA/Flex/Flash paths belong in separate timing/baseline lanes. Mixing these prematurely would let a speed result masquerade as a trace-fidelity result.

A third risk is storage rot. The package is already carrying thousands of historical files and hundreds of revision-specific scripts. Keep the history, but make the active surface tiny and content-address old bulky artifacts into immutable objects.

## Validation performed in this cloudtainer

- Before repair, `bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh` exited with shell `Permission denied`.
- Running `bash artifacts/capture-kit/REV0137_RUN_TINYLLAMA_PUBLIC_TRACE.sh` reached the intended `blocked_here` preflight receipt: missing digest-verified TinyLlama snapshot and `transformers_not_importable`.
- Rev0138 patches the stable aliases and hardens `tools/current_live_script_dependency_audit.py` so this permission/requirements closure failure is detectable.

## Next command

```bash
bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```

Expected in this capsule: a clean `blocked_here` preflight receipt, not a permission error, until the snapshot and runtime are supplied.
