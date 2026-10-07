# Source-Metadata-Backfill Fields — current

Field schema for Source-Metadata-Backfill-current.*

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| backfill_id | yes | pass-through string | backfill id |
| batch_revision | yes | rev0077/rev0078/rev0079/rev0080/rev0081/rev0083/rev0084/rev0086 | source-health batch revision |
| source_id | yes | pass-through string | source id |
| domain | yes | pass-through string | domain |
| candidate_ids | yes | pass-through string | candidate ids |
| verification_mode | yes | pass-through string | verification mode |
| backfill_status | yes | completed_verified_metadata/completed_partial_direct_error_visible/safety_reclassified_no_public_url/blocked_visible_recheck_needed/manual_context_sensitive_verified_no_public_archive/coverage_reconciled_existing_verified_metadata | backfill status |
| fields_updated | yes | pass-through string | fields updated |
| date_checked | yes | YYYY-MM-DD | date checked |
| maintenance_priority_after | yes | pass-through string | maintenance priority after regeneration |
| public_exposure_effect | yes | pass-through string | public exposure effect |
| evidence_note | yes | pass-through string | evidence note |
| status | yes | pass/fail | status |
| note | yes | pass-through string | note |
