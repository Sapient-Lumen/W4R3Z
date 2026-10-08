## REV0153 — blockerfirstliveprune-lynx — 2026-07-08 09:18 America/New_York

- Added semantic-currentness smoke and `tools/semantic_currentness_audit.py` to prevent stale current docs/metadata from passing.
- Rewrote the top current docs around the first-real TinyLlama trace lane.
- Recentered `BABY-DATACUBE-CANDIDATE.json` on the trace chain and removed the stale value-norm next step.
- Pruned stale derived external-runner packets and generated Python bytecode caches.
- Rebuilt the current compact external runner and preserved the non-promotional claim boundary.

## REV0151 — missionwastesemanticdrift-ibis — 2026-07-08 08:52 America/New_York

- Added a deep mission/waste/semantic-drift audit.
- Retargeted current capture-kit aliases and run-manifest surfaces to rev0151 without promoting a trace claim.
- Documented source-rev0150 duplicate/storage waste and semantic metadata drift.
- Preserved the first-real-trace entrypoint: `BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh`.

# Changelog

## rev0150 — runnermanifestfallback-vole

- Added a runner-local manifest integrity audit for compact external public-trace packets.
- Changed external-runner manifests to exclude `PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json` from their subject list, avoiding an unverifiable self-hash.
- Refactored `smoke_validate.py` so an extracted compact runner validates `PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json` when full-cube `CHECKSUMS.sha256` is intentionally absent.
- Wired extracted-packet smoke to run the new manifest integrity audit and the `smoke_validate.py` fallback before handoff.
- Keeps the claim boundary unchanged: no public trace, selector receipt, handoff, or named-hardware timing exists in this cloudtainer.

## rev0149 — runnerclosuretrim-hawk

- Refactors the external public-trace runner builder to copy only the first-real-trace live-script closure instead of the entire tools directory.
- Adds a closure audit/receipt to catch missing reachable scripts, missing imports, and surplus runner tools before packaging.
- Refactors runtime import smoke into a cheap-discovery-first gate: when required modules such as `transformers` are absent, it fails immediately and skips heavy imports instead of burning CPU.
- Makes external-runner packet smoke use the live-closure audit plus a syntax/runtime-import/public-run/direct-alias smoke surface, avoiding subprocess/trap side effects during packet construction while preserving source-tree first-real-trace validation.
- Keeps the same claim boundary: no public trace is claimed until a digest-verified TinyLlama snapshot, local-only capture, selector receipts, replay, handoff, and named-hardware timing exist.

## rev0148 — downloadplangate-auk

- Added `tools/public_trace_runtime_requirement_lock_audit.py` and wired it into bootstrap, first-real-trace, snapshot-prepare, capture wrapper, one-shot, and external-runner smoke.
- Replaced unbounded public-trace runtime requirements with bounded constraints: `numpy>=1.26,<3`, `torch>=2.4,<3`, `transformers>=4.56,<5`, `huggingface_hub>=0.32,<2`, `safetensors>=0.4,<1`, and `hf_xet>=1.1`.
- Changed runtime import smoke so a Transformers major-version escape is a blocker, not a warning, because the capture path depends on a private Llama eager-attention seam.
- Rebuilt the compact external runner with the runtime-lock audit in its smoke surface.
- Kept the expected cloudtainer blocker honest: missing local digest-verified TinyLlama snapshot and missing `transformers` still stop capture here.

## rev0146 — localcachecontract-heron

- Added `tools/public_trace_cache_root_contract_audit.py` and wired it into bootstrap, snapshot-prepare, first-real-trace, run, one-shot, and external-runner paths.
- Defaulted public-trace Hugging Face/Xet cache state to `artifacts/runtime/public-trace-hf-cache` through `PUBLIC_TRACE_CACHE_ROOT`, `HF_HOME`, `HF_HUB_CACHE`, `HF_XET_CACHE`, and `HF_ASSETS_CACHE`.
- Persisted cache-root exports into generated bootstrap and capture env files with a portable dynamic root rather than an absolute extraction path.
- Updated the TinyLlama run packet, source lock, and external runner manifest so cache-root behavior is part of the replay contract.
- Pruned stale derived external-runner packets before rebuilding the current compact runner.

## rev0145 — runtimeimportsmoke-kestrel

- Added `tools/public_trace_runtime_import_smoke.py`, an import-only capture-runtime and Transformers/Llama surface smoke.
- Wired runtime smoke into the project-local venv bootstrap and the first-real-trace one-command path before snapshot materialization.
- Updated requirements to make `huggingface_hub>=0.32` explicit while keeping `hf_xet` visible for large Xet-backed downloads.
- Rebuilt active docs/run surfaces around the next concrete blocker: prove runtime, then materialize snapshot, then capture local-only.
- Removed generated Python bytecode caches from the package to reduce drift and waste.

## rev0144 — preflighthandoffflag-wren

- Added an explicit capture-preflight handoff contract from the stable wrapper to the one-shot runner.
- Preserved direct one-shot execution with full fallback preflight.
- Added `tools/public_trace_capture_preflight_handoff_audit.py` and wired it into smoke/live-surface checks.
- Updated active docs, run manifests, source lock, and external runner references to rev0145.

## rev0143 — offlinecapturequarantine-tern

- Forced evidence capture into Hugging Face/Transformers offline quarantine after snapshot preparation.


## REV0156 — shell syntax bootstrap fix

- Fixed public-trace bootstrap requirements path concatenation.
- Fixed snapshot-prepare Bash syntax.
- Added bootstrap dry-run verification.
- Added active shell syntax and adjacent assignment-concatenation gates to smoke/current live dependency audits.


## REV0156 — dry-run wheelhouse cache guard

- Fixed one-command bootstrap dry-run fallthrough.
- Added optional `PUBLIC_TRACE_WHEELHOUSE` no-index bootstrap support.
- Added cache-duplication guard for `HF_HUB_DISABLE_SYMLINKS=1`.
- Added and wired `public_trace_cache_duplication_guard_audit.py`.
