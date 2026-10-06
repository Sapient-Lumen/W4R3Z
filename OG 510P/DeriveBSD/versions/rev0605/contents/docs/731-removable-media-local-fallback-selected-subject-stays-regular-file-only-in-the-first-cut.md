# Removable-media local fallback selected subject stays regular-file only in the first cut

**Tier:** B (Implementation-shaping cut)  
**Profiles:** B, C  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt

`docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` through `docs/730-removable-media-local-fallback-first-lane-stays-single-selected-subject-only.md` already made the first host-local removable-media fallback finite enough to build: storage-only, session-scoped, quarantine-first, host-controlled read-only mount, disposable no-network jail, finite `fstyp`-admitted filesystems, inert mounted trees, physical root-pinned walk, one portable member-path grammar, path/kind/payload-first reviewed/import identity, and a single-selected-subject import lane instead of direct multi-member reviewed transfer.

This page closes the next smaller implementation seam:

> **the first removable-media local-ingest lane may present directories while browsing `/ingest`, but the selected import subject itself stays regular-file-only in the first cut.**

See also:
- ADR: `adrs/ADR-0321-removable-media-local-fallback-selected-subject-stays-regular-file-only-in-the-first-cut.md`
- previous cut: `docs/730-removable-media-local-fallback-first-lane-stays-single-selected-subject-only.md`
- removable-media workflow: `docs/279-usb-quarantine-and-removable-media-workflow.md`
- current artifact family: `spec/content.import.plan.schema.json`, `spec/content.import.receipt.schema.json`
- richer directory/tree lane that already exists elsewhere in the archive: `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`

## Why this needs a hard decision

The first local-ingest lane now knows how to attach, mount, walk, normalize, and receipt removable-media inputs.
But `ADR-0320` only fixed **selection width**, not **selected-subject kind**.
Without one more cut, implementations can still disagree about whether “pick one thing from the tree” means:

- pick one regular file,
- pick one directory and recurse,
- or treat a directory as a stealth reviewed collection under a subject-shaped receipt family.

That is too much ambiguity for a lane that is supposed to become boring enough to code.
A selected directory is not a small regular file.
It immediately reopens reviewed collection identity, ancestor closure, overlap, ordering, and result-root semantics.
Those questions already have a better home in the archive’s richer reviewed finite-collection handoff work.

FreeBSD’s own surface supports keeping the split explicit:
- `file(1)` is useful for classifying one file and can emit MIME/type strings without turning a browsed directory into the authority object.
- `bsdtar(1)` documents real extraction security hazards around pathnames, `..`, absolute paths, and symlink-altered target directories, which is a good reminder that tree/archive semantics are their own lane and should not sneak in under first-cut subject selection.

## Accepted cut

For the first host-local removable-media ingest lane:

- the selected subject stays **regular-file-only in the first cut**
- directories beneath `/ingest` may still appear in candidate browsing or classification views, but **directories are not selectable import subjects in this lane**
- archive/container handling that remains allowed here is still derived processing of **one selected regular file**, not directory-subject import and not reviewed-collection import
- any later removable-media lane that wants directory/tree subject selection must return as a **separate explicit RFC/ADR cut** instead of widening this first `content.import.*` path

## Why this is the right first cut

### 1) It keeps the implementation target boring enough to ship

The first host-local fallback can now be implemented as:
classify candidates → choose one regular file → scan/sanitize/import it → receipt it.
That is dramatically easier to reason about than half-introducing directory/tree semantics.

### 2) It keeps subject-shaped artifacts honest

The current `content.import.*` family already answers “which exact subject did we import?” reasonably well for one file.
It does **not** yet answer “which exact reviewed tree did we import?” in a manifest-first way.
The archive should not pretend otherwise.

### 3) It keeps richer tree semantics explicit

The archive already has a better conceptual home for reviewed finite collections.
If removable-media workflows later need directory/tree selection, they should earn that lane explicitly instead of stretching this first import path until it means two different things.

## What this still does not decide

This page does **not** ban directory browsing during candidate discovery.
It does **not** ban archive/container processing when the selected subject is one regular file.
It does **not** decide the future richer removable-media directory/tree lane.
It does **not** widen the current receipt family into reviewed collection identity.

Those remain distinct questions, but the archive no longer leaves this first removable-media lane half-way between single-file import and reviewed tree transfer.

## Related docs

- `docs/278-device-grants-and-devfs-rulesets.md`
- `docs/279-usb-quarantine-and-removable-media-workflow.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/458-removable-media-and-usb-posture-by-profile.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `docs/730-removable-media-local-fallback-first-lane-stays-single-selected-subject-only.md`

Last updated: 2026-03-26r462
