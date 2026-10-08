# Summary lineage redacted boundary

`summarylineage.py` sits after accepted handoff import.

It models redacted summary entries for:

```text
operator_local_summary
garden_witness_summary
public_redacted_summary
```

A summary lineage entry binds to the accepted import digest, handoff receipt digest, closure handoff digest, exact boundary, sequence, previous digest, family/path hints, and contradiction-carriage flag.

This is deliberately conservative: a summary line can be useful for operator handoff, garden witness memory, or public status reporting, but it must not smuggle raw scope/request/payload material or erase contradiction evidence.
