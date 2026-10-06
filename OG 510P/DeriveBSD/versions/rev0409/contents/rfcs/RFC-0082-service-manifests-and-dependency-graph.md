# RFC-0082: Service manifests and dependency graphs

Status: Draft

## Summary

Derive an explicit **service graph manifest** from the Plan for host systems and workloads.
Activation backends (rc.d/service-jails/others) consume this manifest.

Inspirational reference: illumos SMF’s first-class service objects and dependency model. https://smartos.org/man/7/smf

## Goals

- Make service dependencies reviewable and diffable.
- Improve `derive explain` and `derive diff --blast-radius`.
- Avoid inventing a full SMF clone.

## Design sketch

- New structured output: `service.graph`.
- Contains:
  - service instances
  - dependencies
  - placement (host/jail/microVM)
  - required resources (pf anchors, rctl profile, mounts)

See: `docs/114-service-manifests-smf-lessons.md`.


## Relationship to `svcdb` + health evidence

RFC-0082 introduced the idea of a derived service graph manifest.
This has now been concretized as:

- `svcdb` (compiled service database; derived from the Plan)
- `svc.snapshot` and `svc.event` (runtime health evidence)

See: `docs/214-service-supervision-health-as-evidence.md` and RFC-0149.
