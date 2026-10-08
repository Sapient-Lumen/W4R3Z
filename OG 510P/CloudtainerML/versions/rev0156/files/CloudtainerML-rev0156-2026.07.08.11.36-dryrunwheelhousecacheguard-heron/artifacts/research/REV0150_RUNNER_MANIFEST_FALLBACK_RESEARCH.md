# REV0150 runner manifest fallback research

Status: `research_support_not_evidence`  
Promotion allowed: `false`

The online check supports a narrow operational change, not a scientific claim. Current Hugging Face Hub docs describe version-aware local caching, `snapshot_download` at a revision, file filters, local folders, CLI dry-run byte planning, cache roots, Xet cache variables, and offline behavior. Current Transformers docs describe offline execution through pre-downloaded local files plus `HF_HUB_OFFLINE`/`local_files_only`.

## Implication for this cube

The compact external runner is intentionally not the whole datacube. After a capable-machine run, it should verify the files it actually shipped plus generated trace receipts, not fail final smoke because `CHECKSUMS.sha256` for omitted historical cube files is absent. REV0150 therefore gives the external runner a non-self-referential subject manifest and makes `smoke_validate.py` switch to that runner-local manifest when `PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json` exists and full-cube `CHECKSUMS.sha256` is intentionally absent.

## Boundary

This is still not public trace evidence. It only prevents a late, avoidable, post-capture packaging failure.
