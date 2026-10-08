# Record templates

Use `witnessed-moment-record-template.json` for new work.

The older rev0001 observation template, if present, is superseded by `RECORD-SCHEMA.json` v2 and should not be used for new records.

- `perspective-record-template.json` — witness-position / account-authority / role-boundary records.


## Rev0014 final audit note
The final audit packaging pass reconciled reader-router alias IDs to the canonical DV-SA namespace and added `publication_review_state: blocked` to every quarantined record. `make check` now runs both lint and the compact audit summary.
