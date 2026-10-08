# Auditmesh current fold refactor

`auditmesh.py` is an audit/refactor surface for rev0031. It does not replace the historical fold modules. It checks that the current revision has a visible path through:

- modules
- tests
- docs
- ADRs
- `VERSION`
- `REVISION_RECEIPT.json`
- `PUBLIC_SURFACE.json`
- `HEAD_REGISTRY.json`
- `NEXT_REVISION.json`
- active `surfaceledger.py`

It also preserves rev0030 `keycrisisfold` as a predecessor health check.

The design debt remains: many historical fold modules should eventually be collapsed behind a declarative map. rev0031 does not attempt that whole cleanup. It starts by making the current path auditable from one new surface.
