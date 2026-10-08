# Record delta protocol draft

When a reviewer changes a record, the change should not disappear into the file.

Future revisions should add a `record_deltas/` directory with entries containing:

- record_id
- reviewer role, not necessarily reviewer identity
- changed field
- previous wording
- new wording
- reason for change
- safety class
- whether downstream surfaces must be rolled back or re-rendered

This draft exists because rev0004 is large enough that review will become the next corpus substrate.
