# Link rot and source mutation playbook — rev0011

When a source target changes, the operator should classify the event before doing anything else.

## Event classes

- `same_payload_same_hash`: keep existing accession, update health-check timestamp.
- `same_url_new_hash`: create source-version event and block dependent claims.
- `redirect_same_payload`: record redirect chain; preserve old and new URL.
- `redirect_new_payload`: create source-version event and rollback review.
- `target_missing`: record dead-link candidate; search official archives or docket source.
- `source_page_row_removed`: create source-page drift event; never delete the old observation.
- `source_page_label_changed`: record source-page label change; do not infer legal status.

## Display rule

Until the changed source is reviewed, public display should say only that the source inventory is under recheck. It should not accuse, clear, close, or exonerate.
