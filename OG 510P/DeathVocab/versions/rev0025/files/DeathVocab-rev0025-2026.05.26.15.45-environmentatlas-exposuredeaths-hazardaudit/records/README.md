# Records

Revision: rev0005

All records currently live in `records/quarantine/`.

Counts:

- quarantined public-source pilot records: 28
- public records: 0
- private contributor records: 0

Records `DV-REC-000001` through `DV-REC-000016` are threshold-observation pilots from earlier revisions.

Records `DV-REC-000017` through `DV-REC-000028` are rev0005 practice-layer pilots. They are care/practice records, not instructions.


## Rev0014 final audit note
The final audit packaging pass reconciled reader-router alias IDs to the canonical DV-SA namespace and added `publication_review_state: blocked` to every quarantined record. `make check` now runs both lint and the compact audit summary.
