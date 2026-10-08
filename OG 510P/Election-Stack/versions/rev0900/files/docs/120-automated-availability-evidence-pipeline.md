# Automated availability evidence pipeline

**Track:** A (Deployable core)


## Goal
Make availability evidence reproducible and auditable.

## Pipeline
1. Ingest raw probe results (internal + external)
2. Canonicalize and hash raw data
3. Run deterministic reduction
4. Emit signed evidence objects (URP, OutageAttestation, ParityReport)
5. Anchor into ATL and reference from PBB checkpoints where relevant

## Reproducibility requirements
- store raw-data hash
- store reduction code hash/version
- store config hash

## Tooling
- `tools/availability_log_builder.py` (baseline)