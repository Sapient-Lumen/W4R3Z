# RFC-0172: Dynamic service identities (ephemeral UIDs/GIDs) as a first-class pattern

Status: Draft  
Last updated: 2026-02-25

## Problem

DeriveBSD wants least-privilege defaults, but “create and manage a system user”
is an ecosystem tax that pushes deployments toward running services as root.

Static identities also accumulate over time and make state ownership ambiguous.

## Goals

- Make “run unprivileged” easy enough to be the default.
- Treat service identity as a **lease** controlled by the restarter.
- Make identity decisions visible in evidence (`svc.event`, `svc.snapshot`, incident bundles).
- Keep compartments (jails/microVMs) as the preferred isolation mechanism.

## Non-goals

- Designing a complete user database replacement.
- Guaranteeing stable UID assignment across all time (that can be a policy choice).

## Proposal

### 1) Add `identity` to `svcdb` service definitions

Add an optional block:

- `identity.mode`: `inherit` | `static` | `dynamic`
- `identity.user` / `identity.group` for `static`
- `identity.dynamic` options (reserved uid range, cleanup policy, state dirs)

This is a declaration only; the restarter enforces it.

### 2) Minimal evidence surface (day-0)

- restarter SHOULD record effective `uid/gid` in `svc.event.meta` on `state-transition` into `online`
- `svc.snapshot` MAY include `meta.uid` / `meta.gid` for each service entry

### 3) Future evolution (not required now)

Introduce typed objects:
- `identity.lease.receipt`
- `identity.release.event`

…and make them part of the evidence spine.

## Schema changes

- Update `spec/svcdb.schema.json` to include `identity`.
- Update `spec/examples/svcdb.json` to show one host service using `identity.mode="dynamic"`.

## Risks / tradeoffs

- UID reuse can cause confusing ownership if state persistence isn’t explicit.
- Some services assume stable usernames; guidance should recommend using compartments in those cases.

## Related

- `docs/240-dynamic-service-identities.md`
- `docs/214-service-supervision-health-as-evidence.md`
- `docs/232-service-promise-profiles.md`
- `docs/238-portal-activated-services-and-socket-activation.md`
