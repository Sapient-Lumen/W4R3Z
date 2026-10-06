# ADR-0199: Workstation working-copy reintegration stays explicit and new-version-shaped

Date: 2026-03-20  
Status: Accepted

## Context

`ADR-0195` fixed the imported-document open floor:
import first, route second, and keep ordinary handling inside bounded `document_viewing` / `document_editing` roles.
`ADR-0196` then fixed the mutation floor:
foreign imported documents stay **view-first**, and editing them requires an explicit working-copy transition instead of editing the imported original in place.
`ADR-0197` made that copy act typed as `content.working-copy.plan` / `content.working-copy.receipt` and made allow-path edit routes prove they opened the working copy via `working_copy_receipt_digest`.
`ADR-0198` then fixed local save scope:
ordinary save stays on the working-copy output, and source write-back is a separate explicit act rather than an editor side effect.

That leaves the next expensive ambiguity:
**once a working-copy output exists and has local edits, what is the first official act that says “these bytes are now a candidate successor of an authoritative origin” without quietly replacing the source or inventing a giant document-management subsystem?**

If the archive leaves that undefined, implementations drift back toward folklore:

1. “Save As” becomes a fake source-update lane.
2. random app/cloud adapters decide whether replacement is in-place, versioned, or duplicated.
3. support/export surfaces can no longer distinguish “local edited derivative” from “candidate successor intended for source lineage.”
4. profile `D` loses a clean evidence boundary for regulated authoring/revision control.

## Decision

1. The first official reintegration act for the imported-document authoring lane is now a narrow typed lane:
   - `content.reintegrate.plan`
   - `content.reintegrate.receipt`

2. This lane does **not** finalize a remote/document-system update by itself.
   It creates a typed **local successor candidate** that binds:
   - the exact `content.working-copy.receipt`,
   - the exact working-copy output digest,
   - the exact `content.import.receipt`,
   - and the authoritative origin digest the candidate claims to succeed.

3. The v0 reintegration boundary is intentionally strict:
   - `candidate_posture = local-successor-candidate`
   - `replace_in_place = forbidden`
   - `upstream_finalize = separate-adapter-required`

4. The v0 reintegration target is intentionally narrow too:
   - `target.scope = same-authoritative-origin`
   - `target.action = register-successor-candidate`

5. Therefore, ordinary workstation authoring now tells one explicit story:
   - import foreign bytes,
   - view first,
   - issue a working copy,
   - save locally onto that working-copy output,
   - and, only if needed, explicitly register those bytes as a **successor candidate** of a known authoritative origin.

6. Any later act that actually pushes the candidate into a remote DMS, ticketing system, VCS, content store, or collaboration service remains a **later adapter/finalization boundary**.
   That later act may export, publish, check in, or upload a new version, but it must not erase the explicit reintegration boundary.

## Consequences

### Positive

- Imported evidence, local authoring, and source-lineage intent are now three distinct steps rather than one blurred editor workflow.
- Profile `B` gets a coherent boring implementation target for “I edited the working copy and now want this to count as the next version.”
- Profile `D` gets a cleaner revision-control/evidence story without requiring one blessed remote document system.
- Profile `C` can still add compatibility adapters later, but the official Derive-managed lane stays audit-friendly.
- Future export/publish/check-in adapters now have a stable typed join instead of inferring intent from app behavior.

### Trade-offs

- Some user-visible flows will require one more explicit step than mainstream disposable/save-back systems.
- The official lane refuses to treat unknown/ambient file paths as authoritative origins worth “updating.”
- A later ADR still needs to define which adapter/finalization lanes deserve first-class support.

## Not decided here

This ADR does **not** decide:

- remote API/protocol details for DMS/VCS/cloud check-in,
- collaborative locking/check-out semantics,
- review/approval rules for accepting or promoting successor candidates,
- or whether profile `C` gets a looser convenience adapter beyond the official lane.

## Related

- `adrs/ADR-0195-workstation-file-open-import-join-and-bounded-document-roles.md`
- `adrs/ADR-0196-workstation-imported-foreign-documents-stay-view-first-and-working-copy-shaped.md`
- `adrs/ADR-0197-workstation-working-copy-receipts-and-edit-route-joins.md`
- `adrs/ADR-0198-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md`
- `docs/605-workstation-file-open-import-and-bounded-document-roles.md`
- `docs/606-workstation-imported-foreign-documents-stay-view-first.md`
- `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md`
- `docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md`
- `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md`
- `spec/content.reintegrate.plan.schema.json`
- `spec/content.reintegrate.receipt.schema.json`
