# Surface-clean active pointer audit

The cube preserves historical docs for wake-from-amnesia. That does not mean active metadata should keep pointing at the previous head. `surfaceclean.py` audits a bounded active set: current revision fields, active source imports, and the historical supersession map.

The rev0019 audit checks:

```text
VERSION matches current revision
PUBLIC_SURFACE / CLAIM_SURFACE / NEXT_REVISION / REVISION_RECEIPT match current revision
active source modules do not import deprecated providerpoison by name
historical supersession still records providerpoison -> provider_poison migration context
```

The audit intentionally allows historical tests to keep pinning legacy behavior. History can remain history; live entry points should be current.
