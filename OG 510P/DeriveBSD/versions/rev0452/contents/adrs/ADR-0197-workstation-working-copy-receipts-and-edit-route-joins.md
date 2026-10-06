# ADR-0197: Workstation working-copy receipts and edit-route joins

- Status: Accepted
- Date: 2026-03-20

## Context

`ADR-0195` already fixed the broad workstation file-open shape:
import first, route second, and keep document handling inside bounded `document_viewing` / `document_editing` roles.
`ADR-0196` then fixed the next mutation boundary:
foreign imported documents stay **view-first**, and editing them requires an explicit working-copy transition instead of saving back over the imported original by default.

That left one expensive ambiguity in the archive:
**what is the typed evidence object for that working-copy transition, and how does an allowed edit route prove it opened the working copy rather than the imported original?**

Without a typed answer, implementations will drift toward one of three bad shortcuts:

1. treat “make editable copy” as UI prose with no durable artifact,
2. hide working-copy creation inside the editor launch path,
3. or let edit routes prove only that *some* file was opened, not that the writable file came from an explicit copy transition.

## Decision

1. **The explicit authoring transition gets its own typed lane:**
   - `content.working-copy.plan`
   - `content.working-copy.receipt`

2. A working-copy plan binds the exact imported source through:
   - `source.import_receipt_digest`
   - `source.source_output_digest`

   This keeps the act attached to the exact imported artifact or inspection derivative that is becoming editable.

3. A working-copy receipt records the new writable artifact separately from the imported source and preserves the upstream provenance join through:
   - `source.import_receipt_digest`
   - `source.source_output_digest`
   - optional `source.authoritative_origin_digest`

4. `intent.route.receipt` grows optional `working_copy_receipt_digest`.
   For imported-document edit routes that are allowed onto `document_editing`, implementations should emit that digest so route evidence can prove which exact explicit working-copy act made the writable file exist.

5. `intent.request.context` grows optional:
   - `import_receipt_digest`
   - `working_copy_receipt_digest`

   This keeps policy/routing inputs explicit when the caller or trusted broker already knows the exact evidence objects involved.

6. The workstation baseline still does **not** auto-create a working copy as an invisible side effect of ordinary view/open.
   The copy transition is a distinct act with distinct evidence.

7. This ADR still does **not** introduce a giant document-management subsystem.
   It standardizes only the minimum artifact pair and route join needed to make **work on a copy** implementable and supportable.

## Consequences

Good:

- support/export surfaces can distinguish:
  - imported original inspected,
  - working copy issued,
  - editor route allowed,
  - and later mutations/export from that working copy,
- edit routes no longer need to rely on path folklore to prove they are not opening the foreign original,
- and profile **B** gets a concrete, implementable authoring path without weakening the view-first floor.

Trade-offs:

- there is one more narrow artifact family to implement,
- trusted brokers/routers need to thread one more digest when opening an editable copy,
- and implementations must decide where working copies physically live while still following this evidence shape.

## What this does not decide

Still open:

- collaborative/version-control semantics for working copies,
- exact viewer heuristics for disposable vs persistent `document_viewing`,
- exact profile-`C` compatibility adapters,
- and richer document/media/app taxonomies.

## Pointers

- `adrs/ADR-0195-workstation-file-open-import-join-and-bounded-document-roles.md`
- `adrs/ADR-0196-workstation-imported-foreign-documents-stay-view-first-and-working-copy-shaped.md`
- `docs/605-workstation-file-open-import-and-bounded-document-roles.md`
- `docs/606-workstation-imported-foreign-documents-stay-view-first.md`
- `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md`
- `spec/content.working-copy.plan.schema.json`
- `spec/content.working-copy.receipt.schema.json`
- `spec/intent.route.receipt.schema.json`
