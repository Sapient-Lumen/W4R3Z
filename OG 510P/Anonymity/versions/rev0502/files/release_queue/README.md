# Release Queue

This directory holds the slow-release control surface for publication decisions.

## Subdirectories

- `candidates/` for papers under active conservative review
- `hold/` for papers explicitly judged not yet ready
- `published_ready/` for papers cleared for release but not yet published
- `decisions/` for timestamped decision notes
- `QUEUE_INDEX.json` for a machine-readable state summary across Candidate / Hold / Published-ready / Published
- `LATEST_DECISION.md` for the most recent written no-release / hold / publish rationale (generated from `LATEST_DECISION.json`)
- `STATUS.md` / `QUEUE.md` for generated human-readable queue summaries derived from machine state rather than hand-maintained revision prose
- `../publishing/render_queue_surfaces.py` for regenerating those queue-facing markdown surfaces
- `LATEST_DECISION.json` for the same latest decision in machine-readable form
- `DECISION_INDEX.md` / `DECISION_INDEX.json` for compact human/machine-readable histories of timestamped decision notes
- `reports/archive_surface_coherence.json` for the latest agreement check across revision, queue, citation, and public-surface state
- `../START_HERE.md` / `../CONTEXT_PACK.json` for the shortest reentry packets
- `../reports/context_pack_contract.json`, `../reports/transient_surface_audit.json`, `../reports/manifest_sha256_verification.json`, and `../reports/manifest_coverage_audit.json` for shipped-surface trust checks

## Current posture

The queue is intentionally allowed to be sparse or empty.
An empty queue is preferable to a rushed queue.

- `../reports/lifecycle_gate_status.json` for the current stage-by-stage gate status across reentry, citation boundary, queue integrity, review movement, publication execution, and post-publication audit
