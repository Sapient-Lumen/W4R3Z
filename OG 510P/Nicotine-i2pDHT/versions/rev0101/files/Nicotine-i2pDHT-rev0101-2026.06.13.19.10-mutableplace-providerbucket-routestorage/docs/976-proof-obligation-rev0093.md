# Proof obligation rev0093

rev0093 must show:

```text
native load loopback does not allow load or dispatch
native call canary records Python result only
native dispatch fence refuses native side effects
predecessor rev0092 fold still passes
native fold spine includes rev0093
surface/fold/audit metadata points to the current revision
```

Local verification uses targeted tests, chunked pytest when needed, compile checks, cube audit, fold map, fold registry, native fold-spine audit, and zip integrity checks.
