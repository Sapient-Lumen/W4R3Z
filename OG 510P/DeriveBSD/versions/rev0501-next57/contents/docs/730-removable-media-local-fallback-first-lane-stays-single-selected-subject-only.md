# Removable-media local fallback first lane stays single-selected-subject only

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** reproducibility, operability  
**Patterns:** Broker→Lease→Receipt

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` already fixed the fallback boundary, `docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md` already fixed the host-mount→disposable-jail execution floor, `docs/725-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md` already fixed the finite admitted filesystem set, `docs/726-removable-media-local-fallback-mounted-trees-stay-inert-and-mount-hardening-is-fail-closed.md` already fixed inert mount posture, `docs/727-removable-media-local-fallback-ingest-walk-stays-physical-root-pinned-and-regular-files-plus-explicit-directories-only.md` already fixed the first member-kind floor, `docs/728-removable-media-local-fallback-member-paths-stay-relative-clean-nfc-and-collision-fail-closed.md` already fixed the portable member-path grammar, and `docs/729-removable-media-local-fallback-keeps-owner-mode-mtime-xattr-fidelity-out-of-the-first-lane.md` already fixed that reviewed/import identity stays path/kind/payload-first rather than filesystem-metadata-first.

This page closes the next smaller implementation seam:

> **the first removable-media local-ingest lane now stays single-selected-subject only; direct multi-member review/import returns as a later explicit lane.**

See also:
- ADR: `adrs/ADR-0320-removable-media-local-fallback-first-lane-stays-single-selected-subject-only.md`
- removable-media workflow: `docs/279-usb-quarantine-and-removable-media-workflow.md`
- removable-media posture by profile: `docs/458-removable-media-and-usb-posture-by-profile.md`
- current artifact family: `spec/content.import.plan.schema.json`, `spec/content.import.receipt.schema.json`
- richer reviewed-collection lane that already exists elsewhere in the archive: `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`

## Why this needs a hard decision

The first local-ingest lane now knows **which devices** it can touch, **which filesystems** it can admit, **how mounts must be hardened**, **which member kinds** it may walk, **which member-path grammar** is authoritative, and **which metadata does not belong to reviewed/import identity**.
But it still did not say whether the lane itself imports one selected subject or an arbitrary reviewed set of independent members.

That is expensive to leave open because the current artifact family is already subject-shaped:
- `content.import.plan` carries one authoritative `subject`
- `content.import.receipt` carries one authoritative `subject`
- `content.import.receipt.outputs[]` can already represent multiple materialized outputs, but only as a consequence of processing that one selected subject, not as proof that the human reviewed and selected an arbitrary finite set of independent inputs

If the archive does not choose a selection-width floor now, the first implementation will quietly reinvent collection semantics inside `content.import.*`: ordering, duplicate-path posture, selected-root overlap, ancestor closure, and reviewed-set identity will all drift in as hidden implementation behavior.

## Accepted cut

For the first host-local removable-media ingest lane:

- `content.import.plan` / `content.import.receipt` stay **single-selected-subject only**
- the authoritative reviewed/import identity is the one exact selected subject already named by the family
- the ingest worker may still walk directories beneath `/ingest` to classify or present candidates, but **direct multi-member review/import is out of scope in the first cut**
- recursive directory/tree import that would require reviewed collection semantics is **not part of this first lane**
- `content.import.receipt.outputs[]` may still contain multiple outputs when they are a deterministic consequence of processing **that one selected subject** (for example sanitize, unpack, or convert)
- any later removable-media lane that wants direct multi-member review/import must return as a **separate explicit RFC/ADR cut** instead of widening this first `content.import.*` lane

## Why this is the right first cut

### 1) It keeps the first implementation target real

The first local removable-media lane can now be built as:
classify candidates → select one subject → scan/sanitize/import that subject → emit one receipted import result.
That is boring enough to code without reopening a collection-transfer subsystem.

### 2) It keeps subject-shaped artifacts honest

The current `content.import.*` family already answers “what exact subject did we import?” well enough.
It does **not** yet answer “what exact reviewed finite set did we transfer?” in a portable, manifest-first way.
The archive should not pretend otherwise.

### 3) It keeps richer collection semantics explicit

The archive already has a richer reviewed finite-collection handoff queue elsewhere.
If removable-media workflows later need that level of selected-set authority, they should earn it as an explicit lane instead of stretching this first import path until it means two different things.

## What this still does not decide

This page does **not** forbid later richer removable-media workflows.
It does **not** forbid selecting a directory in a future explicit reviewed-collection lane.
It does **not** say archive extraction from one selected subject is forbidden.
It does **not** remove the already accepted path/kind/payload, inert-mount, and collision-fail-closed cuts.

Those remain distinct questions, but the archive no longer leaves the first local removable-media lane half-way between a single-subject import and a reviewed multi-member transfer protocol.

## Related docs

- `docs/278-device-grants-and-devfs-rulesets.md`
- `docs/279-usb-quarantine-and-removable-media-workflow.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/458-removable-media-and-usb-posture-by-profile.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`

Last updated: 2026-03-26r461
