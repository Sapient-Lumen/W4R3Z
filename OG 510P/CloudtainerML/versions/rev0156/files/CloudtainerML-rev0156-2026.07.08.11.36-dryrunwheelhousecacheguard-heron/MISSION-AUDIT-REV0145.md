# Mission audit — REV0145

Package: `CloudtainerML-rev0145-2026.07.08.04.19-runtimeimportsmoke-kestrel`

## Heart of the mission

CloudtainerML is still a claim compiler, not a registry collection. The valuable object is a replayable claim that can be falsified: a digest-bound public TinyLlama trace, provenance receipts, replay/evaluation receipts, selector-entry evidence, handoff archive, and named-hardware timing. Until that chain exists, the project should mostly remove blockers on the first real trace rather than add new doctrine.

## Riskiest unfinished piece

The riskiest near-term failure was a late runtime failure after snapshot work. REV0144 had improved preflight handoff, but the first-real-trace path could still reach snapshot materialization before proving that the exact Python runtime could import the capture stack and the current Transformers Llama hook surface. That is wasteful because the selected TinyLlama snapshot includes large model bytes.

## Substance change in REV0145

REV0145 adds `tools/public_trace_runtime_import_smoke.py` and wires it into both the project-local venv bootstrap and the one-command first-real-trace runner before snapshot materialization. The smoke proves, without network, that the runtime can import `numpy`, `torch`, `transformers`, `huggingface_hub`, `safetensors`, `hf_xet`, `AutoTokenizer`, `AutoModelForCausalLM`, and the expected Llama eager-attention function surface.

The external runner packet also now requires that smoke tool, so the compact capable-machine path carries the same early-failure contract.

## Audit/refactor performed

- Refactored the first-real-trace path to add an explicit `runtime_import_smoke` phase before `prepare_snapshot`.
- Refactored bootstrap to run the same smoke inside the project-local venv with `--require-project-venv` before writing the current bootstrap env.
- Refactored first-trace status receipts to bind phase blockers from the runtime smoke into `REV0145_PUBLIC_TRACE_FIRST_REAL_TRACE_STATUS.json`.
- Updated the external runner packet builder so the runtime smoke is part of the required compact packet.
- Removed generated Python bytecode caches from the packaged cube; external runner copy logic already ignores `__pycache__`/`*.pyc`.
- Updated active docs and manifests to keep the next action focused on one real trace.

## Current validation result

In this cloudtainer, `ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh` now reaches the intended early blocker at `runtime_import_smoke`. The blocker is `transformers_import_failed` / `transformers_not_present_in_runtime_python`, before snapshot materialization. That is not promotion evidence; it is a useful waste-prevention stop.

Audits passed for live dependency closure, current entrypoint consistency, revision metadata coherence, run-manifest coherence, preflight handoff, digest cache, offline quarantine, first-trace surface, and external runner packet build. The active-surface audit still reports historical capture-script volume as debt, but current docs use stable aliases and the retained scripts are provenance rather than the live path.

## What should change next

Run the external runner on a capable machine with:

```bash
BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash RUN_FIRST_REAL_TRACE.sh
```

The next acceptable failure should be one small, receipt-backed runtime/snapshot error. If runtime import smoke passes, the project should proceed to snapshot materialization, local-only capture, gate/evaluation receipts, and handoff archive generation; only then should selector/timing claims be considered.
