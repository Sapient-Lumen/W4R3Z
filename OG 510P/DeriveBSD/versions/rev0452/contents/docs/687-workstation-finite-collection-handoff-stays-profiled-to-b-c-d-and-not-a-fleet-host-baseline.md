# Workstation finite collection handoff stays profiled to B/C/D and not a fleet-host baseline

**Tier:** C (RFC shaping cut)  
**Profiles:** B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote

`docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` already fixed the first richer workstation transfer queue, and `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` through `docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md` already narrowed the first cut into a concrete reviewed finite-collection handoff. `docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md` now sharpens the first shipped UX one notch further without widening the profile scope: B/C/D keep the richer lane, while A still stays out.

This doc makes the next small but hard decision inside that RFC queue explicit:
**the first reviewed finite-collection handoff family stays supported for B/C/D only, and it does not become a fleet-host (A) baseline just because operators could imagine using it there.**

See also:
- ADR: `adrs/ADR-0277-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md`
- Draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- queue head: `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- retrieve/materialization cut: `docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`

## Why this needs a hard decision

The queue docs already carry `**Profiles:** B, C, D`, but the RFC still left one last ambiguity open: should A also count under “explicit operator posture” simply because a fleet host might sometimes need files moved around?

Leaving that implicit is dangerous.
It encourages exactly the kind of cross-shape drift the archive is trying to prevent:

- **A / fleet_host** starts treating a human-reviewed finite file handoff as a normal host-admin primitive, even though its baseline answers should stay rollout, support-bundle, import/export, or breakglass shaped.
- **B / workstation** and **C / general_os** lose the clarity that this richer lane exists because real human-facing file-handoff pressure exists there.
- **D / appliance_factory** risks turning a bounded factory/maintenance/review lane into ambient production-image convenience.

The narrower answer is more coherent:
**keep one archive, keep one richer lane family, but make the product-scope boundary explicit instead of pretending every profile wants the same ergonomics.**

## Accepted cut

For the first reviewed finite-collection handoff family:

- the supported profile scope is **B/C/D**
- **A / fleet_host** does **not** treat this lane as a baseline supported workflow
- when **D / appliance_factory** uses this lane, it belongs to explicit factory, maintenance, approval, or quarantined ingest/export stations and workflows rather than unattended production-image runtime convenience
- when **A / fleet_host** needs bytes in or out, the baseline answers remain artifacted rollout/import/export/support/breakglass lanes instead of widening this reviewed finite-collection handoff family
- if fleet-host operations later prove they need a richer host-local file-ferry surface, that must return as a **distinct later RFC/ADR lane** with its own artifact family and operator semantics instead of piggybacking on this family

That keeps the richer handoff real where it solves an actual problem while refusing to let “all product shapes without forks” collapse into “every lane belongs everywhere.”

## Why this is the right cut

### 1) It keeps fleet-host operations on artifacted lanes

A should prefer rollout artifacts, support bundles, explicit imports/exports, and breakglass/operator ceremonies over ad-hoc reviewed file ferrying on hosts. That keeps host operations explainable and avoids creating a shadow workstation UX on production fleet nodes.

### 2) It preserves the real ergonomic value for B/C/D

B and C have genuine human file-handoff pressure. D can also have it, but in bounded factory/review/maintenance stations rather than as ambient production runtime behavior. The archive should preserve that useful pressure instead of diluting it into a universal admin primitive.

### 3) It keeps “no forks” honest without making profiles meaningless

Profiles exist so one archive can compile to different defaults and supported lanes. Saying “A is out of scope for this richer lane” is not a fork; it is the point of having profiles.

## What this still does not decide

The accepted first richer-family stack is now fixed in `docs/698-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md` as `ui.collection.handoff.grant` / `ui.collection.handoff.manifest` / `ui.collection.handoff.receipt`.
It does **not** decide the exact trusted-UI support-level wording for B/C/D implementations.
It does **not** decide whether some future A-specific operator file ferry is worth standardizing.
It does **not** widen D's production-image runtime posture.

Those remain follow-on questions, but the archive no longer leaves the first richer finite-collection handoff profile scope ambiguous.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- `docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md`

Last updated: 2026-03-23r428
For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
