# ADR-0286: Workstation finite collection handoff keeps owner/mode/mtime/xattr fidelity out of this lane

Date: 2026-03-23  
Status: Accepted

## Context

`ADR-0269` fixed the first reviewed finite-collection manifest floor as content-identity-first and stat-light.
`ADR-0280` then fixed advisory MIME as optional descriptive metadata and non-authoritative.
Recent cuts around exact fresh-root receipts and opaque result-root handles narrowed retrieve and local locator posture further.

One portability loophole still remained in `RFC-0194`:
**should this same lane ever standardize owner/group, mode bits, mtimes, xattrs, ACLs, or other richer filesystem metadata fidelity?**

Leaving that as a standing maybe keeps the lane deceptively small on paper while inviting implementations to smuggle host-specific archive/preservation semantics back in under “better fidelity” wording. That would widen the contract from reviewed selected-set handoff toward filesystem-preserving archive semantics, with cross-filesystem normalization and support complexity that the first lane does not need.

## Decision

For the reviewed finite collection handoff lane described by `RFC-0194`:

1. owner/group fidelity is **out of this lane entirely**.
2. mode-bit fidelity is **out of this lane entirely**.
3. mtime / last-modified fidelity is **out of this lane entirely**.
4. xattr / ACL / capability / other extended filesystem-metadata fidelity is **out of this lane entirely**.
5. the authoritative reviewed contract remains path/kind/payload-first plus the already accepted exact created fresh-root receipt and receiver-local opaque result-root handle.
6. retrieve/materialization may still apply receiver-local defaults or policy-controlled local metadata, but those values are **receiver-local realization detail**, not portable reviewed state and not detached evidence authority for the handoff itself.
7. any future lane that wants filesystem-metadata preservation must return as a **separate explicit RFC/ADR cut**, not as a widening of this lane.

## Consequences

- The first richer lane stays implementable across B/C/D without turning into a filesystem-preservation subsystem.
- Detached review/export/support can keep asking the boring portable questions first: which reviewed paths, which member kinds, which exact file bytes, and which exact fresh root was created locally.
- Implementations stay free to choose local materialization defaults without pretending those local owner/mode/time/xattr outcomes were sender-reviewed portable state.

## Alternatives considered

- **Standardize owner/mode/mtime/xattr fidelity later inside this same lane:** rejected because it would quietly transform the selected-set handoff contract into a filesystem-preserving archive format with much higher cross-platform normalization burden.
- **Keep metadata posture permanently open as an RFC footnote:** rejected because it leaves a large implementation fork point in the first lane even after the archive already narrowed most other reviewed-state seams.
- **Make local materialized metadata authoritative after retrieve:** rejected because it would promote receiver-local realization policy into portable reviewed truth.

## Related

- `adrs/ADR-0269-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md`
- `adrs/ADR-0280-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md`
- `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md`
- `docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md`
- `docs/696-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
