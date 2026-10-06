# ADR-0320: Removable-media local fallback first lane stays single-selected-subject only

Date: 2026-03-26  
Status: Accepted

## Context

`ADR-0313` through `ADR-0319` already fixed the first honest host-local removable-media fallback for imperfect B/C hardware:

- storage-only, session-scoped, quarantine-first,
- host-controlled `fstyp` admission and read-only mount,
- disposable no-network jail,
- inert mounted trees,
- physical root-pinned walk,
- one portable member-path grammar,
- and path/kind/payload-first reviewed/import identity with filesystem-metadata fidelity out of scope.

One more expensive ambiguity remained:
**is this first lane a single selected-subject import lane, or is it quietly a multi-member reviewed transfer lane?**

Leaving that open is costly because the current artifact family already leans hard in one direction:

- `content.import.plan` carries one authoritative `subject`.
- `content.import.receipt` also carries one authoritative `subject`.
- `content.import.receipt.outputs[]` can already represent multiple materialized outputs, but only as the consequence of processing that one selected subject (for example archive extraction or document sanitization); multiple outputs arise only as the deterministic consequence of processing that one selected subject, not as proof that the human reviewed and selected an arbitrary finite set of independent input members.

If the archive leaves selection width vague here, the first implementation will quietly reinvent collection semantics inside `content.import.*`:
ordering, duplicate-path posture, selected-root overlap, ancestor closure, and reviewed-set identity will all reappear as hidden implementation folklore.
That is exactly the kind of widening that should arrive only as a separate explicit richer lane.

## Decision

For the first host-local removable-media ingest fallback described by `ADR-0313` through `ADR-0319`:

1. `content.import.plan` / `content.import.receipt` stay **single-selected-subject only** in this lane.
2. The authoritative import identity is the one selected subject already named by the artifact family, not an implicit reviewed collection.
3. The ingest worker may still walk directories beneath `/ingest` to classify or present candidates, but **direct multi-member review/import is out of scope in the first cut**.
4. Recursive directory/tree import that would require reviewed collection semantics is **not part of this first lane**.
5. `content.import.receipt.outputs[]` may still contain multiple outputs when they are the deterministic consequence of processing **that one selected subject** (for example sanitize, unpack, or convert), but those outputs do **not** retroactively widen the lane into multi-subject review/import.
6. Any later removable-media lane that wants direct multi-member reviewed import must return as a **separate explicit RFC/ADR cut** instead of widening this first `content.import.*` path.

## Consequences

- The first removable-media fallback now has a realistic first implementation target: pick one subject, classify/scan/sanitize/import it, receipt it, detach.
- B/C do not accidentally inherit a half-designed collection-transfer subsystem under the name of “import from USB”.
- Directory walking remains useful for candidate discovery without forcing the archive to settle collection-manifest semantics inside the wrong family.

## Alternatives considered

- **Allow direct multi-member review/import inside the same first lane:** rejected because it silently reopens collection identity, manifest ordering, selected-root overlap, and receipt semantics under `content.import.*`.
- **Auto-wrap reviewed trees into an implicit archive subject:** rejected because it hides a lossy/widening transform inside what should stay explicit reviewed/import authority.
- **Leave selection width unspecified until coding:** rejected because the current artifact family is already subject-shaped enough that implementation detail would become the real contract.

## Related

- `adrs/ADR-0313-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md`
- `adrs/ADR-0314-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md`
- `adrs/ADR-0315-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md`
- `adrs/ADR-0316-removable-media-local-fallback-mounted-trees-stay-inert-and-mount-hardening-is-fail-closed.md`
- `adrs/ADR-0317-removable-media-local-fallback-ingest-walk-stays-physical-root-pinned-and-regular-files-plus-explicit-directories-only.md`
- `adrs/ADR-0318-removable-media-local-fallback-member-paths-stay-relative-clean-nfc-and-collision-fail-closed.md`
- `adrs/ADR-0319-removable-media-local-fallback-keeps-owner-mode-mtime-xattr-fidelity-out-of-the-first-lane.md`
- `docs/279-usb-quarantine-and-removable-media-workflow.md`
- `docs/730-removable-media-local-fallback-first-lane-stays-single-selected-subject-only.md`
- `spec/content.import.plan.schema.json`
- `spec/content.import.receipt.schema.json`
