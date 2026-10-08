# CHANGELOG — rev0378

Created: 2026-06-12T23:16:00-04:00  
Base: rev0377

## Added

- `585-nuclear-emergency-preparedness-canonicaldispatch-responsesidecars-deadlineclock-refactor-compact-canon.md`.
- Consolidated FEMA/DHS request `RRT-0378-013`.
- Refined NRC ADAMS/FOIA request `RRT-0378-014`.
- Canonical dispatch batch and supersession ledger.
- Per-request receipt sidecar templates.
- Dispatch deadline clock using estimated receipt date 2026-06-15 for planning only.
- Official artifact search log showing no imported official findings or EOF closure packet located during this pass.
- Active dispatch capsule `evidence-bags/bvps-canonical-dispatch-capsule-rev0378.zip`.

## Changed

- Older request packets are retained but classified as active, superseded-do-not-dispatch, or lineage-only.
- Federal FEMA/Region 3/Region 5 dispatch is consolidated to reduce duplicate federal tickets.
- NRC/EOF ask now explicitly separates Event Notification 58200 trigger text from repair/retest/CAP closure evidence.
- Normalized file/source tables regenerated through file 585 and new sources S1395–S1399.

## Still open

No request is marked sent. No receipt is imported. No response packet is imported. No readiness proofcut is closed.

## Patch before package

- Registered 11 legacy external/SRE source aliases so source-edge validation no longer depends on implicit source IDs.
