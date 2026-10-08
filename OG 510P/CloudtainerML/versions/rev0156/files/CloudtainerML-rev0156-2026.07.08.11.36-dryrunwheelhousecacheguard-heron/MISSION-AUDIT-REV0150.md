# Mission audit — REV0150 runnermanifestfallback-vole

Status: `runner-integrity-refactor-not-evidence`  
Promotion allowed: `false`

## Heart of the mission

CloudtainerML is a claim compiler: claim → hostile falsifier → digest-bound trace/provenance receipts → replayable selector gates → named-hardware timing → promote/kill/pivot. The risky unfinished work is still one real TinyLlama public trace, not more registries.

## What changed

REV0150 fixes a late-run failure that REV0149’s compact runner trim exposed. The external runner intentionally omits most historical cube files and the full-cube `CHECKSUMS.sha256`. But the successful capture path ends by calling `tools/smoke_validate.py`; in a compact runner that would eventually fail at the very end because `CHECKSUMS.sha256` was absent or, if copied from the source cube, would point at thousands of omitted historical files.

The correction is executable:

- `PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json` now deliberately excludes itself from the subject list, avoiding an impossible self-hash.
- New `tools/public_trace_external_runner_manifest_integrity_audit.py` validates every shipped runner subject, required root runner scripts, revision match, subject count, byte total, and subject-set hash.
- `tools/smoke_validate.py` now has an explicit compact-runner mode: when `PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json` exists and full-cube `CHECKSUMS.sha256` is intentionally absent, it validates the runner manifest instead of demanding omitted full-cube files.
- The external-runner builder smoke now runs both the new manifest-integrity audit and `smoke_validate.py` inside the extracted packet, so this late failure is caught before handoff.

## Online research basis

Current Hugging Face Hub docs still support the underlying operating assumptions: downloads are version-aware and cached; `snapshot_download` supports specific revisions, file filters, local folders, CLI dry-run byte planning, and local cache control; Hub env vars are read at import time and `HF_HUB_OFFLINE` prevents HTTP calls; cache docs describe blob/snapshot/chunk indirection and cached immutable tree metadata. Current Transformers docs continue to support the prepare-then-local-capture split using offline/local-files-only loading. These facts justify a compact runner that verifies its own shipped subject manifest and allows generated cache/trace outputs as extras, rather than pretending it is the whole source cube.

## Why this is substance, not registry work

This is a concrete completion-risk repair. Without it, a capable-machine run could pay the cost of bootstrap, large snapshot preparation, digest checks, local-only capture, evaluation, selector entry, replay, and handoff, then die in final smoke because the compact packet is not the whole datacube. REV0150 moves that failure to extracted-runner packet build time and gives the runner a valid subset integrity contract.

## Validation snapshot

- `python3 -m py_compile tools/smoke_validate.py tools/public_trace_external_runner_packet_builder.py tools/public_trace_external_runner_closure_audit.py tools/public_trace_external_runner_manifest_integrity_audit.py`: pass.
- `python3 tools/public_trace_external_runner_manifest_integrity_audit.py --strict` in the source cube: expected fail before packet build because the source cube is not an extracted runner and has no runner manifest.
- Extracted-runner packet smoke now runs manifest-integrity audit and `smoke_validate.py` fallback as part of packet build.
- Live capture remains blocked here by missing `transformers` and missing digest-verified TinyLlama snapshot; REV0150 does not claim a trace.

## Remaining blocker

Run the one-command path on a capable machine:

```bash
BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash RUN_FIRST_REAL_TRACE.sh
```

If that fails, repair the first receipt-backed blocker it returns before adding doctrine.
