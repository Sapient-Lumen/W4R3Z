# Mission audit — REV0147 runtimeversionlock-oryx

## Heart of the mission

CloudtainerML is still a claim compiler: claim → hostile falsifier → digest-bound trace/provenance receipts → replayable selector gates → named-hardware timing → promote/kill/pivot. The heart is one real TinyLlama public trace that can be replayed and falsified, not more registry surface.

## What was riskiest this turn

The active path had become much better at failing for the right reasons: project-local cache, offline capture quarantine, selected-snapshot handoff, runtime import smoke, and digest-cache reuse. The next high-risk completion gap was runtime version drift. The requirements file still allowed an unbounded `transformers` install even though the capture adapter depends on a private Llama eager-attention seam rather than only the stable AutoModel API. Current Transformers docs show a new major stable line, so a capable runner could install a new surface, burn time, then fail late—or subtly capture different attention/mask semantics.

## Online grounding used

- Hugging Face Hub docs support pinned revision downloads, `allow_patterns`, custom cache roots, and dry-run planning before download.
- Transformers docs show the current major/stable line and the PyTorch/Python support surface.
- Transformers offline docs support the existing prepare-then-local-only-capture split.
- Transformers attention-backend docs emphasize backend-specific attention and mask semantics, which is exactly the surface this project is trying to intercept faithfully.

## What changed

- Added `tools/public_trace_runtime_requirement_lock_audit.py`.
- Replaced unbounded public-trace runtime requirements with bounded constraints:
  - `numpy>=1.26,<3`
  - `torch>=2.4,<3`
  - `transformers>=4.56,<5`
  - `huggingface_hub>=0.32,<2`
  - `safetensors>=0.4,<1`
  - `hf_xet>=1.1`
- Wired the runtime lock audit into:
  - `REV0147_BOOTSTRAP_PUBLIC_TRACE_ENV.sh` before `pip install -r`;
  - `REV0147_FIRST_REAL_TRACE_ONE_COMMAND.sh` before runtime smoke/snapshot work;
  - `REV0147_PREPARE_TINYLLAMA_SNAPSHOT.sh` before snapshot materialization;
  - `REV0147_RUN_TINYLLAMA_PUBLIC_TRACE.sh` and `REV0147_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh` before capture gates;
  - the compact external-runner smoke surface.
- Changed `tools/public_trace_runtime_import_smoke.py` so Transformers major 5 is a blocker under the current capture contract, not a warning.
- Rebuilt `REV0147_PUBLIC_TRACE_EXTERNAL_RUNNER.zip` with the bounded requirements and the runtime-lock audit.

## Validation status

- `RUN_CURRENT_FIRST_REAL_TRACE.sh` now first reports the runtime requirement lock audit as `pass`, then reaches the expected cloudtainer blocker: missing `transformers` in this runtime.
- `RUN_CURRENT_PUBLIC_TRACE.sh` now reports the runtime requirement lock audit as `pass`, then reaches the expected capture-start blockers: missing local digest-verified TinyLlama snapshot and missing `transformers`.
- Static audits pass for revision metadata coherence, run-manifest coherence, bootstrap runtime, cache-root contract, snapshot digest receipt cache, runtime requirement lock, live script dependency closure, current entrypoint consistency, offline quarantine, selected snapshot contract, preflight handoff, source lock, and trace run packet.
- The external runner packet audit passes with only the expected environment warning for this cloudtainer.

## What is still missing

A real public trace is still missing. This revision does not promote any scientific claim. It reduces the chance that the first capable-machine trace attempt fails late because the runtime floated across an unreviewed Transformers/Llama attention surface.

## Next best move

Run `BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash RUN_FIRST_REAL_TRACE.sh` from `REV0147_PUBLIC_TRACE_EXTERNAL_RUNNER.zip` on a capable machine. Preserve the first generated status/trace/receipt artifacts. If bootstrap fails, keep the exact `REV0147_PUBLIC_TRACE_RUNTIME_REQUIREMENT_LOCK_AUDIT.json` and `REV0147_PUBLIC_TRACE_RUNTIME_IMPORT_SMOKE.json` outputs instead of loosening the runtime bounds blindly.
