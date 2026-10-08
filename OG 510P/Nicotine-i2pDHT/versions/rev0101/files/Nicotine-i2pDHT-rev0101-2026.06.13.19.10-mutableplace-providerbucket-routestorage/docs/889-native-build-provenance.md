# Native build provenance

`nativeprovenance.py` treats native builds as exact-boundary evidence.

A build stamp binds:

```text
source audit report
sanitizer report
native budget report
source digest
compiler flags digest
object digest
artifact digest
compiler id/version
builder family
path family
sequence / previous digest
```

It accepts only reproducible-looking, source-audited, sanitizer-budgeted leaf artifacts with enough builder/path diversity. It rejects source drift, flag drift, object drift, unsupported compilers, replay/rollback, same-sequence forks, previous-link mismatch, and single-builder-only evidence.
