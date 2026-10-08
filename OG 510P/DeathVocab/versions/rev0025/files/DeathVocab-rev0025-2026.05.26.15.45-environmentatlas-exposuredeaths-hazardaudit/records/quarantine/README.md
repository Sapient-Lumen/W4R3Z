# Quarantined records

All records in this directory are internal construction records. They are not public corpus pages.

As of rev0007 there are 62 quarantined public-source pilot records:

- `DV-REC-000001` through `DV-REC-000016`: threshold / signs / first-room-after-death pilots.
- `DV-REC-000017` through `DV-REC-000028`: practice-layer care-move pilots.
- `DV-REC-000029` through `DV-REC-000044`: utterance and listening-layer pilots.
- `DV-REC-000045` through `DV-REC-000062`: decision-language, code-status, ICU, organ-donation, MAID/VSED, and institution-gate pilots.

Public record count remains zero. Every record requires review before rendering.


## Rev0014 final audit note
The final audit packaging pass reconciled reader-router alias IDs to the canonical DV-SA namespace and added `publication_review_state: blocked` to every quarantined record. `make check` now runs both lint and the compact audit summary.
