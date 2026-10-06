# RFC-0108: Compiled service database and bundles

Status: Draft

## Problem

`rc.d` is a good executor but a weak *explanation surface*. Operators need a stable, diffable model of:

* service dependencies
* target states (“bundles”)
* what changed between generations

## Proposal

Derive a compiled service database artifact (`svcdb`) from the module/options layer.

* `svcdb` is bound into `plan_digest`.
* activation uses `rc.d` and service-jail lifecycle as the backend.

## Evidence

* `svcdb.digest`
* activation log references the bundle targets applied and their health gates

## References

See `docs/173-compiled-service-database-bundles.md`.
