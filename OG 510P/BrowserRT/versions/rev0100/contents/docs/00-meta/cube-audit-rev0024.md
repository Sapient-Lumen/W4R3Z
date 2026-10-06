# Cube audit rev0025 — scheduler contract coherence

Revision: rev0028

This audit/factor pass focused on the scheduler lane and future-session legibility.

## What changed

- Added `CrossLaneScheduler` as a fake-provider lane-contract primitive.
- Added `scheduler:cross-lane-contract-proof` as a release-tier proof.
- Added `facility:scheduler-contract-audit` as the coherence guard for the new surface.
- Updated the non-claims charter and future-session handoff surfaces so this does not read like a production scheduler.
- Kept broad release browser-light.

## Coherence checks

The new audit checks:

- source has the scheduler primitive;
- manifest has the proof and audit tasks;
- impact map covers the proof;
- proof artifact observations are true;
- docs name the artifact and non-claims;
- the non-claims charter includes the scheduler non-claims.

## Future risk

The biggest risk is conceptual overreach. Future sessions may see `CrossLaneScheduler` and assume BrowserRT owns scheduling. It does not. It owns a contract vocabulary. Real provider scheduling must be earned lane by lane.
