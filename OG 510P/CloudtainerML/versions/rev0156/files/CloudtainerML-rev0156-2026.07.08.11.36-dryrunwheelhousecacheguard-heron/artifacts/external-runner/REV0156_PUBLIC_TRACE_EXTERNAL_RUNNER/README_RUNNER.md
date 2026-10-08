# REV0156 public-trace external runner packet

Current revision: `rev0156`.

This is the live-closure packet for the riskiest unfinished work: producing the first real digest-bound TinyLlama public trace. It intentionally omits historical mission audits, idea ledgers, older capture-kit wrappers, and tool files not reachable from the current first-real-trace path.

## Status boundary

- Promotion allowed: `false`.
- This packet is a runner, not evidence.
- A real claim still requires: digest-verified TinyLlama snapshot → capture → evaluation receipt → selector-entry receipt → replay gate → handoff archive gate → named-hardware sparse-vs-dense timing.

## Commands

0. One-command path for the first real trace. By default, Hugging Face/Transformers/Xet cache files go under `artifacts/runtime/public-trace-hf-cache` inside this runner; set `PUBLIC_TRACE_CACHE_ROOT=/path/to/cache` to override:

```bash
BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash RUN_FIRST_REAL_TRACE.sh
```

For a host with a prebuilt wheelhouse/no-index policy:

```bash
PUBLIC_TRACE_WHEELHOUSE=/path/to/wheels BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash RUN_FIRST_REAL_TRACE.sh
```

Or, with an already reviewed snapshot:

```bash
LOCAL_SNAPSHOT_DIR=/path/to/TinyLlama-snapshot bash RUN_FIRST_REAL_TRACE.sh
```

Manual phase path:

1. Optional runtime bootstrap; this creates/uses a project-local `.venv-public-trace` and writes `artifacts/runtime/CURRENT_PUBLIC_TRACE_BOOTSTRAP_ENV.sh`:

```bash
bash BOOTSTRAP_RUNTIME.sh
```

For manual shells, source the generated env before later phases:

```bash
source artifacts/runtime/CURRENT_PUBLIC_TRACE_BOOTSTRAP_ENV.sh
```

2. Materialize the reviewed snapshot on a machine where downloads are allowed:

```bash
HASH_WEIGHTS=1 ALLOW_DOWNLOAD=1 bash PREPARE_SNAPSHOT.sh
```

3. Capture only from local verified files:

```bash
ALLOW_DOWNLOAD=0 CAPTURE_LOCAL_ONLY=1 bash RUN_PUBLIC_TRACE.sh
```

4. Or mount an already reviewed flat snapshot:

```bash
LOCAL_SNAPSHOT_DIR=/path/to/TinyLlama-snapshot ALLOW_DOWNLOAD=0 CAPTURE_LOCAL_ONLY=1 bash RUN_PUBLIC_TRACE.sh
```

Reviewed run packet: `artifacts/run-manifests/REV0156_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json`.

## Why this exists

The full cube has useful history, but the current failure mode is operational: the real trace needs a runtime and a large model snapshot. This packet gives an external runner the current live closure without asking it to wade through the whole datacube or carry unrelated probe tools.
