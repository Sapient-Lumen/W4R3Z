# rev0045 helper timeout notes

During rev0045, the inherited multi-lane helper wrappers were attempted first. They successfully produced U-123 output but then timed out or were killed while orchestrating repeated failing pytest matrices. The individual tests themselves were fast when run directly.

Rev0045 therefore records manual per-packet source-refresh evidence using this smaller gate:

```text
current source + fixed regression: run with --maxfail=1 and require expected failure
selected temporary patch + fixed regression: run full fixed regression and require pass
```

This is why the clean source-refresh evidence is split across packet-specific files rather than relying only on the inherited wrappers.
