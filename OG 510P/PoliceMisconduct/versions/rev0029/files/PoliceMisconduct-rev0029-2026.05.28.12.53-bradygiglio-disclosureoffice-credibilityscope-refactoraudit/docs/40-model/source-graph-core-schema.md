# Source graph core schema

The source graph is the first layer of the cube.

## Source row

A source row is a pointer to a public-record carrier. It should not carry extracted misconduct facts.

Minimum fields:

- `row_id`
- `record_kind`
- `source_url`
- `source_owner`
- `source_accessed_at_utc`
- `state_or_territory`
- `matter_label`
- `agency_names`
- `source_page_status_label`
- `document_classes_present_from_page_label`
- `display_class`
- `person_level_claims_admitted`
- `incident_level_claims_admitted`
- `status_interpretation_rule`

## Source document

A source document is a document linked from or associated with a source row.

Minimum fields:

- `source_document_id`
- `source_row_id`
- `title`
- `document_class`
- `issuer`
- `date_label`
- `url`
- `accessed_at_utc`
- `local_hash_sha256` if frozen
- `person_exposure_risk`
- `claim_power`

## Status event

A status event is a source-scoped temporal event.

Minimum fields:

- `status_event_id`
- `agency_or_matter`
- `event_date`
- `event_source_type`
- `status_label`
- `source_url`
- `confidence`
- `display_permission`
