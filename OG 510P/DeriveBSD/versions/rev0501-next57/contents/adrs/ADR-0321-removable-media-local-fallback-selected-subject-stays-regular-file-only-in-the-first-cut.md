# ADR-0321: Removable-media local fallback selected subject stays regular-file only in the first cut

Date: 2026-03-26  
Status: Accepted

## Context

`ADR-0313` through `ADR-0320` already made the first honest host-local removable-media fallback for imperfect B/C hardware finite enough to implement:

- storage-only, session-scoped, quarantine-first,
- host-controlled `fstyp` admission and read-only mount,
- disposable no-network jail,
- inert mounted trees,
- physical root-pinned walk,
- one portable member-path grammar,
- path/kind/payload-first reviewed/import identity,
- and a single-selected-subject import lane rather than direct multi-member reviewed transfer.

One more ambiguity still leaked collection semantics back in through the side door:
**may the selected subject itself be a directory/tree, or does the first lane stay regular-file-only?**

Leaving that open is expensive because a selected directory is not a smaller version of a selected file.
It immediately reopens exactly the collection questions `ADR-0320` just avoided:
reviewed-set identity, ancestor closure, overlap posture, ordering, and result-root semantics.
A directory-shaped subject would also blur the boundary between “walk a mounted tree to present candidates” and “import a reviewed collection”.

FreeBSD’s own substrate reinforces the split.
`file(1)` is a regular-file classifier with MIME/type output and no-dereference posture available, while `bsdtar(1)` spends real security text on why archive/tree extraction has separate pathname and overwrite hazards.
That is a good reminder that “candidate discovery in a tree” and “reviewed import subject semantics” should not collapse into one casual first-cut rule.

## Decision

For the first host-local removable-media ingest fallback described by `ADR-0313` through `ADR-0320`:

1. The selected subject stays **regular-file-only in the first cut**.
2. Directories beneath `/ingest` may still be walked and shown as navigation/classification aids, but **directories are not selectable import subjects in this lane**.
3. Any archive/container handling that remains allowed in this lane is still derived processing of **one selected regular file**, not directory-subject or reviewed-collection import.
4. Any later removable-media lane that wants directory/tree subject selection must return as a **separate explicit RFC/ADR cut** instead of widening this first `content.import.*` path.

## Consequences

- The first removable-media fallback now has a more honest coding target: enumerate candidates, select one regular file, classify/scan/sanitize/import it, receipt it, detach.
- Directory browsing remains useful for human review without silently making directory trees part of the import subject contract.
- The richer reviewed finite-collection lane remains the right place for future directory/tree semantics.

## Alternatives considered

- **Allow directory subjects in the same first lane:** rejected because it silently reopens reviewed-collection semantics under a subject-shaped artifact family.
- **Auto-wrap selected directories into an implicit archive/manifest subject:** rejected because it hides a widening transform inside what should stay explicit reviewed/import authority.
- **Leave selected-subject kind unspecified until coding:** rejected because implementation detail would become the real contract.

## Related

- `adrs/ADR-0313-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md`
- `adrs/ADR-0314-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md`
- `adrs/ADR-0315-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md`
- `adrs/ADR-0316-removable-media-local-fallback-mounted-trees-stay-inert-and-mount-hardening-is-fail-closed.md`
- `adrs/ADR-0317-removable-media-local-fallback-ingest-walk-stays-physical-root-pinned-and-regular-files-plus-explicit-directories-only.md`
- `adrs/ADR-0318-removable-media-local-fallback-member-paths-stay-relative-clean-nfc-and-collision-fail-closed.md`
- `adrs/ADR-0319-removable-media-local-fallback-keeps-owner-mode-mtime-xattr-fidelity-out-of-the-first-lane.md`
- `adrs/ADR-0320-removable-media-local-fallback-first-lane-stays-single-selected-subject-only.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `docs/731-removable-media-local-fallback-selected-subject-stays-regular-file-only-in-the-first-cut.md`
