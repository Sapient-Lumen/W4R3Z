# Verifier profiles (stable capability claims)

**Track:** Shared

This document indexes **verifier profile IDs** from `artifacts/registries/verifier-profiles.csv`. Verifiers MAY claim these IDs in `hfv.verifier.report.supported_profiles` so independent observers can compare what implementations actually support.

## Registry digest

- `artifacts/registries/verifier-profiles.csv` — `sha256:8beec259f650c600db1363a16446c61bf75f4d9fef7b042b48b7844f37087b6c`

## Profiles

### `tes.verifier.profile.closeout_index.v1`

Precinct closeout omission detection support.

Required envelope kinds:

- `hfv.results.closeout_index`

### `tes.verifier.profile.public_comms_discovery.v1`

Public communications & discovery surfaces for real incidents.

Required envelope kinds:

- `hfv.coverage.liveness_beacon`
- `hfv.public.notice`
- `hfv.public.notice_feed`
- `hfv.public.notice_signing_keyset`
- `hfv.public.official_channel_directory`
- `hfv.public.surface_parity_snapshot`
- `hfv.public.well_known_discovery`

### `tes.verifier.profile.publishable_reports.v1`

Publishable verifier output kinds for ecosystem comparability.

Required envelope kinds:

- `hfv.verifier.packet_verification_report`
- `hfv.verifier.report`

### `tes.verifier.profile.track_a_base_integrity_ingest.v1`

Track A base integrity: minimum kinds a verifier must be able to ingest offline.

Required envelope kinds:

- `hfv.coverage.report`
- `hfv.election.parameters_bundle`
- `hfv.incident.after_action_report`
- `hfv.inspection.challenge_schedule`
- `hfv.inspection.gossip_message`
- `hfv.inspection.suppression_report`
- `hfv.results.enr_update`

### `tes.verifier.profile.verifier_ecosystem_meta.v1`

Meta surfaces that make verifier capacity visible (who will look; where reports land).

Required envelope kinds:

- `hfv.verifier.capacity_roster`
- `hfv.verifier.packet_verification_report`
- `hfv.verifier.report`
- `hfv.witness.liveness_dissent_report`

### `tes.verifier.profile.witness_governance.v1`

Witness governance + behavioral health surfaces (quorum + liveness+dissent).

Required envelope kinds:

- `hfv.witness.liveness_dissent_report`
- `hfv.witness.set`
- `hfv.witness.set_change`

## Notes

- Profiles are intentionally **small**. When you need to communicate additional constraints (e.g., receipt tiers, transport, or UI expectations), do so in a publishable verifier narrative, not by proliferating profile IDs.
- Kind semantics and schemas live in `docs/EVIDENCE_OBJECT_CATALOG.md` (generated) and the underlying registries/schemas.
